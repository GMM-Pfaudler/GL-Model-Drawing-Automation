from pywinauto import Application
import win32com.client
import win32gui
import math
import time
import os
import logging
from datetime import datetime


# Add temperature and pressure in fittings

# Configure logging with date-wise file logging
LOG_DIR = r"D:\GL\logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Prevent duplicate handlers if module is reloaded
if not logger.handlers:
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    console_handler.setFormatter(console_format)

    # File handler with date-based filename
    log_filename = os.path.join(LOG_DIR, f"generation_{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s [%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s')
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info(f"Logging initialized. Log file: {log_filename}")

# =============================================================================
# CONSTANTS
# =============================================================================

# Constraint type codes (Inventor API)
MATE_CONSTRAINT_INFERENCE_1 = 24833
MATE_CONSTRAINT_INFERENCE_2 = 24833
FLUSH_CONSTRAINT_TYPE = 115459

# Dimension constraint direction types
DIM_CONSTRAINT_HORIZONTAL = 19201
DIM_CONSTRAINT_VERTICAL = 19202
DIM_CONSTRAINT_ALIGNED = 19203

# Nozzle angles (degrees) - DEPRECATED: Use dynamic angles from item.get('nozzle_degree')
# These constants are kept for backward compatibility when nozzle_degree is not provided
NOZZLE_N16_ANGLE = -28      # First jacket nozzle (shell top)
NOZZLE_N15_ANGLE = -135     # Second jacket nozzle (shell top)
NOZZLE_N11_ANGLE = -90      # Third jacket nozzle (bottom)
NOZZLE_N17_ANGLE = -270     # Fourth jacket nozzle (bottom)


# Work plane/axis names
AXIS_Y = "Y Axis"
AXIS_X = "X Axis"
AXIS_Z = "Z Axis"
PLANE_XY = "XY Plane"
PLANE_XZ = "XZ Plane"
PLANE_YZ = "YZ Plane"

# Circular pattern counts
SIDE_BRACKET_COUNT = 4
SIDE_BRACKET_ANGLE = 90.0

# Common dimensions (mm)
DEFAULT_SKETCH_WIDTH = 10.0
DEFAULT_SKETCH_HEIGHT = 5.0
NOZZLE_DISTANCE_FROM_PLANE = 2350  # mm
NOZZLE_SKETCH_WIDTH = 5000  # mm



# Fitting type configurations
FITTING_CONFIG = {
    "split_flange": {
        "proxies": ["Y Axis", "XY PLANE"],
        "constraints": ["mate", "flush", "flush"],
        "stores_state": True,
    },
    "gasket": {
        "proxies": ["Y Axis", "XY PLANE", "XZ PLANE"],
        "offset": 2.2,
    },
    "blind_cover": {
        "proxies": ["Y Axis", "XY PLANE", "XZ PLANE"],
        "bolt_offset": -1.8,
    },
    "baffle": {
        "proxies": ["Y Axis", "XY PLANE", "XZ PLANE"],
        "bolt_offset": -2.8,
    },
    "toughened_glass": {
        "proxies": ["Y Axis", "XY PLANE", "XZ PLANE"],
        "bolt_offset": 0,
    },
    "sight_light_glass_flange": {
        "proxies": ["Y Axis", "XY PLANE", "XZ PLANE", "ASSEMBLY PLANE"],
        "bolt_offset": 0,
    },
    "bolt_stud": {
        "is_fastener": True,
        "creates_pattern": False,
    },
    "washer": {
        "is_fastener": True,
        "creates_pattern": False,
    },
    "nut": {
        "is_fastener": True,
        "creates_pattern": True,  # Last fastener triggers circular pattern
    },
}

# Component handler registry - maps patterns to handler methods
COMPONENT_HANDLERS = {
    "core": {
        "patterns": ["monoblock", "jacket", "diaphragmring", "sidebracket", "earthing"],
        "handler": "_handle_core_component",
    },
    "jacket_nozzle": {
        "patterns": ["jacketnozzle_n16_shell", "jacketnozzle_n17_btm"],
        "handler": "_handle_jacket_nozzle",
    },
    "airvent": {
        "patterns": ["airvent_coupling"],
        "handler": "_handle_airvent_coupling",
    },
    "manhole": {
        "patterns": ["nozzle_500_0_gasket", "nozzle_500_0_manhole", "nozzle_500_0_toughened", "nozzle_500_0_sight", "nozzle_500_0_washer", "nozzle_500_0_bolt"],
        "handler": "_handle_manhole_component",
    },
    "manhole_accessory": {
        "patterns": ["mhcclamp", "springbalanceassembly"],
        "handler": "_handle_manhole_accessory",
    },
    "coc": {
        "patterns": ["coc_gasket", "coc", "bfcclamp"],
        "handler": "_handle_coc_component",
    },
    "center_nozzle": {
        "patterns": ["nozzle_200_d_gasket", "nozzle_200_d_"],
        "handler": "_handle_center_nozzle",
    },
    "drive": {
        "patterns": ["driveassembly", "shaftclosure", "agitator", "mechanical_seal", "sensor"],
        "handler": "_handle_drive_component",
    },
    "nameplate": {
        "patterns": ["nameplatebracket"],
        "handler": "_handle_nameplate",
    },
}


class Inventor:
    """
    Autodesk Inventor COM automation wrapper for 3D assembly generation.

    Supports context manager protocol for proper resource management:
        with Inventor() as inventor:
            inventor.generate(components, model_details)

    Or traditional usage with explicit cleanup:
        inventor = Inventor()
        try:
            inventor.connect()
            inventor.generate(components, model_details)
        finally:
            inventor.disconnect()
    """

    def __init__(self):
        """Initialize the Inventor wrapper with empty state."""
        self._occurrence_cache = {}
        self._used_nozzle_planes = []  # Track used work planes for nozzles
        self._nozzle_state = {}  # Track nozzle geometry across components (keyed by '{size}_{degree}', e.g. '150_60')
        self.inv_app = None
        self.tg = None
        self.main_assy_doc = None
        self.main_assy_def = None
        self._is_connected = False

    # =========================================================================
    # COM LIFECYCLE MANAGEMENT
    # =========================================================================

    def __enter__(self):
        """Context manager entry - connect to Inventor."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.disconnect()
        # Don't suppress exceptions
        return False

    def connect(self):
        """
        Connect to Inventor application.

        Creates or gets existing Inventor instance and initializes TransientGeometry.
        """
        if self._is_connected:
            logger.debug("Already connected to Inventor")
            return

        try:
            # Try to connect to existing Inventor instance first
            try:
                self.inv_app = win32com.client.GetActiveObject("Inventor.Application")
                logger.info("Connected to existing Inventor instance")
            except Exception:
                # No existing instance, create new one
                self.inv_app = win32com.client.Dispatch("Inventor.Application")
                logger.info("Created new Inventor instance")

            self.inv_app.Visible = True
            self.tg = self.inv_app.TransientGeometry
            self._is_connected = True

        except Exception as e:
            logger.error(f"Failed to connect to Inventor: {e}")
            self._cleanup()
            raise

    def disconnect(self):
        """
        Disconnect from Inventor and cleanup resources.

        Note: Does not close Inventor if other documents are open.
        """
        self._cleanup()

    def _cleanup(self):
        """Internal cleanup of COM objects and caches."""
        # Clear caches
        self._occurrence_cache.clear()

        # Release COM objects
        self.main_assy_def = None
        self.main_assy_doc = None
        self.tg = None

        # Don't close Inventor if user has other documents open
        if self.inv_app:
            try:
                # Only quit if no documents are open (besides ours)
                if self.inv_app.Documents.Count == 0:
                    logger.debug("No documents open, but keeping Inventor running")
            except Exception as e:
                logger.debug(f"Could not check Inventor document count: {e}")
            finally:
                self.inv_app = None

        self._is_connected = False
        logger.debug("Inventor resources cleaned up")

    def is_connected(self):
        """Check if connected to Inventor."""
        return self._is_connected and self.inv_app is not None

    def _ensure_connected(self):
        """Ensure connection to Inventor exists, connect if needed."""
        if not self.is_connected():
            self.connect()

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _get_geometry_proxies(self, occurrence, axes=None, planes=None):
        """
        Get geometry proxies for specified axes and planes from an occurrence.

        Args:
            occurrence: Inventor ComponentOccurrence
            axes: List of axis names (defaults to [AXIS_Y])
            planes: List of plane names (defaults to [PLANE_XY, PLANE_XZ])

        Returns:
            dict: Proxies keyed by axis/plane name
        """
        axes = axes or [AXIS_Y]
        planes = planes or [PLANE_XY, PLANE_XZ]
        proxies = {}

        for axis_name in axes:
            try:
                proxies[axis_name] = occurrence.CreateGeometryProxy(
                    occurrence.Definition.WorkAxes[axis_name]
                )
            except Exception as e:
                logger.warning(f"Failed to get axis proxy '{axis_name}': {e}")

        for plane_name in planes:
            try:
                proxies[plane_name] = occurrence.CreateGeometryProxy(
                    occurrence.Definition.WorkPlanes[plane_name]
                )
            except Exception as e:
                logger.warning(f"Failed to get plane proxy '{plane_name}': {e}")

        return proxies

    def _add_mate_constraint(self, assy_def, entity1, entity2, offset=0):
        """
        Add mate constraint with standard Inventor parameters.

        Args:
            assy_def: Assembly ComponentDefinition
            entity1: First geometry entity
            entity2: Second geometry entity
            offset: Offset distance (default 0)

        Returns:
            MateConstraint object
        """
        return assy_def.Constraints.AddMateConstraint2(
            entity1, entity2, offset,
            MATE_CONSTRAINT_INFERENCE_1, MATE_CONSTRAINT_INFERENCE_2,
            FLUSH_CONSTRAINT_TYPE, None, None
        )

    def _add_flush_constraint(self, assy_def, entity1, entity2, offset=0):
        """
        Add flush constraint between two entities.

        Args:
            assy_def: Assembly ComponentDefinition
            entity1: First geometry entity
            entity2: Second geometry entity
            offset: Offset distance (default 0)

        Returns:
            FlushConstraint object
        """
        return assy_def.Constraints.AddFlushConstraint(entity1, entity2, offset, None, None)

    def _create_angled_plane(self, tg, assy_def, angle_degrees, name=None):
        """
        Create a work plane at specified angle from origin.

        Args:
            tg: TransientGeometry object
            assy_def: Assembly ComponentDefinition
            angle_degrees: Rotation angle in degrees
            name: Optional name for the plane

        Returns:
            WorkPlane object
        """
        angle_rad = math.radians(angle_degrees)
        origin = tg.CreatePoint(0.0, 0.0, 0.0)
        x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
        y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

        plane = assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
        plane.Visible = False
        plane.Grounded = True

        if name:
            plane.Name = name

        return plane

    def _create_circular_pattern(self, assy_def, components, axis, count, angle_degrees=None):
        """
        Create circular pattern of components around an axis.

        Args:
            assy_def: Assembly ComponentDefinition
            components: List of components to pattern
            axis: Axis entity for rotation
            count: Number of instances
            angle_degrees: Angle between instances (defaults to 360/count)

        Returns:
            CircularOccurrencePattern object
        """
        self._ensure_connected()

        angle_degrees = angle_degrees or (360.0 / count)
        angle_rad = math.radians(angle_degrees)

        obj_collection = self.inv_app.TransientObjects.CreateObjectCollection()
        for comp in components:
            obj_collection.Add(comp)

        return assy_def.OccurrencePatterns.AddCircularPattern(
            ParentComponents=obj_collection,
            AxisEntity=axis,
            AxisEntityNaturalDirection=True,
            AngleOffset=angle_rad,
            Count=count
        )

    def _get_cached_occurrence(self, name, occurrences):
        """
        Get occurrence with caching to avoid repeated recursive searches.

        Args:
            name: Target occurrence name
            occurrences: Occurrences collection to search

        Returns:
            ComponentOccurrence or None
        """
        cache_key = f"{id(occurrences)}:{name}"
        if cache_key not in self._occurrence_cache:
            self._occurrence_cache[cache_key] = self.find_occurrence_recursive(occurrences, name)
        return self._occurrence_cache[cache_key]

    def _clear_occurrence_cache(self):
        """Clear the occurrence cache."""
        self._occurrence_cache = {}

    def _validate_occurrence(self, occurrence, name):
        """
        Validate that an occurrence exists.

        Args:
            occurrence: The occurrence to validate
            name: Name for error message

        Returns:
            The occurrence if valid

        Raises:
            ValueError: If occurrence is None
        """
        if occurrence is None:
            raise ValueError(f"Required occurrence '{name}' not found in assembly")
        return occurrence

    def _create_dimension_text_point(self, tg, pt1, pt2):
        """
        Create a 2D point at the midpoint between two sketch points for dimension text.

        Args:
            tg: TransientGeometry object
            pt1: First sketch point
            pt2: Second sketch point

        Returns:
            Point2d object
        """
        mid_x = (pt1.Geometry.X + pt2.Geometry.X) / 2
        mid_y = (pt1.Geometry.Y + pt2.Geometry.Y) / 2
        return tg.CreatePoint2d(mid_x, mid_y)

    def _parse_component_name(self, component_name):
        """
        Parse component name to extract nozzle info (name-independent).

        New pattern: nozzle_{size}_{degree}_{fitting...}
        Examples:
            'nozzle_150_60_split_flange_1' → {'size': '150', 'degree': '60', 'fitting': 'split_flange'}
            'nozzle_500_0_gasket_1' → {'size': '500', 'degree': '0', 'fitting': 'gasket'}
            'nozzle_200_d_gasket_1' → {'size': '200', 'degree': 'd', 'fitting': 'gasket'}
            'monoblock' → None (not a nozzle component)

        Args:
            component_name: Component name string

        Returns:
            dict with size, degree, fitting keys, or None if not a nozzle component.
            Note: 'nozzle' key is intentionally NOT included - identification is by size/degree only.
        """
        if not component_name:
            return None

        parts = component_name.lower().split('_')

        # New pattern: nozzle_{size}_{degree}_{fitting...}[_{id}]
        if len(parts) >= 4 and parts[0] == 'nozzle':
            size = parts[1]    # '150', '500', '200'
            degree = parts[2]  # '60', '0', 'd'
            fitting = '_'.join(parts[3:])  # 'split_flange_1', 'gasket_1', 'bolt/stud'

            # Remove trailing numeric ID from fitting
            fitting_parts = fitting.split('_')
            if fitting_parts and fitting_parts[-1].isdigit():
                fitting = '_'.join(fitting_parts[:-1])

            return {
                'size': size,
                'degree': degree,
                'fitting': fitting
            }

        return None

    def _is_vessel_nozzle(self, component_name):
        """
        Check if component is a vessel nozzle using property-based detection.

        Vessel nozzle: size != 500 (not manhole) AND degree not in ('d', '-', '', 'none') (not center).
        Uses only size and degree properties - NO nozzle names.

        Args:
            component_name: Component name string

        Returns:
            bool: True if vessel nozzle component
        """
        parsed = self._parse_component_name(component_name)
        if not parsed:
            return False

        size = parsed['size']
        degree = parsed['degree']

        # Exclude manhole (size=500) - has special handling
        if size == '500':
            return False

        # Exclude center nozzle (degree=d) - has special handling
        if degree in ('d', '-', '', 'none'):
            return False

        return True

    def _get_component_handler(self, component_name: str, item: dict = None):
        """
        Match component name to handler using property-based detection.

        For nozzle components (nozzle_{size}_{degree}_{fitting}):
        - Vessel nozzles: dispatches to fitting-specific handlers
        - Manhole (size=500): dispatches to manhole handlers
        - Center nozzle (degree=d): dispatches to center nozzle handler

        Falls back to exact/prefix matching for non-nozzle components.

        Args:
            component_name: Component name string
            item: Optional item dict containing component data (may include fastener_count)

        Returns:
            tuple: (handler_method, config_dict, parsed_info) or (None, None, None)
        """
        # First, try to parse as nozzle component
        parsed = self._parse_component_name(component_name)

        if parsed:
            fitting = parsed['fitting']
            size = parsed['size']
            degree = parsed['degree']

            # Build config from fitting type and item metadata (NO NOZZLE_CONFIG lookup)
            fitting_config = FITTING_CONFIG.get(fitting, {})
            config = {**fitting_config}

            # Get fastener_count from item metadata (derived from nozzle size)
            if item and 'fastener_count' in item:
                config['fastener_count'] = item['fastener_count']

            # Vessel nozzle: not manhole, not center
            if self._is_vessel_nozzle(component_name):
                if 'split_flange' in fitting:
                    return self._handle_nozzle_split_flange, config, parsed
                elif 'gasket' in fitting:
                    return self._handle_nozzle_gasket, config, parsed
                elif any(x in fitting for x in ['blind_cover', 'baffle', 'toughened_glass', 'sight']):
                    return self._handle_nozzle_cover, config, parsed
                elif any(x in fitting for x in ['bolt', 'stud', 'washer', 'nut']):
                    return self._handle_nozzle_fastener, config, parsed

            # Manhole nozzle: size=500
            if size == '500':
                # Route to manhole-specific handlers (will be implemented in Phase 3)
                pass

            # Center nozzle: degree=d
            if degree in ('d', '-', '', 'none'):
                # Route to center nozzle handler (will be implemented in Phase 3)
                pass

        # Fall back to exact/prefix matching for non-nozzle components
        for category, handler_config in COMPONENT_HANDLERS.items():
            for pattern in handler_config["patterns"]:
                if component_name == pattern or component_name.startswith(pattern):
                    handler_name = handler_config["handler"]
                    if hasattr(self, handler_name):
                        handler = getattr(self, handler_name)
                        return handler, handler_config, None

        return None, None, None

    # =========================================================================
    # GENERIC NOZZLE ASSEMBLY HELPERS
    # =========================================================================

    def _get_nozzle_geometry(self, swagged_dish, nozzle_deg, tolerance=2.0):
        """
        Get the work plane and axis for a nozzle at a specific degree.

        Args:
            swagged_dish: The swagged dish occurrence
            nozzle_deg: Target degree for the nozzle plane
            tolerance: Degree tolerance for matching (default 2.0)

        Returns:
            tuple: (plane, axis) or (None, None) if not found
        """
        try:
            plane = self.get_workplanes_by_degrees(
                work_planes=swagged_dish.Definition.WorkPlanes,
                target=nozzle_deg,
                tolerance=tolerance
            )
            if plane is None:
                logger.warning(f"No work plane found for degree {nozzle_deg}")
                return None, None

            axis = self.get_y_parallel_axis_from_plane(
                work_axes=swagged_dish.Definition.WorkAxes,
                plane=plane
            )
            if axis is None:
                logger.warning(f"No Y-parallel axis found for plane at {nozzle_deg} degrees")
                return None, None

            return plane, axis
        except Exception as e:
            logger.error(f"Error getting nozzle geometry at {nozzle_deg} degrees: {e}")
            return None, None

    def _get_fastener_axis_proxy(self, occurrence, axis_names=None):
        """
        Get the fastener assembly axis proxy from an occurrence.
        Tries the occurrence first, then sub-occurrences.

        Args:
            occurrence: The component occurrence (e.g., split flange)
            axis_names: List of axis name variants to try

        Returns:
            Proxy for the fastener assembly axis, or None
        """
        axis_names = axis_names or ["Fastener Assly Axis", "Fastner Assly Axis"]

        # Search each name across parent → sub before trying next name
        # This matches old static code behavior: correct spelling on parent/sub first
        for axis_name in axis_names:
            # Try parent occurrence
            axis = self.get_work_axis(work_axes=occurrence.Definition.WorkAxes, axis_name=axis_name)
            if axis is not None:
                return occurrence.CreateGeometryProxy(axis)

            # Try sub-occurrence
            if hasattr(occurrence, "SubOccurrences") and occurrence.SubOccurrences.Count > 0:
                sub_occ = occurrence.SubOccurrences.Item(1)
                axis = self.get_work_axis(work_axes=sub_occ.Definition.WorkAxes, axis_name=axis_name)
                if axis is not None:
                    return sub_occ.CreateGeometryProxy(axis)

        return None

    def _get_top_face_plane_proxy(self, occurrence, plane_name="TOP FACE PLANE"):
        """
        Get the top face plane proxy from an occurrence.
        Tries the occurrence first, then sub-occurrences.

        Args:
            occurrence: The component occurrence
            plane_name: Name of the plane to find

        Returns:
            Proxy for the top face plane, or None
        """
        plane = self.get_work_plane(work_planes=occurrence.Definition.WorkPlanes, plane_name=plane_name)
        if plane is not None:
            return occurrence.CreateGeometryProxy(plane)

        # Try sub-occurrences
        if hasattr(occurrence, "SubOccurrences") and occurrence.SubOccurrences.Count > 0:
            sub_occ = occurrence.SubOccurrences.Item(1)
            plane = self.get_work_plane(work_planes=sub_occ.Definition.WorkPlanes, plane_name=plane_name)
            if plane is not None:
                return sub_occ.CreateGeometryProxy(plane)

        return None

    def _add_nozzle_split_flange(self, main_assy_def, tg, filepath, swagged_dish,
                                  nozzle_axis, nozzle_plane, monoblock, nozzle_size):
        """
        Add a split flange for a vessel nozzle and apply standard constraints.

        Args:
            main_assy_def: Assembly definition
            tg: TransientGeometry object
            filepath: Path to the split flange file
            swagged_dish: Swagged dish occurrence
            nozzle_axis: Nozzle axis on swagged dish
            nozzle_plane: Nozzle plane on swagged dish
            monoblock: Monoblock occurrence
            nozzle_size: Size of the nozzle (for plane lookup)

        Returns:
            dict with occurrence and proxy references, or None on failure
        """
        try:
            occ = main_assy_def.Occurrences.Add(filepath, tg.CreateMatrix())
            occ.Grounded = False

            # Get geometry proxies
            y_axis_proxy = occ.CreateGeometryProxy(occ.Definition.WorkAxes["Y Axis"])
            xy_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XY PLANE"])

            # Get fastener axis and top face plane
            fastener_axis_proxy = self._get_fastener_axis_proxy(occ)
            top_face_plane_proxy = self._get_top_face_plane_proxy(occ)

            # Get swagged dish proxies
            swagged_dish_axis_proxy = swagged_dish.CreateGeometryProxy(nozzle_axis)
            swagged_dish_plane_proxy = swagged_dish.CreateGeometryProxy(nozzle_plane)

            # Get monoblock nozzle height plane
            monoblock_fabricated = monoblock.SubOccurrences.Item(1)
            monoblock_nozzle_plane = self.get_work_plane(
                work_planes=monoblock_fabricated.Definition.WorkPlanes,
                plane_name=f"{nozzle_size} NB"
            )
            monoblock_nozzle_plane_proxy = monoblock_fabricated.CreateGeometryProxy(monoblock_nozzle_plane)

            # Apply constraints
            self._add_mate_constraint(main_assy_def, swagged_dish_axis_proxy, y_axis_proxy)
            self._add_flush_constraint(main_assy_def, swagged_dish_plane_proxy, xy_plane_proxy)
            self._add_flush_constraint(main_assy_def, monoblock_nozzle_plane_proxy, top_face_plane_proxy, -2.0)

            self.hide_workplanes_recursively(occurrence=occ)

            return {
                'occurrence': occ,
                'y_axis_proxy': y_axis_proxy,
                'xy_plane_proxy': xy_plane_proxy,
                'fastener_axis_proxy': fastener_axis_proxy,
                'top_face_plane_proxy': top_face_plane_proxy,
                'swagged_dish_axis_proxy': swagged_dish_axis_proxy,
                'swagged_dish_plane_proxy': swagged_dish_plane_proxy
            }
        except Exception as e:
            logger.error(f"Error adding split flange: {e}")
            return None

    def _add_nozzle_gasket(self, main_assy_def, tg, filepath, swagged_dish_axis_proxy,
                           swagged_dish_plane_proxy, flange_top_face_proxy, slit_envelope_name=None):
        """
        Add a gasket for a vessel nozzle.

        Args:
            main_assy_def: Assembly definition
            tg: TransientGeometry object
            filepath: Path to the gasket file
            swagged_dish_axis_proxy: Axis proxy on swagged dish
            swagged_dish_plane_proxy: Plane proxy on swagged dish
            flange_top_face_proxy: Top face plane proxy from the split flange
            slit_envelope_name: Name to search for slit envelope (optional)

        Returns:
            dict with occurrence and proxy references, or None on failure
        """
        try:
            occ = main_assy_def.Occurrences.Add(filepath, tg.CreateMatrix())
            occ.Grounded = False

            y_axis_proxy = occ.CreateGeometryProxy(occ.Definition.WorkAxes["Y Axis"])
            xy_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XY PLANE"])
            xz_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XZ PLANE"])

            # Try to find gasket ref plane in slit envelope
            gasket_ref_plane = None
            if slit_envelope_name:
                slit_envelope = self.find_occurrence_recursive(
                    occurrences=occ.SubOccurrences,
                    target_name=slit_envelope_name
                )
                if slit_envelope:
                    gasket_ref_plane = slit_envelope.CreateGeometryProxy(
                        slit_envelope.Definition.WorkPlanes["GASKET REF PLANE"]
                    )
            else:
                # Try generic search
                slit_envelope = self.find_occurrence_recursive(
                    occurrences=occ.SubOccurrences,
                    target_name='SLIT ENVELOPE'
                )
                if slit_envelope:
                    gasket_ref_plane = slit_envelope.CreateGeometryProxy(
                        slit_envelope.Definition.WorkPlanes["GASKET REF PLANE"]
                    )

            # Apply constraints
            self._add_mate_constraint(main_assy_def, swagged_dish_axis_proxy, y_axis_proxy)
            self._add_flush_constraint(main_assy_def, swagged_dish_plane_proxy, xy_plane_proxy)
            self._add_flush_constraint(main_assy_def, flange_top_face_proxy, xz_plane_proxy, 2.2)

            return {
                'occurrence': occ,
                'y_axis_proxy': y_axis_proxy,
                'xy_plane_proxy': xy_plane_proxy,
                'xz_plane_proxy': xz_plane_proxy,
                'gasket_ref_plane': gasket_ref_plane
            }
        except Exception as e:
            logger.error(f"Error adding gasket: {e}")
            return None

    def _add_nozzle_cover(self, main_assy_def, tg, filepath, gasket_y_axis_proxy,
                          flange_xy_plane_proxy, gasket_ref_plane, use_angle=True, angle_deg='22.5 deg'):
        """
        Add a blind cover or baffle for a vessel nozzle.

        Args:
            main_assy_def: Assembly definition
            tg: TransientGeometry object
            filepath: Path to the cover file
            gasket_y_axis_proxy: Y axis proxy from the gasket
            flange_xy_plane_proxy: XY plane proxy from the split flange
            gasket_ref_plane: Gasket reference plane proxy
            use_angle: Whether to use angle constraint instead of flush (default True)
            angle_deg: Angle for angle constraint (default '22.5 deg')

        Returns:
            dict with occurrence and proxy references, or None on failure
        """
        try:
            occ = main_assy_def.Occurrences.Add(filepath, tg.CreateMatrix())
            occ.Grounded = False

            y_axis_proxy = occ.CreateGeometryProxy(occ.Definition.WorkAxes["Y Axis"])
            xy_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XY PLANE"])
            xz_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XZ PLANE"])

            # Apply constraints
            self._add_mate_constraint(main_assy_def, gasket_y_axis_proxy, y_axis_proxy)

            if use_angle:
                main_assy_def.Constraints.AddAngleConstraint(
                    flange_xy_plane_proxy, xy_plane_proxy, angle_deg, 78593, None, None, None
                )
            else:
                self._add_flush_constraint(main_assy_def, flange_xy_plane_proxy, xy_plane_proxy)

            if gasket_ref_plane:
                self._add_flush_constraint(main_assy_def, gasket_ref_plane, xz_plane_proxy, 0)

            return {
                'occurrence': occ,
                'y_axis_proxy': y_axis_proxy,
                'xy_plane_proxy': xy_plane_proxy,
                'xz_plane_proxy': xz_plane_proxy
            }
        except Exception as e:
            logger.error(f"Error adding cover: {e}")
            return None

    def _add_nozzle_fastener(self, main_assy_def, tg, filepath, flange_fastener_axis_proxy,
                              cover_xz_plane_proxy, cover_xy_plane_proxy, flush_offset=-1.8):
        """
        Add a fastener (bolt/stud) for a vessel nozzle.

        Args:
            main_assy_def: Assembly definition
            tg: TransientGeometry object
            filepath: Path to the fastener file
            flange_fastener_axis_proxy: Fastener axis proxy from the split flange
            cover_xz_plane_proxy: XZ plane proxy from the cover
            cover_xy_plane_proxy: XY plane proxy from the cover
            flush_offset: Offset for flush constraint (default -1.8)

        Returns:
            dict with occurrence and proxy references, or None on failure
        """
        try:
            occ = main_assy_def.Occurrences.Add(filepath, tg.CreateMatrix())
            occ.Grounded = False

            y_axis_proxy = occ.CreateGeometryProxy(occ.Definition.WorkAxes["Y Axis"])
            xy_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XY PLANE"])
            xz_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XZ PLANE"])

            # Apply constraints
            self._add_mate_constraint(main_assy_def, y_axis_proxy, flange_fastener_axis_proxy)
            self._add_flush_constraint(main_assy_def, xz_plane_proxy, cover_xz_plane_proxy, flush_offset)
            main_assy_def.Constraints.AddAngleConstraint(
                xy_plane_proxy, cover_xy_plane_proxy, 0, 78593, None, None, None
            )

            return {
                'occurrence': occ,
                'y_axis_proxy': y_axis_proxy,
                'xy_plane_proxy': xy_plane_proxy,
                'xz_plane_proxy': xz_plane_proxy
            }
        except Exception as e:
            logger.error(f"Error adding fastener: {e}")
            return None

    def _add_nozzle_washer(self, main_assy_def, tg, filepath, fastener_y_axis_proxy,
                            fastener_xy_plane_proxy, flange_top_face_proxy, mate_offset=-2.2):
        """
        Add a washer for a vessel nozzle.

        Args:
            main_assy_def: Assembly definition
            tg: TransientGeometry object
            filepath: Path to the washer file
            fastener_y_axis_proxy: Y axis proxy from the fastener
            fastener_xy_plane_proxy: XY plane proxy from the fastener
            flange_top_face_proxy: Top face plane proxy from the split flange
            mate_offset: Offset for mate constraint (default -2.2)

        Returns:
            dict with occurrence and proxy references, or None on failure
        """
        try:
            occ = main_assy_def.Occurrences.Add(filepath, tg.CreateMatrix())
            occ.Grounded = False

            y_axis_proxy = occ.CreateGeometryProxy(occ.Definition.WorkAxes["Y Axis"])
            xy_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XY PLANE"])
            xz_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XZ PLANE"])
            fastener_assly_plane_proxy = occ.CreateGeometryProxy(
                occ.Definition.WorkPlanes["Fastener Assly Plane"]
            )

            # Apply constraints
            self._add_mate_constraint(main_assy_def, y_axis_proxy, fastener_y_axis_proxy)
            main_assy_def.Constraints.AddMateConstraint(
                xz_plane_proxy, flange_top_face_proxy, mate_offset,
                MATE_CONSTRAINT_INFERENCE_1, MATE_CONSTRAINT_INFERENCE_2, None, None
            )
            self._add_flush_constraint(main_assy_def, xy_plane_proxy, fastener_xy_plane_proxy)

            return {
                'occurrence': occ,
                'y_axis_proxy': y_axis_proxy,
                'xy_plane_proxy': xy_plane_proxy,
                'xz_plane_proxy': xz_plane_proxy,
                'fastener_assly_plane_proxy': fastener_assly_plane_proxy
            }
        except Exception as e:
            logger.error(f"Error adding washer: {e}")
            return None

    def _add_nozzle_nut(self, main_assy_def, tg, filepath, washer_y_axis_proxy,
                         washer_xy_plane_proxy, washer_fastener_assly_plane_proxy):
        """
        Add a nut for a vessel nozzle.

        Args:
            main_assy_def: Assembly definition
            tg: TransientGeometry object
            filepath: Path to the nut file
            washer_y_axis_proxy: Y axis proxy from the washer
            washer_xy_plane_proxy: XY plane proxy from the washer
            washer_fastener_assly_plane_proxy: Fastener assembly plane proxy from the washer

        Returns:
            dict with occurrence and proxy references, or None on failure
        """
        try:
            occ = main_assy_def.Occurrences.Add(filepath, tg.CreateMatrix())
            occ.Grounded = False

            y_axis_proxy = occ.CreateGeometryProxy(occ.Definition.WorkAxes["Y Axis"])
            xy_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XY PLANE"])
            xz_plane_proxy = occ.CreateGeometryProxy(occ.Definition.WorkPlanes["XZ PLANE"])

            # Apply constraints
            self._add_mate_constraint(main_assy_def, y_axis_proxy, washer_y_axis_proxy)
            self._add_flush_constraint(main_assy_def, xz_plane_proxy, washer_fastener_assly_plane_proxy)
            self._add_flush_constraint(main_assy_def, xy_plane_proxy, washer_xy_plane_proxy)

            return {
                'occurrence': occ,
                'y_axis_proxy': y_axis_proxy,
                'xy_plane_proxy': xy_plane_proxy,
                'xz_plane_proxy': xz_plane_proxy
            }
        except Exception as e:
            logger.error(f"Error adding nut: {e}")
            return None

    def _create_fastener_pattern(self, main_assy_def, fastener, washer, nut, pattern_axis, count=8):
        """
        Create a circular pattern for fastener set (bolt + washer + nut).

        Args:
            main_assy_def: Assembly definition
            fastener: Fastener occurrence
            washer: Washer occurrence
            nut: Nut occurrence
            pattern_axis: Axis to pattern around
            count: Number of instances (default 8)

        Returns:
            CircularOccurrencePattern or None on failure
        """
        try:
            return self._create_circular_pattern(
                main_assy_def,
                [fastener, washer, nut],
                pattern_axis,
                count
            )
        except Exception as e:
            logger.error(f"Error creating fastener pattern: {e}")
            return None

    # =========================================================================
    # DYNAMIC COMPONENT HANDLERS
    # These methods are called by _get_component_handler for dynamic dispatch
    # =========================================================================

    def _handle_nozzle_split_flange(self, item, config, parsed, context):
        """
        Handle any nozzle split_flange component dynamically.

        Args:
            item: Component item dict with filepath, component name, etc.
            config: Combined nozzle and fitting config
            parsed: Parsed component name info (size, degree, fitting) - NO nozzle name
            context: Shared context with main_assy_def, swagged_dish, etc.

        Returns:
            Occurrence or None
        """
        nozzle_deg = parsed['degree']
        nozzle_size = parsed['size']

        if nozzle_deg == '180':
            print(parsed)
        print(f"Start: nozzle_{nozzle_size}_{nozzle_deg}_split_flange")

        # Get swagged dish reference
        swagged_dish = context.get('swagged_dish')
        if swagged_dish is None:
            swagged_dish = self.find_occurrence_recursive(
                occurrences=context['main_assy_def'].Occurrences,
                target_name="CT-1950"
            )
            context['swagged_dish'] = swagged_dish

        if swagged_dish is None:
            print(f"Warning: Could not find swagged_dish for nozzle_{nozzle_size}_{nozzle_deg}")
            return None

        # Get geometry for this nozzle degree
        plane, axis = self._get_nozzle_geometry(swagged_dish, nozzle_deg)
        if axis is None or plane is None:
            print(f"Warning: Could not find plane/axis for nozzle at {nozzle_deg}°")
            return None

        # Mark plane as used
        self._used_nozzle_planes.append(plane.Name)

        # Add component
        main_assy_def = context['main_assy_def']
        tg = context['tg']
        occurrence = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
        occurrence.Grounded = False

        # Create proxies
        y_axis_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkAxes["Y Axis"])
        xy_plane_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkPlanes["XY PLANE"])

        # Get fastener axis and top face plane for subsequent components
        fastener_axis = self._get_fastener_axis_proxy(occurrence)
        top_face_plane = self._get_top_face_plane_proxy(occurrence)

        # Create dish proxies and apply constraints
        dish_axis_proxy = swagged_dish.CreateGeometryProxy(axis)
        dish_plane_proxy = swagged_dish.CreateGeometryProxy(plane)

        # Get monoblock nozzle height plane
        monoblock = context.get('monoblock')
        monoblock_plane_proxy = None
        if monoblock:
            monoblock_fabricated = monoblock.SubOccurrences.Item(1)
            monoblock_plane = self.get_work_plane(
                work_planes=monoblock_fabricated.Definition.WorkPlanes,
                plane_name=f"{nozzle_size} NB"
            )
            if monoblock_plane:
                monoblock_plane_proxy = monoblock_fabricated.CreateGeometryProxy(monoblock_plane)

        # Apply constraints
        self._add_mate_constraint(main_assy_def, dish_axis_proxy, y_axis_proxy)
        self._add_flush_constraint(main_assy_def, dish_plane_proxy, xy_plane_proxy)
        if monoblock_plane_proxy and top_face_plane:
            self._add_flush_constraint(main_assy_def, monoblock_plane_proxy, top_face_plane, -2.0)

        # Store state for subsequent components keyed by size_degree (name-independent)
        nozzle_key = f"{nozzle_size}_{nozzle_deg}"
        self._nozzle_state[nozzle_key] = {
            'occurrence': occurrence,
            'axis': axis,
            'plane': plane,
            'dish_axis_proxy': dish_axis_proxy,
            'dish_plane_proxy': dish_plane_proxy,
            'fastener_axis': fastener_axis,
            'top_face_plane': top_face_plane,
            'y_axis_proxy': y_axis_proxy,
            'xy_plane_proxy': xy_plane_proxy,
        }

        self.hide_workplanes_recursively(occurrence)
        print(f"End: nozzle_{nozzle_size}_{nozzle_deg}_split_flange")
        return occurrence

    def _handle_nozzle_gasket(self, item, config, parsed, context):
        """
        Handle any nozzle gasket component dynamically.

        Args:
            item: Component item dict
            config: Combined nozzle and fitting config
            parsed: Parsed component name info (size, degree, fitting)
            context: Shared context

        Returns:
            Occurrence or None
        """
        nozzle_deg = parsed['degree']
        nozzle_size = parsed['size']
        nozzle_key = f"{nozzle_size}_{nozzle_deg}"

        print(f"Start: nozzle_{nozzle_size}_{nozzle_deg}_gasket")

        state = self._nozzle_state.get(nozzle_key)
        if not state:
            print(f"Warning: No split_flange state for {nozzle_key}, skipping gasket")
            return None

        # Add component
        main_assy_def = context['main_assy_def']
        tg = context['tg']
        occurrence = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
        occurrence.Grounded = False

        # Create proxies
        y_axis_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkAxes["Y Axis"])
        xy_plane_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkPlanes["XY PLANE"])
        xz_plane_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkPlanes["XZ PLANE"])

        # Try to find gasket ref plane for subsequent components
        gasket_ref_plane = None
        slit_envelope = self.find_occurrence_recursive(
            occurrences=occurrence.SubOccurrences,
            target_name="SLIT ENVELOPE"
        )
        if slit_envelope:
            gasket_ref_plane = self.get_work_plane(
                work_planes=slit_envelope.Definition.WorkPlanes,
                plane_name="GASKET REF PLANE"
            )
            if gasket_ref_plane:
                gasket_ref_plane = slit_envelope.CreateGeometryProxy(gasket_ref_plane)

        # Apply constraints
        # Check item metadata for gasket_offset (sight glass nozzles use 2.0)
        offset = item.get('gasket_offset') or config.get('offset', 2.2)
        self._add_mate_constraint(main_assy_def, state['dish_axis_proxy'], y_axis_proxy)
        self._add_flush_constraint(main_assy_def, state['dish_plane_proxy'], xy_plane_proxy)
        if state.get('top_face_plane'):
            self._add_flush_constraint(main_assy_def, state['top_face_plane'], xz_plane_proxy, offset)

        # Update state with gasket reference
        state['gasket'] = occurrence
        state['gasket_y_axis_proxy'] = y_axis_proxy
        state['gasket_xy_plane_proxy'] = xy_plane_proxy
        state['gasket_xz_plane_proxy'] = xz_plane_proxy
        state['gasket_ref_plane'] = gasket_ref_plane

        self.hide_workplanes_recursively(occurrence)
        print(f"End: nozzle_{nozzle_size}_{nozzle_deg}_gasket")
        return occurrence

    def _handle_nozzle_cover(self, item, config, parsed, context):
        """
        Handle nozzle cover components (blind_cover, baffle, toughened_glass, sight_glass).

        Args:
            item: Component item dict
            config: Combined nozzle and fitting config
            parsed: Parsed component name info (size, degree, fitting)
            context: Shared context

        Returns:
            Occurrence or None
        """
        nozzle_deg = parsed['degree']
        nozzle_size = parsed['size']
        fitting = parsed['fitting']
        nozzle_key = f"{nozzle_size}_{nozzle_deg}"

        print(f"Start: nozzle_{nozzle_size}_{nozzle_deg}_{fitting}")

        state = self._nozzle_state.get(nozzle_key)
        if not state:
            print(f"Warning: No state for {nozzle_key}, skipping {fitting}")
            return None

        # Add component
        main_assy_def = context['main_assy_def']
        tg = context['tg']
        occurrence = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
        occurrence.Grounded = False

        # Create proxies
        y_axis_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkAxes["Y Axis"])
        xy_plane_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkPlanes["XY PLANE"])
        xz_plane_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkPlanes["XZ PLANE"])

        # Apply constraints based on cover type
        gasket_y_axis = state.get('gasket_y_axis_proxy')
        gasket_ref_plane = state.get('gasket_ref_plane')
        split_flange_xy = state.get('xy_plane_proxy')

        if 'toughened_glass' in fitting:
            # Toughened glass aligns to gasket XY plane (not split flange)
            gasket_xy = state.get('gasket_xy_plane_proxy')
            if gasket_y_axis:
                self._add_mate_constraint(main_assy_def, gasket_y_axis, y_axis_proxy)
            if gasket_xy:
                self._add_flush_constraint(main_assy_def, gasket_xy, xy_plane_proxy)
            if gasket_ref_plane:
                self._add_flush_constraint(main_assy_def, gasket_ref_plane, xz_plane_proxy, 2.0)
            # Store toughened_glass XZ for sight_glass_flange reference
            state['toughened_glass_xz_proxy'] = xz_plane_proxy

        elif 'sight' in fitting or 'light_glass' in fitting:
            # Sight/light glass flange uses toughened_glass XZ → ASSEMBLY PLANE
            if gasket_y_axis:
                self._add_mate_constraint(main_assy_def, gasket_y_axis, y_axis_proxy)
            if split_flange_xy:
                self._add_flush_constraint(main_assy_def, split_flange_xy, xy_plane_proxy)
            tg_xz = state.get('toughened_glass_xz_proxy')
            if tg_xz:
                try:
                    assembly_plane_proxy = occurrence.CreateGeometryProxy(
                        occurrence.Definition.WorkPlanes["ASSEMBLY PLANE"])
                    self._add_flush_constraint(main_assy_def, tg_xz, assembly_plane_proxy, 0.3)
                except Exception as e:
                    print(f"Warning: Could not find ASSEMBLY PLANE for sight glass: {e}")
                    if gasket_ref_plane:
                        self._add_flush_constraint(main_assy_def, gasket_ref_plane, xz_plane_proxy, 0)
            elif gasket_ref_plane:
                self._add_flush_constraint(main_assy_def, gasket_ref_plane, xz_plane_proxy, 0)

        else:
            # Blind cover and baffle
            if gasket_y_axis:
                self._add_mate_constraint(main_assy_def, gasket_y_axis, y_axis_proxy)
            if split_flange_xy:
                if 'blind_cover' in fitting:
                    # Blind cover bolt holes are offset from split flange XY reference
                    # by half a bolt spacing. Rotation = 360 / (2 * fastener_count).
                    from services.generation_service import FASTENER_COUNT_BY_SIZE
                    fc = FASTENER_COUNT_BY_SIZE.get(nozzle_size, 8)
                    half_angle = 360 / (2 * fc)
                    main_assy_def.Constraints.AddAngleConstraint(
                        split_flange_xy, xy_plane_proxy, f'{half_angle} deg', 78593, None, None, None)
                else:
                    # Baffle: flush alignment
                    self._add_flush_constraint(main_assy_def, split_flange_xy, xy_plane_proxy)
            if gasket_ref_plane:
                self._add_flush_constraint(main_assy_def, gasket_ref_plane, xz_plane_proxy, 0)

        # Store cover reference for fastener pattern
        state['cover'] = occurrence
        state['cover_y_axis_proxy'] = y_axis_proxy
        state['cover_xy_plane_proxy'] = xy_plane_proxy
        state['cover_xz_plane_proxy'] = xz_plane_proxy
        state['bolt_offset'] = config.get('bolt_offset', -1.8)

        self.hide_workplanes_recursively(occurrence)
        print(f"End: nozzle_{nozzle_size}_{nozzle_deg}_{fitting}")
        return occurrence

    def _handle_nozzle_fastener(self, item, config, parsed, context):
        """
        Handle nozzle fastener components (bolt/stud, washer, nut).
        Creates circular pattern when nut is processed.

        Args:
            item: Component item dict
            config: Combined nozzle and fitting config
            parsed: Parsed component name info (size, degree, fitting)
            context: Shared context

        Returns:
            Occurrence or None
        """
        nozzle_deg = parsed['degree']
        nozzle_size = parsed['size']
        fitting = parsed['fitting']
        nozzle_key = f"{nozzle_size}_{nozzle_deg}"

        print(f"Start: nozzle_{nozzle_size}_{nozzle_deg}_{fitting}")

        state = self._nozzle_state.get(nozzle_key)
        if not state:
            print(f"Warning: No state for {nozzle_key}, skipping {fitting}")
            return None

        # Add component
        main_assy_def = context['main_assy_def']
        tg = context['tg']
        inv_app = context['inv_app']
        occurrence = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
        occurrence.Grounded = False

        # Create proxies
        y_axis_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkAxes["Y Axis"])
        xy_plane_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkPlanes["XY PLANE"])
        xz_plane_proxy = occurrence.CreateGeometryProxy(occurrence.Definition.WorkPlanes["XZ PLANE"])

        if 'bolt' in fitting or 'stud' in fitting:
            # Position bolt using fastener axis from split flange
            fastener_axis = state.get('fastener_axis')
            cover_xz = state.get('cover_xz_plane_proxy')
            cover_xy = state.get('cover_xy_plane_proxy')
            bolt_offset = state.get('bolt_offset', -1.8)
            print(f"  [DEBUG] Fastener axis for {nozzle_key}: {fastener_axis}")
            print(f"  [DEBUG] Cover XZ: {cover_xz}, Cover XY: {cover_xy}, bolt_offset: {bolt_offset}")

            if fastener_axis:
                self._add_mate_constraint(main_assy_def, y_axis_proxy, fastener_axis)
            if cover_xz:
                self._add_flush_constraint(main_assy_def, xz_plane_proxy, cover_xz, bolt_offset)
            if cover_xy:
                main_assy_def.Constraints.AddAngleConstraint(xy_plane_proxy, cover_xy, 0, 78593, None, None, None)

            state['bolt'] = occurrence
            state['bolt_y_axis_proxy'] = y_axis_proxy
            state['bolt_xy_plane_proxy'] = xy_plane_proxy
            state['bolt_xz_plane_proxy'] = xz_plane_proxy

        elif 'washer' in fitting:
            # Position washer relative to bolt
            bolt_y_axis = state.get('bolt_y_axis_proxy')
            bolt_xy = state.get('bolt_xy_plane_proxy')
            top_face = state.get('top_face_plane')

            # Get washer fastener assembly plane
            washer_fastener_plane = None
            try:
                washer_fastener_plane = occurrence.CreateGeometryProxy(
                    occurrence.Definition.WorkPlanes["Fastener Assly Plane"]
                )
            except:
                pass

            if bolt_y_axis:
                self._add_mate_constraint(main_assy_def, y_axis_proxy, bolt_y_axis)
            if top_face:
                washer_offset = -2.8 if int(nozzle_size) > 200 else -2.2
                main_assy_def.Constraints.AddMateConstraint(xz_plane_proxy, top_face, washer_offset, 24833, 24833, None, None)
            if bolt_xy:
                self._add_flush_constraint(main_assy_def, xy_plane_proxy, bolt_xy)

            state['washer'] = occurrence
            state['washer_y_axis_proxy'] = y_axis_proxy
            state['washer_xy_plane_proxy'] = xy_plane_proxy
            state['washer_fastener_plane'] = washer_fastener_plane

        elif 'nut' in fitting:
            # Position nut relative to washer
            washer_y_axis = state.get('washer_y_axis_proxy')
            washer_xy = state.get('washer_xy_plane_proxy')
            washer_fastener_plane = state.get('washer_fastener_plane')

            if washer_y_axis:
                self._add_mate_constraint(main_assy_def, y_axis_proxy, washer_y_axis)
            if washer_fastener_plane:
                self._add_flush_constraint(main_assy_def, xz_plane_proxy, washer_fastener_plane)
            if washer_xy:
                self._add_flush_constraint(main_assy_def, xy_plane_proxy, washer_xy)

            state['nut'] = occurrence

            # Create circular pattern for bolt + washer + nut
            bolt = state.get('bolt')
            washer = state.get('washer')
            pattern_axis = state.get('cover_y_axis_proxy', state.get('y_axis_proxy'))
            fastener_count = config.get('fastener_count', 8)
            print(f"  [DEBUG] Pattern axis: {pattern_axis}, Fastener count: {fastener_count}")
            print(f"  [DEBUG] Washer fastener plane: {state.get('washer_fastener_plane')}")

            if bolt and washer and pattern_axis:
                try:
                    collection = inv_app.TransientObjects.CreateObjectCollection()
                    collection.Add(bolt)
                    collection.Add(washer)
                    collection.Add(occurrence)

                    angle = math.radians(360 / fastener_count)
                    occurrence_patterns = main_assy_def.OccurrencePatterns
                    circular_pattern = occurrence_patterns.AddCircularPattern(
                        ParentComponents=collection,
                        AxisEntity=pattern_axis,
                        AxisEntityNaturalDirection=True,
                        AngleOffset=angle,
                        Count=fastener_count
                    )
                    print(f"Created circular pattern with {fastener_count} fasteners")
                except Exception as e:
                    print(f"Error creating circular pattern: {e}")

        self.hide_workplanes_recursively(occurrence)
        print(f"End: nozzle_{nozzle_size}_{nozzle_deg}_{fitting}")
        return occurrence

    # =========================================================================
    # MAIN METHODS
    # =========================================================================

    def open(self, files):
        """
        Open a part or assembly file in Inventor.

        Args:
            files: List of file paths (opens first file)

        Returns:
            bool: True if file opened and window brought to front

        Raises:
            FileNotFoundError: If file does not exist
        """
        part_path = files[0]
        if not os.path.isfile(part_path):
            raise FileNotFoundError(f"File not found: {part_path}")

        # Ensure connection to Inventor
        self._ensure_connected()

        part_doc = self.inv_app.Documents.Open(part_path)
        logger.info(f"Opened: {part_doc.DisplayName}")
        time.sleep(1)

        # Bring window to front
        window_title = self.inv_app.Caption
        hwnd = win32gui.FindWindow(None, window_title)

        if hwnd:
            win32gui.ShowWindow(hwnd, 5)  # SW_SHOW
            win32gui.SetForegroundWindow(hwnd)
            logger.info("Inventor window brought to the front")
            return True
        else:
            logger.warning("Could not find the Inventor window")
            return False
        
    def generate(self, components, model_details, use_dynamic_handlers=True):
        """
        Generate 3D assembly from component list.

        Args:
            components: List of component dicts with 'component' and 'filepath' keys
            model_details: Model configuration details
            use_dynamic_handlers: If True, use dynamic handler system for vessel nozzle
                                  components. Default True for name-independent dispatch.

        Returns:
            bool: True if generation successful
        """

        # Ensure connection to Inventor
        self._ensure_connected()

        # Clear occurrence cache for fresh generation
        self._clear_occurrence_cache()

        # Reset used nozzle planes list for fresh generation
        self._used_nozzle_planes = []

        # Reset nozzle state for fresh generation
        self._nozzle_state = {}

        # Sort components by dynamic priority (name-independent)
        from services.generation_service import get_dynamic_priority
        sorted_components = sorted(
            components,
            key=lambda x: get_dynamic_priority(x["component"])
        )

        # Use instance variables for Inventor app and TransientGeometry
        inv_app = self.inv_app
        tg = self.tg

        # Create a new Assembly document: Main Assembly
        self.main_assy_doc = inv_app.Documents.Add(
            "12291",
            inv_app.FileManager.GetTemplateFile("12291", "8963"),
            True
        )
        main_assy_doc = self.main_assy_doc
        self.main_assy_def = main_assy_doc.ComponentDefinition
        main_assy_def = self.main_assy_def

        monoblock = jacket = diapharm = sidebracket = jacketnozzle = None

        # Context for dynamic handlers (shared state across handler calls)
        handler_context = {
            'inv_app': inv_app,
            'tg': tg,
            'main_assy_def': main_assy_def,
            'monoblock': None,
            'jacket': None,
            'swagged_dish': None,
        }

        # Initialize manhole components and proxies (used by spring balance assembly and other components)
        manhole_cover = None
        manhole_cover_y_axis_proxy = None
        manhole_cover_xy_plane_proxy = None
        manhole_cover_xz_plane_proxy = None
        manhole_cover_yz_plane_proxy = None
        manhole_stump = None
        manhole_stump_y_axis_proxy = None
        manhole_stump_xy_plane_proxy = None

        # Initialize COC components and proxies (used by coc and bfcclamp components)
        coc_gasket = None
        coc_gasket_y_axis_proxy = None
        coc_gasket_xy_plane_proxy = None
        coc_gasket_xz_plane_proxy = None
        coc_body_flange = None
        coc_body_flange_xz_plane_proxy = None
        coc = None
        coc_y_axis_proxy = None
        coc_xy_plane_proxy = None
        coc_xz_plane_proxy = None
        coc_yz_plane_proxy = None

        # Bring Inventor window to front
        window_title = inv_app.Caption
        try:
            app = Application(backend="uia").connect(title=window_title)
            app.window(title=window_title).set_focus()
        except Exception as e:
            logger.warning(f"Could not bring Inventor window to front: {e}")
        try:
            for idx, item in enumerate(sorted_components):
                component_name = item.get("component", "")

                # Dynamic handler dispatch (when use_dynamic_handlers=True)
                if use_dynamic_handlers:
                    handler, config, parsed = self._get_component_handler(component_name, item)
                    if handler is not None:
                        try:
                            logger.info(f"[DYNAMIC] Processing: {component_name}")
                            result = handler(item, config, parsed, handler_context)

                            # Update context with key references for subsequent components
                            if component_name == 'monoblock':
                                handler_context['monoblock'] = result
                                monoblock = result  # Keep local var for existing code compatibility
                            elif component_name == 'jacket':
                                handler_context['jacket'] = result
                                jacket = result

                            continue  # Skip to next component, handler processed this one
                        except Exception as e:
                            print(f"[DYNAMIC] Error with handler for {component_name}: {e}")
                            print(f"[DYNAMIC] Falling back to static matching...")
                            # Fall through to static matching below

                # Static matching (existing code)
                if item.get("component") == 'monoblock':
                    logger.info("Start: Monoblock")
                    monoblock = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    monoblock.Grounded = False

                    # Main Assembly Work Axes and Work Planes
                    main_y_axis = main_assy_def.WorkAxes[AXIS_Y]
                    main_xy_plane = main_assy_def.WorkPlanes[PLANE_XY]
                    main_xz_plane = main_assy_def.WorkPlanes[PLANE_XZ]

                    # Monoblock Work Axes and Work Planes using helper
                    monoblock_proxies = self._get_geometry_proxies(monoblock, axes=[AXIS_Y], planes=[PLANE_XY, PLANE_XZ])
                    monoblock_y_axis = monoblock_proxies[AXIS_Y]
                    monoblock_xy_plane = monoblock_proxies[PLANE_XY]
                    monoblock_xz_plane = monoblock_proxies[PLANE_XZ]

                    # Constraints for Monoblock using helper methods
                    monoblock_mate_y = self._add_mate_constraint(main_assy_def, main_y_axis, monoblock_y_axis)
                    monoblock_flush_xy = self._add_flush_constraint(main_assy_def, main_xy_plane, monoblock_xy_plane)
                    monoblock_flush_xz = self._add_flush_constraint(main_assy_def, main_xz_plane, monoblock_xz_plane)

                    self.hide_workplanes_recursively(occurrence=monoblock)
                    handler_context['monoblock'] = monoblock  # Update context for dynamic handlers
                    logger.info("End: Monoblock")

                elif item.get("component") == 'jacket':
                    logger.info("Start: Jacket")
                    jacket = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    jacket.Grounded = False

                    # Monoblock Work Axes and Work Planes using helper
                    monoblock_proxies = self._get_geometry_proxies(monoblock, axes=[AXIS_Y], planes=[PLANE_XY, PLANE_XZ])
                    monoblock_y_axis = monoblock_proxies[AXIS_Y]
                    monoblock_xy_plane = monoblock_proxies[PLANE_XY]
                    monoblock_xz_plane = monoblock_proxies[PLANE_XZ]

                    # Jacket Work Axes and Work Planes using helper
                    jacket_proxies = self._get_geometry_proxies(jacket, axes=[AXIS_Y], planes=[PLANE_XY, PLANE_XZ])
                    jacket_y_axis = jacket_proxies[AXIS_Y]
                    jacket_xy_plane = jacket_proxies[PLANE_XY]
                    jacket_xz_plane = jacket_proxies[PLANE_XZ]

                    # Constraints for Jacket using helper methods
                    jacket_mate_y = self._add_mate_constraint(main_assy_def, monoblock_y_axis, jacket_y_axis)
                    jacket_flush_xy = self._add_flush_constraint(main_assy_def, monoblock_xy_plane, jacket_xy_plane)
                    jacket_flush_xz = self._add_flush_constraint(main_assy_def, jacket_xz_plane, monoblock_xz_plane, "52 mm")

                    self.hide_workplanes_recursively(occurrence=jacket)
                    handler_context['jacket'] = jacket  # Update context for dynamic handlers
                    logger.info("End: Jacket")

                    # JSR CUT
                    # print("JSR mounting cut start")
                    logger.info("Start: JSR mounting cut")
                    main_xy_plane = main_assy_def.WorkPlanes["XY Plane"]
                    jsr_sketch = main_assy_def.Sketches.Add(main_xy_plane)

                    jsr_mss = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="JSR-MSS")
                    jsr_mounting_plane = jsr_mss.Definition.WorkPlanes[3]
                    jsr_mounting_plane_proxy = jsr_mss.CreateGeometryProxy(jsr_mounting_plane)
                    jsr_mounting_plane_pg = jsr_sketch.AddByProjectingEntity(jsr_mounting_plane_proxy)
                    jsr_mounting_plane_pg.Construction = True

                    main_y_axis = main_assy_def.WorkAxes["Y Axis"]
                    main_y_axis_pg = jsr_sketch.AddByProjectingEntity(main_y_axis)

                    width = 100.0
                    height = 50.0
                    rect_lines = jsr_sketch.SketchLines.AddAsTwoPointRectangle(tg.CreatePoint2d(-width/2, 0), tg.CreatePoint2d(width/2, height))

                    rect_line_1 = rect_lines.Item(1)
                    rect_line_2 = rect_lines.Item(2)
                    rect_line_3 = rect_lines.Item(3)
                    rect_line_4 = rect_lines.Item(4)
                    
                    jsr_collinear = jsr_sketch.GeometricConstraints.AddCollinear(main_y_axis_pg, rect_line_2) 

                    dimTextPt = tg.CreatePoint2d(10, 10)
                    # dimension = jsr_sketch.DimensionConstraints.AddTwoPointDistance(jsr_mounting_plane_pg.StartSketchPoint, rect_line_2.EndSketchPoint, 19202, dimTextPt, False)
                    dimension = jsr_sketch.DimensionConstraints.AddTwoPointDistance(jsr_mounting_plane_pg.StartSketchPoint, rect_line_3.StartSketchPoint, 19202, dimTextPt, False)
                    dimension.Parameter.Expression = '85 mm'

                    dimTextPt = tg.CreatePoint2d(10, 70)
                    dimension = jsr_sketch.DimensionConstraints.AddTwoPointDistance(rect_line_1.StartSketchPoint, rect_line_3.EndSketchPoint, 19202, dimTextPt, False)
                    dimension.Parameter.Expression = '85 mm'

                    dimTextPt = tg.CreatePoint2d(5, 50)
                    dimension = jsr_sketch.DimensionConstraints.AddTwoPointDistance(rect_line_2.EndSketchPoint, rect_line_4.StartSketchPoint, 19201, dimTextPt, False)
                    dimension.Parameter.Expression = '2000 mm'

                    jsr_sketch.Solve()
                    jsr_sketch.UpdateProfiles()
                    jsr_sketch.Profiles.AddForSolid()
                    jsr_sketch.UpdateProfiles()

                    revolve_features = main_assy_def.Features.RevolveFeatures
                    revolve_feature = revolve_features.AddFull(jsr_sketch.Profiles.Item(1), main_y_axis_pg, 20482)

                    inner_shell = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="INNER SHELL")
                    revolve_feature.RemoveParticipant(inner_shell)
                    glass_9100 = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="GL_MBCE-06300-2020")
                    revolve_feature.RemoveParticipant(glass_9100)
                    jacket_shell = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="10Tx2100x") #JACKET SHELL_ NEED TO UPDATE INSTEAD OF 10Tx2100x
                    revolve_feature.RemoveParticipant(jacket_shell)

                    # Jacket Shell ---------------------------------------
                    jacket_shell_sketch = main_assy_def.Sketches.Add(main_xy_plane)

                    jacket_shell_mss = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="JSR-MSS")
                    jacket_shell_mounting_plane = jacket_shell_mss.Definition.WorkPlanes[3]
                    jacket_shell_mounting_plane_proxy = jacket_shell_mss.CreateGeometryProxy(jacket_shell_mounting_plane)
                    jacket_shell_mounting_plane_pg = jacket_shell_sketch.AddByProjectingEntity(jacket_shell_mounting_plane_proxy)
                    jacket_shell_mounting_plane_pg.Construction = True

                    width = 100.0
                    height = 50.0
                    rect_lines = jacket_shell_sketch.SketchLines.AddAsTwoPointRectangle(tg.CreatePoint2d(-width/2, 0), tg.CreatePoint2d(width/2, height))

                    rect_line_1 = rect_lines.Item(1)
                    rect_line_2 = rect_lines.Item(2)
                    rect_line_3 = rect_lines.Item(3)
                    rect_line_4 = rect_lines.Item(4)
                    
                    jacket_shell_collinear1 = jacket_shell_sketch.GeometricConstraints.AddCollinear(main_y_axis_pg, rect_line_2) 
                    jacket_shell_collinear2 = jacket_shell_sketch.GeometricConstraints.AddCollinear(jacket_shell_mounting_plane_pg, rect_line_3) 

                    dimTextPt = tg.CreatePoint2d(10, 70)
                    dimension = jacket_shell_sketch.DimensionConstraints.AddTwoPointDistance(rect_line_1.StartSketchPoint, rect_line_3.EndSketchPoint, 19202, dimTextPt, False)
                    dimension.Parameter.Expression = '85 mm'

                    dimTextPt = tg.CreatePoint2d(5, 50)
                    dimension = jacket_shell_sketch.DimensionConstraints.AddTwoPointDistance(rect_line_2.EndSketchPoint, rect_line_4.StartSketchPoint, 19201, dimTextPt, False)
                    dimension.Parameter.Expression = '2000 mm'

                    jacket_shell_sketch.Solve()
                    jacket_shell_sketch.UpdateProfiles()
                    jacket_shell_sketch.Profiles.AddForSolid()
                    jacket_shell_sketch.UpdateProfiles()

                    revolve_features = main_assy_def.Features.RevolveFeatures
                    revolve_feature = revolve_features.AddFull(jacket_shell_sketch.Profiles.Item(1), main_y_axis_pg, 20482)

                    inner_shell = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="INNER SHELL")
                    revolve_feature.RemoveParticipant(inner_shell)


                    glass_9100 = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="9100")
                    revolve_feature.RemoveParticipant(glass_9100)
                    revolve_feature.RemoveParticipant(jacket_shell_mss)

                    swagged_dish = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="CT-1950")
                    revolve_feature.RemoveParticipant(swagged_dish)

                    logger.info("End: JSR mounting cut")

                elif item.get("component") == 'diaphragmring':
                    logger.info("Start: Diaphragm Ring")
                    diapharm = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    diapharm.Grounded = False

                    btm_jcr = self._get_cached_occurrence("BTM JSR", monoblock.SubOccurrences)
                    self._validate_occurrence(btm_jcr, "BTM JSR")

                    # Bottom JSR Work Axes and Work Planes using helper
                    btm_jcr_proxies = self._get_geometry_proxies(btm_jcr, axes=[AXIS_Y], planes=[PLANE_XY, PLANE_XZ])
                    btm_jcr_y_axis = btm_jcr_proxies[AXIS_Y]
                    btm_jcr_xy_plane = btm_jcr_proxies[PLANE_XY]
                    btm_jcr_xz_plane = btm_jcr_proxies[PLANE_XZ]

                    # Diaphragm Ring Work Axes and Work Planes using helper
                    diapharm_proxies = self._get_geometry_proxies(diapharm, axes=[AXIS_Y], planes=[PLANE_XY, PLANE_XZ])
                    diapharm_y_axis = diapharm_proxies[AXIS_Y]
                    diapharm_xy_plane = diapharm_proxies[PLANE_XY]
                    diapharm_xz_plane = diapharm_proxies[PLANE_XZ]

                    # Constraints for Diaphragm Ring using helper methods
                    diapharm_mate_y = self._add_mate_constraint(main_assy_def, btm_jcr_y_axis, diapharm_y_axis)
                    diapharm_flush_xy = self._add_flush_constraint(main_assy_def, btm_jcr_xy_plane, diapharm_xy_plane)
                    diapharm_flush_xz = self._add_flush_constraint(main_assy_def, diapharm_xz_plane, btm_jcr_xz_plane, "40 mm")     
                    
                    self.hide_workplanes_recursively(occurrence=diapharm)
                    # print("Start Bottom JSR Cut")
                    logger.info("Start: Bottom JSR Cut")
                    jacket_diapharm_ring = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="3616000548 01")

                    jacket_diapharm_ring_xz_plane_proxy = jacket_diapharm_ring.CreateGeometryProxy(jacket_diapharm_ring.Definition.WorkPlanes["XZ Plane"])
                    bottom_jsr_cut_sketch = main_assy_def.Sketches.Add(jacket_diapharm_ring_xz_plane_proxy)

                    jacket_diapharm_ring_center_point = jacket_diapharm_ring.CreateGeometryProxy(jacket_diapharm_ring.Definition.WorkPoints["Center Point"])
                    jacket_diapharm_ring_projected_center = bottom_jsr_cut_sketch.AddByProjectingEntity(jacket_diapharm_ring_center_point)

                    jacket_diapharm_ring_circle = bottom_jsr_cut_sketch.SketchCircles.AddByCenterRadius(jacket_diapharm_ring_projected_center, 27.4)

                    dimTextPoint = tg.CreatePoint2d(jacket_diapharm_ring_circle.CenterSketchPoint.Geometry.X + 50, jacket_diapharm_ring_circle.CenterSketchPoint.Geometry.Y)
                    # Add diameter dimension (not driven by default, so it drives the size)
                    diameter_dimension = bottom_jsr_cut_sketch.DimensionConstraints.AddDiameter(jacket_diapharm_ring_circle, dimTextPoint)
                    diameter_dimension.Parameter.Expression = '548 mm'
                    bottom_jsr_cut_sketch.GeometricConstraints.AddCoincident(jacket_diapharm_ring_projected_center, jacket_diapharm_ring_circle.CenterSketchPoint)

                    # Extrude Operation
                    bottom_jsr_cut_sketch.Solve()
                    bottom_jsr_cut_sketch.UpdateProfiles()
                    bottom_jsr_cut_sketch.Profiles.AddForSolid()
                    bottom_jsr_cut_sketch.UpdateProfiles()
                    cut_sketch_profile = bottom_jsr_cut_sketch.Profiles.Item(1)

                    extrude_features  = main_assy_def.Features.ExtrudeFeatures
                    extrude_def = extrude_features.CreateExtrudeDefinition(cut_sketch_profile, 20482)
                    extrude_def.SetDistanceExtent(150, 20994)
                    extrude = extrude_features.Add(extrude_def)

                    comp_9100_Glass = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="9100 GLASS")
                    _3701CEQB0412 = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="3701CEQB0412")
                    extrude.RemoveParticipant(jacket_diapharm_ring)
                    extrude.RemoveParticipant(comp_9100_Glass)
                    extrude.RemoveParticipant(_3701CEQB0412)
                    logger.info("End: Bottom JSR Cut")
                    
                    # print("End diapharmring")
                    logger.info("End: Diapharmring")

                elif item.get("component") == 'sidebracket':
                    # print("Start sidebracket")
                    logger.info("Start: Sidebracket")
                    sidebracket = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    sidebracket.Grounded = False

                    # Jacket Work Axes and Work Planes
                    jacket_y_axis = jacket.CreateGeometryProxy(jacket.Definition.WorkAxes["Y Axis"])
                    jacket_xy_plane = jacket.CreateGeometryProxy(jacket.Definition.WorkPlanes["XY Plane"])

                    initial = main_assy_def.Occurrences[0]
                    ref_occ = initial.Definition.Occurrences[0]  # Inside monoblock
                    # Get "REF LINE" from the ref_occ (this is still in its own context)
                    ref_workplane_local = ref_occ.Definition.WorkPlanes["REF LINE"]
                    # Step 2: Promote to monoblock-level assembly context
                    ref_plane_proxy_lvl1 = ref_occ.CreateGeometryProxy(ref_workplane_local)
                    # Step 3: Promote to main assembly context
                    ref_plane_proxy_top = initial.CreateGeometryProxy(ref_plane_proxy_lvl1)


                    # Side Bracket Work Axes and Work Planes
                    sidebracket_proxies = self._get_geometry_proxies(sidebracket, axes=[AXIS_Y], planes=[PLANE_XY, PLANE_XZ])
                    sidebracket_y_axis = sidebracket_proxies.get(AXIS_Y)
                    sidebracket_xy_plane = sidebracket_proxies.get(PLANE_XY)
                    sidebracket_xz_plane = sidebracket_proxies.get(PLANE_XZ)

                    # Constraints for Side Bracket
                    sidebracket_mate_y = self._add_mate_constraint(main_assy_def, jacket_y_axis, sidebracket_y_axis)
                    # sidebracket_flush_xy = main_assy_def.Constraints.AddFlushConstraint(jacket_xy_plane, sidebracket_xy_plane, 0, None, None)
                    sidebracket_angle_xy = main_assy_def.Constraints.AddAngleConstraint(jacket_xy_plane, sidebracket_xy_plane, 0, 78593, None, None, None)
                    sidebracket_flush_xz = main_assy_def.Constraints.AddFlushConstraint(sidebracket_xz_plane, ref_plane_proxy_top, "535 mm", None, None)

                    self.hide_workplanes_recursively(occurrence=sidebracket)
                    # Adding 4 side bracket at 90.0 degree with corresponds to Y-axis
                    pattern_axis = monoblock.CreateGeometryProxy(monoblock.Definition.WorkAxes[AXIS_Y])
                    self._create_circular_pattern(main_assy_def, [sidebracket], pattern_axis, SIDE_BRACKET_COUNT, SIDE_BRACKET_ANGLE)
                    
                    # print("End sidebracket")
                    logger.info("End: Sidebracket")

                elif item.get("component") == 'jacketnozzle_n16_shell':
                    # ---------------------------------------------------- First Jacket Nozzle at Top (Shell) Start ------------------------------------------
                    # NOTE: This block processes BOTH N16 and N15 shell nozzles in sequence
                    # Get N16 angle from item data if available, otherwise use default
                    n16_degree = item.get("nozzle_degree", "28")
                    n16_angle = -float(n16_degree)  # Negative for Inventor plane orientation

                    logger.info(f"Start: First Jacket Nozzle at Top (Shell) - N16 at {n16_degree} degrees")

                    # Create angled work plane for N16 nozzle (dynamic degree)
                    shell_nozzle1_angled_plane = self._create_angled_plane(tg, main_assy_def, n16_angle, "N16_Plane")

                    # Add Sketch
                    shell_jacket_nozzle1_sketch = main_assy_def.Sketches.Add(shell_nozzle1_angled_plane)

                    # Add Y-axis project geometry
                    main_y_axis = main_assy_def.WorkAxes["Y Axis"]
                    yaxis_pg = shell_jacket_nozzle1_sketch.AddByProjectingEntity(main_y_axis)

                    L_nozzle_occ = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="L_DN150")

                    width = 10.0
                    height = 5.0
                    # Create 2D corner points in sketch space
                    bottom_left_pt = shell_jacket_nozzle1_sketch.ModelToSketchSpace(tg.CreatePoint(-width/2, 0, 0))  # Bottom-left
                    top_right_pt = shell_jacket_nozzle1_sketch.ModelToSketchSpace(tg.CreatePoint(width/2, height, 0))  # Top-right

                    # Add rectangle
                    rect_lines = shell_jacket_nozzle1_sketch.SketchLines.AddAsTwoPointRectangle(bottom_left_pt, top_right_pt)

                    # Get bottom line (first item)
                    bottom_line = rect_lines.Item(1)
                    bottom_line.Centerline = True
                                    
                    # Get the XZ plane of L_nozzle_occ
                    L_nozzle_xz_plane = L_nozzle_occ.Definition.WorkPlanes["XZ Plane"]
                    L_nozzle_xz_plane_proxy = L_nozzle_occ.CreateGeometryProxy(L_nozzle_xz_plane)

                    # Project XZ plane into the sketch
                    proj_line = shell_jacket_nozzle1_sketch.AddByProjectingEntity(L_nozzle_xz_plane_proxy)

                    # Ensure the projected line is valid
                    if not hasattr(proj_line, "StartSketchPoint"):
                        raise Exception("Projected XZ plane did not return a SketchLine.")

                    # Get points from bottom line and projected line
                    bottom_line_start_pt1 = bottom_line.StartSketchPoint
                    project_line_start_pt2 = proj_line.StartSketchPoint

                    # Validate points
                    if bottom_line_start_pt1 is None or project_line_start_pt2 is None:
                        raise Exception("One or both SketchPoints are None.")

                    # Create a text point for dimension label (optional but required by API)
                    # Use midpoint between pt1 and pt2 as a reasonable label position
                    mid_x = (bottom_line_start_pt1.Geometry.X + project_line_start_pt2.Geometry.X) / 2
                    mid_y = (bottom_line_start_pt1.Geometry.Y + project_line_start_pt2.Geometry.Y) / 2
                    text_point = inv_app.TransientGeometry.CreatePoint2d(mid_x, mid_y)

                    # Add vertical dimension constraint
                    dim_constraints = shell_jacket_nozzle1_sketch.DimensionConstraints
                    dimension = dim_constraints.AddTwoPointDistance(bottom_line_start_pt1, project_line_start_pt2, 19202, text_point, False)

                    # Set the distance value (assuming mm)
                    dimension.Parameter.Expression = '2350 mm'

                    second_line = rect_lines.Item(2)  

                    # Add collinear constraint
                    geo_constraints = shell_jacket_nozzle1_sketch.GeometricConstraints
                    geo_constraints.AddCollinear(yaxis_pg, second_line)

                    # Get second and fourth lines of the rectangle
                    fourth_line = rect_lines.Item(4)  # Likely the right vertical edge

                    # Get sketch points from each line
                    second_line_start_pt1 = second_line.StartSketchPoint
                    fourth_line_start_pt2 = fourth_line.StartSketchPoint

                    # Validate points
                    if second_line_start_pt1 is None or fourth_line_start_pt2 is None:
                        raise Exception("One or both sketch points are None.")

                    # Compute midpoint for dimension text placement
                    mid_x = (second_line_start_pt1.Geometry.X + fourth_line_start_pt2.Geometry.X) / 2
                    mid_y = (second_line_start_pt1.Geometry.Y + fourth_line_start_pt2.Geometry.Y) / 2
                    text_point = inv_app.TransientGeometry.CreatePoint2d(mid_x, mid_y)

                    # Add horizontal dimension constraint
                    dim_constraints = shell_jacket_nozzle1_sketch.DimensionConstraints
                    horizontal_dim = dim_constraints.AddTwoPointDistance(second_line_start_pt1, fourth_line_start_pt2, 19203, text_point, False)

                    # Set the dimension to the actual rectangle width (10.0 mm)
                    horizontal_dim.Parameter.Expression = "5000 mm"

                    # Get first and third lines of the rectangle
                    first_line = rect_lines.Item(1)   # Bottom edge
                    third_line = rect_lines.Item(3)   # Top edge

                    # Get sketch points (use start point for consistency)
                    first_line_start_pt1 = first_line.StartSketchPoint
                    third_line_start_pt2 = third_line.StartSketchPoint

                    # Validate points
                    if first_line_start_pt1 is None or third_line_start_pt2 is None:
                        raise Exception("One or both sketch points are None.")

                    # Compute midpoint for dimension text
                    mid_x = (first_line_start_pt1.Geometry.X + third_line_start_pt2.Geometry.X) / 2
                    mid_y = (first_line_start_pt1.Geometry.Y + third_line_start_pt2.Geometry.Y) / 2
                    text_point = inv_app.TransientGeometry.CreatePoint2d(mid_x, mid_y)

                    # Add vertical dimension
                    vertical_dim = shell_jacket_nozzle1_sketch.DimensionConstraints.AddTwoPointDistance(first_line_start_pt1, third_line_start_pt2, 19202, text_point, False)

                    # Set the value (height of the rectangle)
                    vertical_dim.Parameter.Expression = "45 mm"

                    # Solve the sketch: Needs to update profile after adding for solid.
                    shell_jacket_nozzle1_sketch.Solve()
                    shell_jacket_nozzle1_sketch.UpdateProfiles()
                    shell_jacket_nozzle1_sketch.Profiles.AddForSolid()
                    shell_jacket_nozzle1_sketch.UpdateProfiles()

                    # === Step 1: Get the profile from the sketch ===
                    profile = shell_jacket_nozzle1_sketch.Profiles.Item(1)  # Assumes rectangle forms a closed profile

                    # === Step 2: Get the axis (centerline) ===
                    axis_line = bottom_line  # Bottom line marked as Centerline earlier

                    # === Step 3: Access the part definition (not assembly) ===
                    # This must be run inside a part document, not an assembly
                    # For example, if you're in jacketnozzle component part:
                    part_def = inv_app.ActiveDocument.ComponentDefinition  # Must be a PartDocument

                    # === Step 4: Revolve the sketch using AddFull ===
                    revolve_features = part_def.Features.RevolveFeatures
                    revolve_feature = revolve_features.AddFull(profile, axis_line, 20482)

                    # Remove participants - components or occurrences
                    # 1) Remove Inner shell
                    inner_shell = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="INNER SHELL")
                    revolve_feature.RemoveParticipant(inner_shell)
                    # 2) Remove 9100 glass 
                    glass_9100 = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="9100")
                    revolve_feature.RemoveParticipant(glass_9100)

                    # Adding Axis
                    cylinder = revolve_feature.Faces.Item(1).Geometry  # Should be a cylinder
                    base_pt = cylinder.BasePoint
                    axis_vec = cylinder.AxisVector
                    work_axis = main_assy_def.WorkAxes.AddFixed(base_pt, axis_vec, False)
                    work_axis.Name = "N16_Axis"
                    work_axis.Grounded = True

                    shell_jacket_nozzle1 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    shell_jacket_nozzle1.Grounded = False

                    # Create a transform matrix (identity to start)
                    transform = tg.CreateMatrix()
                    translation_vector = tg.CreateVector(base_pt.X, base_pt.Y, base_pt.Z)
                    transform.SetTranslation(translation_vector)
                    shell_jacket_nozzle1.Transformation = transform

                    # Attach Jacket Nozzle with Jacket
                    shell_jacket_nozzle1_y_axis = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkAxes["Y Axis"])
                    shell_jacket_nozzle1_xy_plane = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkPlanes["XY Plane"])
                    shell_jacket_jacket_nozzle1_xz_plane = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkPlanes["XZ Plane"])

                    self.hide_workplanes_recursively(occurrence=shell_jacket_nozzle1)

                    main_N16_Plane = main_assy_def.WorkPlanes['N16_Plane']
                    main_N16_Axis = main_assy_def.WorkAxes["N16_Axis"]
                    jacket_shell = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="10Tx2100x")
                    jacket_shell_face = jacket_shell.Definition.SurfaceBodies[0].Faces[0]
                    shell_face_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_face)

                    # Adding Constraints
                    jacket_nozzle_flush = self._add_flush_constraint(main_assy_def, main_N16_Plane, shell_jacket_nozzle1_xy_plane)
                    jacket_nozzle_mate_y = self._add_mate_constraint(main_assy_def, main_N16_Axis, shell_jacket_nozzle1_y_axis)
                    jacket_nozzle_tangent = main_assy_def.Constraints.AddTangentConstraint(shell_jacket_jacket_nozzle1_xz_plane, shell_face_proxy, False, "140 mm")


                    # Start cut operation on first jacket nozzle:
                    yz_plane = shell_jacket_nozzle1.Definition.WorkPlanes["YZ Plane"]
                    yz_plane_proxy = shell_jacket_nozzle1.CreateGeometryProxy(yz_plane)
                    first_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(yz_plane_proxy)

                    # jacket_shell_edge = jacket_shell.Definition.SurfaceBodies[0].Edges.Item(7) # Instead of this draw circle of 2080.
                    jacket_comp = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="95-JKT-6699")
                    center_point_pg = jacket_comp.CreateGeometryProxy(jacket_comp.Definition.WorkPoints["Center Point"])
                    projected_center = first_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(center_point_pg)
                    ID_circle = first_jacket_nozzle_length_cut_sketch.SketchCircles.AddByCenterRadius(projected_center, 104.0)
                    ID_circle.Construction = True
                    dimTextPoint = tg.CreatePoint2d(ID_circle.CenterSketchPoint.Geometry.X + 50, ID_circle.CenterSketchPoint.Geometry.Y)
                    # Add diameter dimension (not driven by default, so it drives the size)
                    diameter_dimension = first_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddDiameter(ID_circle, dimTextPoint)
                    diameter_dimension.Parameter.Expression = '2080 mm'
                    first_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(projected_center, ID_circle.CenterSketchPoint)

                    # jacket_shell_edge_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_edge)
                    # jacket_shell_edge_pg = first_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(jacket_shell_edge_proxy)

                    shell_jacket_nozzle1_y_axis = shell_jacket_nozzle1.Definition.WorkAxes["Y Axis"]
                    shell_jacket_nozzle1_y_axis_proxy = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1_y_axis)
                    shell_jacket_nozzle1_y_axis_pg = first_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(shell_jacket_nozzle1_y_axis_proxy)
                    shell_jacket_nozzle1_y_axis_pg.CenterLine = True

                    # # 8. Create 2D point at that location
                    pt2d = tg.CreatePoint2d(0.0, 0.0)

                    # 9. Add the sketch point
                    skpt = first_jacket_nozzle_length_cut_sketch.SketchPoints.Add(pt2d, False)

                    width = 5.0
                    height = 15.0

                    # Place rectangle starting at Y-axis (X = 0), going right
                    pt1 = first_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(0.0, 0.0, 0.0))  # Bottom-left corner on Y-axis
                    pt2 = first_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(width, height, 0.0))  # Top-right corner to the right

                    # Add rectangle
                    first_jacket_nozzle_length_cut_rectangle = first_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)
                    fourth_line_end_pt = first_jacket_nozzle_length_cut_rectangle.Item(3).EndSketchPoint
                    first_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddHorizontalAlign(fourth_line_end_pt, skpt)

                    mid_x = (fourth_line_end_pt.Geometry.X + skpt.Geometry.X) / 2
                    mid_y = (fourth_line_end_pt.Geometry.Y + skpt.Geometry.Y) / 2
                    text_point = tg.CreatePoint2d(mid_x, mid_y)
                    first_jacket_nozzle_length_cut_dim_constraints = first_jacket_nozzle_length_cut_sketch.DimensionConstraints
                    aligned_dim = first_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_end_pt, skpt, 19203, text_point, False)
                    aligned_dim.Parameter.Expression = '2 mm'
                    first_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(skpt, ID_circle)

                    fourth_line_start_pt = first_jacket_nozzle_length_cut_rectangle.Item(3).StartSketchPoint
                    mid_x = (fourth_line_start_pt.Geometry.X + fourth_line_end_pt.Geometry.X) / 2
                    mid_y = (fourth_line_start_pt.Geometry.Y + fourth_line_end_pt.Geometry.Y) / 2
                    text_point = tg.CreatePoint2d(mid_x, mid_y)
                    aligned_dim = first_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_start_pt, fourth_line_end_pt, 19203, text_point, False)
                    aligned_dim.Parameter.Expression = '150 mm'

                    second_line_start_pt = first_jacket_nozzle_length_cut_rectangle.Item(2).StartSketchPoint
                    second_line_end_pt = first_jacket_nozzle_length_cut_rectangle.Item(2).EndSketchPoint
                    mid_x = (second_line_start_pt.Geometry.X + second_line_end_pt.Geometry.X) / 2
                    mid_y = (second_line_start_pt.Geometry.Y + second_line_end_pt.Geometry.Y) / 2
                    text_point = tg.CreatePoint2d(mid_x, mid_y)

                    aligned_dim = first_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(second_line_start_pt, second_line_end_pt, 19203, text_point, False)
                    aligned_dim.Parameter.Expression = '50 mm'

                    forth_line = first_jacket_nozzle_length_cut_rectangle.Item(3)
                    geo_const = first_jacket_nozzle_length_cut_sketch.GeometricConstraints
                    geo_const.AddCollinear(shell_jacket_nozzle1_y_axis_pg, forth_line, True, True)

                    first_jacket_nozzle_length_cut_sketch.Solve()
                    first_jacket_nozzle_length_cut_sketch.UpdateProfiles()
                    first_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
                    first_jacket_nozzle_length_cut_sketch.UpdateProfiles()
                    cut_sketch_profile = first_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

                    part_def = inv_app.ActiveDocument.ComponentDefinition

                    cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
                    cut_sketch_revolve_feature = cut_sketch_revolve_feats.AddFull(cut_sketch_profile, shell_jacket_nozzle1_y_axis_pg, 20482)

                    # Remove participants again
                    cut_sketch_revolve_feature.RemoveParticipant(inner_shell)
                    cut_sketch_revolve_feature.RemoveParticipant(glass_9100)

                    # print("First Jacket Nozzle at Top (Shell) Finish")
                    logger.info("End: First Jacket Nozzle at Top (Shell)")
                    # ------------------------------ First Jacket Nozzle at Top (Shell) Finish ------------------------------------------------------------


                    # ------------------------------ Second Jacket Nozzle at Top (Shell) Start ------------------------------------------------------------
                    # print("Second Jacket Nozzle at Top (Shell) Start")
                    logger.info("Start: Second Jacket Nozzle at Top (Shell)")

                    # Create angled work plane for N15 nozzle
                    shell_nozzle2_angled_plane = self._create_angled_plane(tg, main_assy_def, NOZZLE_N15_ANGLE, "N15_Plane")

                    # Add sketch on second plane
                    shell_jacket_nozzle2_sketch = main_assy_def.Sketches.Add(shell_nozzle2_angled_plane)

                    # Project Y-axis
                    yaxis_pg_2 = shell_jacket_nozzle2_sketch.AddByProjectingEntity(main_y_axis)

                    # Define rectangle dimensions
                    width = 500.0
                    height = 5.0

                    # Place rectangle starting at Y-axis (X = 0), going right
                    pt1 = shell_jacket_nozzle2_sketch.ModelToSketchSpace(tg.CreatePoint(0.0, 0.0, 0.0))  # Bottom-left corner on Y-axis
                    pt2 = shell_jacket_nozzle2_sketch.ModelToSketchSpace(tg.CreatePoint(width, height, 0.0))  # Top-right corner to the right

                    # Add rectangle
                    second_rect_lines = shell_jacket_nozzle2_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)

                    # Set centerline
                    second_bottom_line = second_rect_lines.Item(1)
                    second_bottom_line.Centerline = True

                    # Get L_DN150 again
                    xz_plane = L_nozzle_occ.Definition.WorkPlanes["XZ Plane"]
                    xz_plane_proxy = L_nozzle_occ.CreateGeometryProxy(xz_plane)

                    # Project and dimension
                    proj_line_2 = shell_jacket_nozzle2_sketch.AddByProjectingEntity(xz_plane_proxy)

                    # Dimension from proj_line to bottom_line
                    second_bottom_line_start_pt1 = second_bottom_line.StartSketchPoint
                    second_project_line_start_pt2 = proj_line_2.StartSketchPoint
                    mid_x = (second_bottom_line_start_pt1.Geometry.X + second_project_line_start_pt2.Geometry.X) / 2
                    mid_y = (second_bottom_line_start_pt1.Geometry.Y + second_project_line_start_pt2.Geometry.Y) / 2
                    text_point = tg.CreatePoint2d(mid_x, mid_y)

                    second_dim_constraints = shell_jacket_nozzle2_sketch.DimensionConstraints
                    vertical_dim = second_dim_constraints.AddTwoPointDistance(second_bottom_line_start_pt1, second_project_line_start_pt2, 19202, text_point, False)
                    vertical_dim.Parameter.Expression = '2350 mm'


                    # Height
                    first_line = second_rect_lines.Item(1)
                    third_line = second_rect_lines.Item(3)
                    pt1 = first_line.StartSketchPoint
                    pt2 = third_line.StartSketchPoint
                    mid_x = (pt1.Geometry.X + pt2.Geometry.X) / 2
                    mid_y = (pt1.Geometry.Y + pt2.Geometry.Y) / 2
                    text_point = tg.CreatePoint2d(mid_x, mid_y)
                    vertical_dim2 = second_dim_constraints.AddTwoPointDistance(pt1, pt2, 19202, text_point, False)
                    vertical_dim2.Parameter.Expression = "45 mm"

                    # Solve and revolve
                    shell_jacket_nozzle2_sketch.Solve()
                    shell_jacket_nozzle2_sketch.UpdateProfiles()
                    shell_jacket_nozzle2_sketch.Profiles.AddForSolid()
                    shell_jacket_nozzle2_sketch.UpdateProfiles()
                    profile_2 = shell_jacket_nozzle2_sketch.Profiles.Item(1)

                    axis_line_2 = second_bottom_line
                    revolve_feats = part_def.Features.RevolveFeatures
                    revolve_feature_2 = revolve_feats.AddFull(profile_2, axis_line_2, 20482)

                    # Remove participants again
                    revolve_feature_2.RemoveParticipant(inner_shell)
                    revolve_feature_2.RemoveParticipant(glass_9100)

                    # Add second axis
                    cylinder_2 = revolve_feature_2.Faces.Item(1).Geometry
                    base_pt_2 = cylinder_2.BasePoint
                    axis_vec_2 = cylinder_2.AxisVector
                    axis_2 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
                    axis_2.Name = "N15_Axis"
                    axis_2.Grounded = True

                    # Add second nozzle component
                    shell_jacket_nozzle2 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    shell_jacket_nozzle2.Grounded = False

                    # Set position
                    transform_2 = tg.CreateMatrix()
                    transform_2.SetTranslation(tg.CreateVector(base_pt_2.X, base_pt_2.Y, base_pt_2.Z))
                    shell_jacket_nozzle2.Transformation = transform_2

                    # Get proxies
                    nozzle2_proxies = self._get_geometry_proxies(shell_jacket_nozzle2, axes=[AXIS_Y], planes=[PLANE_XY, PLANE_XZ])
                    y_axis_2 = nozzle2_proxies.get(AXIS_Y)
                    xy_plane_2 = nozzle2_proxies.get(PLANE_XY)
                    xz_plane_2 = nozzle2_proxies.get(PLANE_XZ)
                    shell_face_proxy_2 = jacket_shell.CreateGeometryProxy(jacket_shell_face)

                    # Add constraints
                    flush_2 = self._add_flush_constraint(main_assy_def, shell_nozzle2_angled_plane, xy_plane_2)
                    mate_y_2 = self._add_mate_constraint(main_assy_def, axis_2, y_axis_2)
                    tangent_2 = main_assy_def.Constraints.AddTangentConstraint(xz_plane_2, shell_face_proxy_2, False, "140 mm")

                    self.hide_workplanes_recursively(occurrence=shell_jacket_nozzle2)

                    # Start cut revolve operation on first jacket nozzle:
                    yz_plane = shell_jacket_nozzle2.Definition.WorkPlanes["YZ Plane"]
                    yz_plane_proxy = shell_jacket_nozzle2.CreateGeometryProxy(yz_plane)
                    second_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(yz_plane_proxy)

                    # jacket_shell_edge = jacket_shell.Definition.SurfaceBodies[0].Edges.Item(7) # 
                    jacket_comp = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="95-JKT-6699")
                    center_point_pg = jacket_comp.CreateGeometryProxy(jacket_comp.Definition.WorkPoints["Center Point"])
                    projected_center = second_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(center_point_pg)
                    
                    ID_circle_2 = second_jacket_nozzle_length_cut_sketch.SketchCircles.AddByCenterRadius(projected_center, 104.0)
                    ID_circle_2.Construction = True

                    dimTextPoint = tg.CreatePoint2d(ID_circle_2.CenterSketchPoint.Geometry.X + 50, ID_circle_2.CenterSketchPoint.Geometry.Y)
                    diameter_dimension = second_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddDiameter(ID_circle_2, dimTextPoint)
                    diameter_dimension.Parameter.Expression = '2080 mm'
                    second_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(projected_center, ID_circle_2.CenterSketchPoint)

                    # jacket_shell_edge_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_edge)
                    # jacket_shell_edge_pg = second_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(jacket_shell_edge_proxy)

                    shell_jacket_nozzle2_y_axis = shell_jacket_nozzle2.Definition.WorkAxes["Y Axis"]
                    shell_jacket_nozzle2_y_axis_proxy = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2_y_axis)
                    shell_jacket_nozzle2_y_axis_pg = second_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(shell_jacket_nozzle2_y_axis_proxy)
                    shell_jacket_nozzle2_y_axis_pg.CenterLine = True

                    # # 8. Create 2D point at that location
                    pt2d = tg.CreatePoint2d(0.0, 0.0)

                    # 9. Add the sketch point
                    skpt = second_jacket_nozzle_length_cut_sketch.SketchPoints.Add(pt2d, False)

                    width = 5.0
                    height = 15.0

                    # Place rectangle starting at Y-axis (X = 0), going right
                    pt1 = second_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(0.0, 0.0, 0.0))  # Bottom-left corner on Y-axis
                    pt2 = second_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(width, height, 0.0))  # Top-right corner to the right

                    # Add rectangle
                    second_jacket_nozzle_length_cut_rectangle = second_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)
                    fourth_line_end_pt = second_jacket_nozzle_length_cut_rectangle.Item(3).EndSketchPoint
                    second_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddHorizontalAlign(fourth_line_end_pt, skpt)
                    
                    mid_x = (fourth_line_end_pt.Geometry.X + skpt.Geometry.X) / 2
                    mid_y = (fourth_line_end_pt.Geometry.Y + skpt.Geometry.Y) / 2
                    text_point = tg.CreatePoint2d(mid_x, mid_y)
                    second_jacket_nozzle_length_cut_dim_constraints = second_jacket_nozzle_length_cut_sketch.DimensionConstraints
                    aligned_dim = second_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_end_pt, skpt, 19203, text_point, False)
                    aligned_dim.Parameter.Expression = '2 mm'
                    second_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(skpt, ID_circle_2)

                    fourth_line_start_pt = second_jacket_nozzle_length_cut_rectangle.Item(3).StartSketchPoint
                    mid_x = (fourth_line_start_pt.Geometry.X + fourth_line_end_pt.Geometry.X) / 2
                    mid_y = (fourth_line_start_pt.Geometry.Y + fourth_line_end_pt.Geometry.Y) / 2
                    text_point = tg.CreatePoint2d(mid_x, mid_y)
                    aligned_dim = second_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_start_pt, fourth_line_end_pt, 19203, text_point, False)
                    aligned_dim.Parameter.Expression = '150 mm'

                    second_line_start_pt = second_jacket_nozzle_length_cut_rectangle.Item(2).StartSketchPoint
                    second_line_end_pt = second_jacket_nozzle_length_cut_rectangle.Item(2).EndSketchPoint
                    mid_x = (second_line_start_pt.Geometry.X + second_line_end_pt.Geometry.X) / 2
                    mid_y = (second_line_start_pt.Geometry.Y + second_line_end_pt.Geometry.Y) / 2
                    text_point = tg.CreatePoint2d(mid_x, mid_y)

                    aligned_dim = second_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(second_line_start_pt, second_line_end_pt, 19203, text_point, False)
                    aligned_dim.Parameter.Expression = '50 mm'

                    forth_line = second_jacket_nozzle_length_cut_rectangle.Item(3)
                    geo_const = second_jacket_nozzle_length_cut_sketch.GeometricConstraints
                    geo_const.AddCollinear(shell_jacket_nozzle2_y_axis_pg, forth_line, True, True)

                    second_jacket_nozzle_length_cut_sketch.Solve()
                    second_jacket_nozzle_length_cut_sketch.UpdateProfiles()
                    second_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
                    second_jacket_nozzle_length_cut_sketch.UpdateProfiles()
                    cut_sketch_profile = second_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

                    part_def = inv_app.ActiveDocument.ComponentDefinition

                    cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
                    cut_sketch_revolve_feature = cut_sketch_revolve_feats.AddFull(cut_sketch_profile, shell_jacket_nozzle2_y_axis_pg, 20482)

                    # Remove participants again
                    cut_sketch_revolve_feature.RemoveParticipant(inner_shell)
                    cut_sketch_revolve_feature.RemoveParticipant(glass_9100)


                    # print("Second Jacket Nozzle at Top (Shell) Finish")
                    logger.info("End: Second Jacket Nozzle at Top (Shell)")
                    # ------------------------------ Second Jacket Nozzle at Top (Shell) Finish ------------------------------------------------------------

                elif item.get("component") == 'jacketnozzle_n17_btm':
                    # NOTE: This block processes BOTH N11 and N17 bottom nozzles in sequence
                    # N11 is processed first, N17 is processed second
                    # The item contains N17's data, so use default constant for N11
                    logger.info("Start: jacketnozzle_n17_btm")
                    # ------------------------------ Third Jacket Nozzle at Bottom Start ------------------------------------------------------------
                    logger.info("Start: Third Jacket Nozzle at Bottom (N11)")

                    # Create angled work plane for N11 nozzle (uses default constant since item is for N17)
                    bottom_nozzle1_angled_plane = self._create_angled_plane(tg, main_assy_def, NOZZLE_N11_ANGLE, "N11_Plane")

                    bottom_jacket_nozzle3_sketch = main_assy_def.Sketches.Add(main_assy_def.WorkPlanes["XZ Plane"])
                    originPoint = main_assy_def.WorkPoints["Center Point"]  # Usually the origin work point
                    projectedCenter = bottom_jacket_nozzle3_sketch.AddByProjectingEntity(originPoint)
                    originSketchPoint  = bottom_jacket_nozzle3_sketch.SketchPoints.Item(1)
                    startPt = tg.CreatePoint2d(0, 0)
                    endPt = tg.CreatePoint2d(37, 0)  # 370 mm in cm (as Inventor usually uses cm internally)

                    line1 = bottom_jacket_nozzle3_sketch.SketchLines.AddByTwoPoints(startPt, endPt)
                    line1.Construction = True
                    horizontal_line1 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddHorizontal(line1)
                    coincident0 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(line1.StartSketchPoint, projectedCenter)


                    dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
                    line_1_dimension = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddTwoPointDistance(line1.StartSketchPoint, line1.EndSketchPoint, 19201, dimTextPt1)
                    line_1_dimension.Parameter.Expression = '370 mm'

                    endPt2 = tg.CreatePoint2d(0, -37)  # 370 mm along Y
                    line2 = bottom_jacket_nozzle3_sketch.SketchLines.AddByTwoPoints(startPt, endPt2)
                    line2.Construction = True

                    circle_center_point = line2.EndSketchPoint
                    center2d = circle_center_point.Geometry
                    circle = bottom_jacket_nozzle3_sketch.SketchCircles.AddByCenterRadius(center2d, 4.6)

                    dimTextPt2 = tg.CreatePoint2d(-10, 10)  # Text placement
                    line_2_dimension = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddTwoPointDistance(line2.StartSketchPoint, line2.EndSketchPoint, 19203, dimTextPt2)
                    line_2_dimension.Parameter.Expression = '370 mm'
                    # vertical_constraint = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddVertical(line2)

                    dimTextPoint = tg.CreatePoint2d(circle.CenterSketchPoint.Geometry.X + 50, circle.CenterSketchPoint.Geometry.Y)
                    # Add diameter dimension (not driven by default, so it drives the size)
                    diameter_dimension = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddDiameter(circle, dimTextPoint)
                    # Optionally, set the diameter value explicitly, e.g. 92 mm
                    diameter_dimension.Parameter.Expression = '92 mm'
                    
                    textPoint = tg.CreatePoint2d(10, -10)  # position of dimension text
                    angleDim = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddTwoLineAngle(line1, line2, textPoint)
                    angleDim.Parameter.Expression = "90.0 deg"
                    
                    circle_center = circle.CenterSketchPoint    # The SketchPoint at the center of the circle
                    line_endpoint = line2.EndSketchPoint

                    # coincident1 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(line2.StartSketchPoint, projectedCenter)
                    line2.StartSketchPoint.Merge(projectedCenter)
                    coincident_circle = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(circle_center, line_endpoint)
                    
                    bottom_jacket_nozzle3_sketch.Solve()
                    bottom_jacket_nozzle3_sketch.UpdateProfiles()
                    bottom_jacket_nozzle3_sketch.Profiles.AddForSolid()
                    bottom_jacket_nozzle3_sketch.UpdateProfiles()

                    extrude_features  = part_def.Features.ExtrudeFeatures
                    extrude_def = extrude_features.CreateExtrudeDefinition(bottom_jacket_nozzle3_sketch.Profiles[0], 20482)
                    extrude_def.SetDistanceExtent(150, 20994)
                    extrude = extrude_features.Add(extrude_def)

                    extrude_3_n11 = extrude.Faces.Item(1).Geometry
                    base_pt_2 = extrude_3_n11.BasePoint
                    axis_vec_2 = extrude_3_n11.AxisVector
                    axis_3 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
                    axis_3.Name = "N11_Axis"
                    axis_3.Grounded = True

                    # Add second nozzle component
                    jacketnozzle_3 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    jacketnozzle_3.Grounded = False

                    L_occ = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="L_DN150")
                    xz_plane = L_occ.Definition.WorkPlanes["XZ Plane"]
                    xz_plane_proxy = L_occ.CreateGeometryProxy(xz_plane)

                    # Set position
                    transform_3 = tg.CreateMatrix()
                    transform_3.SetTranslation(tg.CreateVector(base_pt_2.X, base_pt_2.Y, base_pt_2.Z))
                    jacketnozzle_3.Transformation = transform_3

                    # Get proxies
                    nozzle3_proxies = self._get_geometry_proxies(jacketnozzle_3, axes=[AXIS_Y], planes=[PLANE_XY, PLANE_XZ])
                    y_axis_3 = nozzle3_proxies.get(AXIS_Y)
                    xy_plane_3 = nozzle3_proxies.get(PLANE_XY)
                    xz_plane_3 = nozzle3_proxies.get(PLANE_XZ)

                    self.hide_workplanes_recursively(occurrence=jacketnozzle_3)

                    # Add constraints
                    flush_3 = self._add_flush_constraint(main_assy_def, bottom_nozzle1_angled_plane, xy_plane_3)
                    mate_y_3 = self._add_mate_constraint(main_assy_def, axis_3, y_axis_3)
                    mate_xz_3 = self._add_mate_constraint(main_assy_def, xz_plane_3, xz_plane_proxy, "90 mm")

                    # Start cut revolve operation on first jacket nozzle:

                    # xz_plane_nozzle_3 = jacketnozzle_3.Definition.WorkPlanes["XY Plane"]
                    # bottom_nozzle1_angled_plane_proxy = jacketnozzle_3.CreateGeometryProxy(bottom_nozzle1_angled_plane)
                    third_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(bottom_nozzle1_angled_plane)
                    
                    bottom_jacket_nozzle3_y_axis = jacketnozzle_3.Definition.WorkAxes["Y Axis"]
                    bottom_jacket_nozzle3_y_axis_proxy = jacketnozzle_3.CreateGeometryProxy(bottom_jacket_nozzle3_y_axis)
                    bottom_jacket_nozzle3_y_axis_pg = third_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_jacket_nozzle3_y_axis_proxy)
                    bottom_jacket_nozzle3_y_axis_pg.CenterLine = True
                    
                    bottom_swg_dish = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="BTM-1950")
                    bottom_swg_dish_center_point = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkPoints["Center Point"])
                    bottom_swg_dish_center_proj = third_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_center_point)

                    bottom_swg_dish_y_axis = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkAxes["Y Axis"])
                    

                    bottom_swg_dish_y_axis_proj = third_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_y_axis)
                    bottom_swg_dish_y_axis_proj_start_pt = bottom_swg_dish_y_axis_proj.StartSketchPoint
                    # bottom_swg_dish_y_axis_proj.CenterLine = True

                    # Draw Circle
                    # center2d_point = tg.CreatePoint2d(0, 0)
                    textPoint = tg.CreatePoint2d(10, 10)
                    third_jacket_nozzle_circle = third_jacket_nozzle_length_cut_sketch.SketchCircles.AddByCenterRadius(bottom_swg_dish_y_axis_proj_start_pt.Geometry, 202.0)
                    dim = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddRadius(third_jacket_nozzle_circle, textPoint)
                    dim.Parameter.Expression = '2020 mm'
                    third_jacket_nozzle_circle.Construction = True
                    
                    third_jacket_nozzle_circle_center_pt = third_jacket_nozzle_circle.CenterSketchPoint

                    third_jacket_nozzle_circle_coincidence_2 = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_y_axis_proj, third_jacket_nozzle_circle_center_pt)
                    third_jacket_nozzle_circle_coincidence_1 = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_center_proj, third_jacket_nozzle_circle)
                    

                    rect1_width = 10.0
                    rect1_height = 5.0
                    center_x = bottom_swg_dish_center_proj.Geometry.X
                    center_y = bottom_swg_dish_center_proj.Geometry.Y

                    rect1_bottom_left_pt = tg.CreatePoint2d(center_x - rect1_width / 2, center_y)
                    rect1_top_right_pt = tg.CreatePoint2d(center_x + rect1_width / 2, center_y + rect1_height)
                    # Create 2D corner points in sketch space
                    # rect1_bottom_left_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_bottom_left_pt)  # Bottom-left
                    # rect1_top_right_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_top_right_pt)  # Top-right

                    # Add rectangle
                    rect1_lines = third_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(rect1_bottom_left_pt, rect1_top_right_pt)

                    fourth_line_of_rect1 = rect1_lines.Item(4)
                    collinear1 = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCollinear(bottom_jacket_nozzle3_y_axis_pg, fourth_line_of_rect1)

                    second_line_of_rect1 = rect1_lines.Item(2)

                    first_line_of_rect1 = rect1_lines.Item(1)
                    dimTextPt1 = tg.CreatePoint2d(-10, 10)  # Text placement
                    line_1_dimension = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(first_line_of_rect1.StartSketchPoint, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
                    line_1_dimension.Parameter.Expression = '50 mm'

                    
                    dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
                    line_1_dimension = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(second_line_of_rect1.StartSketchPoint, second_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
                    line_1_dimension.Parameter.Expression = '150 mm'

                    new_pt = tg.CreatePoint2d(10, -10)
                    new_sketch_pt = third_jacket_nozzle_length_cut_sketch.SketchPoints.Add(new_pt, False)
                    coincidence1_new_pt = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, third_jacket_nozzle_circle)

                    dimTextPt1 = tg.CreatePoint2d(10, 10)  # Text placement
                    line_1_dimension = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(new_sketch_pt, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
                    line_1_dimension.Parameter.Expression = '9 mm'

                    coincidence1_new_pt = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, second_line_of_rect1)

                    third_jacket_nozzle_length_cut_sketch.Solve()
                    third_jacket_nozzle_length_cut_sketch.UpdateProfiles()
                    third_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
                    third_jacket_nozzle_length_cut_sketch.UpdateProfiles()
                    third_cut_sketch_profile = third_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

                    part_def = inv_app.ActiveDocument.ComponentDefinition

                    third_cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
                    third_cut_sketch_revolve_feature = third_cut_sketch_revolve_feats.AddFull(third_cut_sketch_profile, bottom_jacket_nozzle3_y_axis_pg, 20482)

                    # Remove participants again
                    third_cut_sketch_revolve_feature.RemoveParticipant(bottom_swg_dish)
                    third_cut_sketch_revolve_feature.RemoveParticipant(glass_9100)

                    # first_line_of_rect1
                    # New Sketch: For Nozzle inner cut (Extrude)
                    nozzle_3_yz_plane = jacketnozzle_3.Definition.WorkPlanes["YZ Plane"]
                    nozzle_3_yz_plane_proxy = jacketnozzle_3.CreateGeometryProxy(nozzle_3_yz_plane)
                    nozzle_3_yz_plane_sketch = main_assy_def.Sketches.Add(nozzle_3_yz_plane_proxy)

                    nozzle_3_y_axis = jacketnozzle_3.Definition.WorkAxes["Y Axis"]
                    nozzle_3_y_axis_proxy = jacketnozzle_3.CreateGeometryProxy(nozzle_3_y_axis)
                    nozzle_3_y_axis_pg = nozzle_3_yz_plane_sketch.AddByProjectingEntity(nozzle_3_y_axis_proxy)
                    nozzle_3_y_axis_pg.CenterLine = True

                    first_line_of_rect1_pg = nozzle_3_yz_plane_sketch.AddByProjectingEntity(first_line_of_rect1)

                    # Add rectangle 1
                    nozzle_3_sketch_rectangle = nozzle_3_yz_plane_sketch.SketchLines.AddAsTwoPointRectangle(tg.CreatePoint2d(0, -10), tg.CreatePoint2d(10, 0))
                    nozzle_3_sketch_rectangle_line1 = nozzle_3_sketch_rectangle.Item(1)
                    nozzle_3_sketch_rectangle_line2 = nozzle_3_sketch_rectangle.Item(2)
                    nozzle_3_sketch_rectangle_line3 = nozzle_3_sketch_rectangle.Item(3)
                    nozzle_3_sketch_rectangle_line4 = nozzle_3_sketch_rectangle.Item(4)

                    
                    # nozzle_3_sketch_lin3_yaxis_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle_line3.StartSketchPoint, nozzle_3_y_axis_pg.StartSketchPoint, 19203, dimTextPt)
                    # nozzle_3_sketch_lin3_yaxis_dim.Parameter.Expression = '15 mm'

                    dimTextPt = tg.CreatePoint2d(15, -5)
                    nozzle_3_sketch_lin4_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle_line4.StartSketchPoint, nozzle_3_sketch_rectangle_line4.EndSketchPoint, 19203, dimTextPt)
                    nozzle_3_sketch_lin4_dim.Parameter.Expression = '48 mm'

                    dimTextPt = tg.CreatePoint2d(-10, 15)
                    nozzle_3_sketch_lin1_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle_line1.StartSketchPoint, nozzle_3_sketch_rectangle_line1.EndSketchPoint, 19203, dimTextPt)
                    nozzle_3_sketch_lin1_dim.Parameter.Expression = '38 mm'

                    # dimTextPt = tg.CreatePoint2d(-15, -5)
                    # nozzle_3_sketch_lin3_yaxis_dim_offset = nozzle_3_yz_plane_sketch.DimensionConstraints.AddOffset(nozzle_3_sketch_rectangle_line3, nozzle_3_y_axis_pg, dimTextPt, True)
                    # nozzle_3_sketch_lin3_yaxis_dim_offset.Parameter.Expression = '15 mm'

                    nozzle_3_sketch_fillet_arc = nozzle_3_yz_plane_sketch.SketchArcs.AddByFillet(
                            nozzle_3_sketch_rectangle_line3,                  # Second sketch line (e.g. rectangle's 3rd line)
                            nozzle_3_sketch_rectangle_line4,                  # First sketch line (e.g. rectangle's 2nd line)
                            "15 mm",                 # Fillet radius (use string to specify mm)=
                            nozzle_3_sketch_rectangle_line3.StartSketchPoint.Geometry,  # Point on second line
                            nozzle_3_sketch_rectangle_line4.EndSketchPoint.Geometry,   # Point on first line
                        )
                    
                    arc_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddArcLength(nozzle_3_sketch_fillet_arc, tg.CreatePoint2d(-5, 5))
                    arc_dim.Parameter.Expression = '10 mm'
                    
                    nozzle_3_yz_plane_sketch_verticle_align =  nozzle_3_yz_plane_sketch.GeometricConstraints.AddVerticalAlign(first_line_of_rect1_pg, nozzle_3_sketch_rectangle_line2.EndSketchPoint)

                    profile1 = nozzle_3_yz_plane_sketch.Profiles.AddForSolid()
                    nozzle_3_yz_plane_sketch.UpdateProfiles()
                    
                    # Add rectangle 2 -------------------- Second Rectangle -----------------------
                    nozzle_3_sketch_rectangle2 = nozzle_3_yz_plane_sketch.SketchLines.AddAsTwoPointRectangle(tg.CreatePoint2d(0, -10), tg.CreatePoint2d(10, 0))
                    nozzle_3_sketch_rectangle2_line1 = nozzle_3_sketch_rectangle2.Item(1)
                    nozzle_3_sketch_rectangle2_line2 = nozzle_3_sketch_rectangle2.Item(2)
                    nozzle_3_sketch_rectangle2_line3 = nozzle_3_sketch_rectangle2.Item(3)
                    nozzle_3_sketch_rectangle2_line4 = nozzle_3_sketch_rectangle2.Item(4)

                    dimTextPt = tg.CreatePoint2d(15, -5)
                    nozzle_3_sketch_lin4_dim2 = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle2_line4.StartSketchPoint, nozzle_3_sketch_rectangle2_line4.EndSketchPoint, 19203, dimTextPt)
                    nozzle_3_sketch_lin4_dim2.Parameter.Expression = '48 mm'

                    dimTextPt = tg.CreatePoint2d(-10, 15)
                    nozzle_3_sketch_lin1_dim2 = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle2_line1.StartSketchPoint, nozzle_3_sketch_rectangle2_line1.EndSketchPoint, 19203, dimTextPt)
                    nozzle_3_sketch_lin1_dim2.Parameter.Expression = '38 mm'

                    # dimTextPt = tg.CreatePoint2d(-15, -5)
                    # nozzle_3_sketch_lin3_yaxis_dim_offset2 = nozzle_3_yz_plane_sketch.DimensionConstraints.AddOffset(nozzle_3_sketch_rectangle2_line1, nozzle_3_y_axis_pg, dimTextPt, True)
                    # nozzle_3_sketch_lin3_yaxis_dim_offset2.Parameter.Expression = '15 mm'

                    nozzle_3_sketch_fillet_arc2 = nozzle_3_yz_plane_sketch.SketchArcs.AddByFillet(
                            nozzle_3_sketch_rectangle2_line1,                  # Second sketch line (e.g. rectangle's 3rd line)
                            nozzle_3_sketch_rectangle2_line4,                  # First sketch line (e.g. rectangle's 2nd line)
                            "10 mm",                 # Fillet radius (use string to specify mm)=
                            nozzle_3_sketch_rectangle2_line1.EndSketchPoint.Geometry,  # Point on second line
                            nozzle_3_sketch_rectangle2_line4.StartSketchPoint.Geometry,   # Point on first line
                        )
                    
                    arc_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddArcLength(nozzle_3_sketch_fillet_arc2, tg.CreatePoint2d(5, -5))
                    arc_dim.Parameter.Expression = '10 mm'
                    
                    nozzle_3_yz_plane_sketch_verticle_align2 =  nozzle_3_yz_plane_sketch.GeometricConstraints.AddVerticalAlign(first_line_of_rect1_pg, nozzle_3_sketch_rectangle2_line2.StartSketchPoint)

                    nozzle_3_yz_plane_sketch.GeometricConstraints.AddSymmetry( nozzle_3_sketch_rectangle2_line1, nozzle_3_sketch_rectangle_line3,nozzle_3_y_axis_pg)

                    dimTextPt = tg.CreatePoint2d(-10, 15)
                    nozzle_3_sketch_lin1_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle2_line2.StartSketchPoint, nozzle_3_sketch_rectangle_line2.EndSketchPoint, 19203, dimTextPt)
                    nozzle_3_sketch_lin1_dim.Parameter.Expression = '15 mm'

                    nozzle_3_yz_plane_sketch.Solve()
                    profile2 = nozzle_3_yz_plane_sketch.Profiles.AddForSolid()
                    nozzle_3_yz_plane_sketch.UpdateProfiles()

                    extrude_def2 = part_def.Features.ExtrudeFeatures.CreateExtrudeDefinition(profile2, 20482)
                    extrude_def2.SetDistanceExtent("150 mm", 20995)
                    extrude = part_def.Features.ExtrudeFeatures.Add(extrude_def2)

                    JKT_occ = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="JKT-2100")
                    extrude.RemoveParticipant(JKT_occ)

                    logger.info("End: Third Jacket Nozzle at Bottom")
                    # ------------------------------ Third Jacket Nozzle at Bottom End ------------------------------------------------------------

                    # ------------------------------ Forth Jacket Nozzle at Bottom Start ------------------------------------------------------------
                    logger.info("Start: Forth Jacket Nozzle at Bottom")

                    # Create angled work plane for N17 nozzle
                    bottom_nozzle2_angled_plane = self._create_angled_plane(tg, main_assy_def, NOZZLE_N17_ANGLE, "N17_Plane")

                    bottom_jacket_nozzle4_sketch = main_assy_def.Sketches.Add(main_assy_def.WorkPlanes["XZ Plane"])
                    originPoint = main_assy_def.WorkPoints["Center Point"]  # Usually the origin work point
                    projectedCenter = bottom_jacket_nozzle4_sketch.AddByProjectingEntity(originPoint)
                    originSketchPoint  = bottom_jacket_nozzle4_sketch.SketchPoints.Item(1)
                    startPt = tg.CreatePoint2d(0, 0)
                    endPt = tg.CreatePoint2d(37, 0)  # 370 mm in cm (as Inventor usually uses cm internally)

                    line1 = bottom_jacket_nozzle4_sketch.SketchLines.AddByTwoPoints(startPt, endPt)
                    line1.Construction = True
                    horizontal_line1 = bottom_jacket_nozzle4_sketch.GeometricConstraints.AddHorizontal(line1)
                    coincident0 = bottom_jacket_nozzle4_sketch.GeometricConstraints.AddCoincident(line1.StartSketchPoint, projectedCenter)


                    dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
                    line_1_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddTwoPointDistance(line1.StartSketchPoint, line1.EndSketchPoint, 19201, dimTextPt1)
                    line_1_dimension.Parameter.Expression = '370 mm'

                    endPt2 = tg.CreatePoint2d(0, 37)  # 370 mm along Y
                    line2 = bottom_jacket_nozzle4_sketch.SketchLines.AddByTwoPoints(startPt, endPt2)
                    line2.Construction = True

                    circle_center_point = line2.EndSketchPoint
                    center2d = circle_center_point.Geometry
                    circle = bottom_jacket_nozzle4_sketch.SketchCircles.AddByCenterRadius(center2d, 4.6)

                    dimTextPt2 = tg.CreatePoint2d(-10, 10)  # Text placement
                    line_2_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddTwoPointDistance(line2.StartSketchPoint, line2.EndSketchPoint, 19203, dimTextPt2)
                    line_2_dimension.Parameter.Expression = '370 mm'
                    # vertical_constraint = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddVertical(line2)

                    dimTextPoint = tg.CreatePoint2d(circle.CenterSketchPoint.Geometry.X + 50, circle.CenterSketchPoint.Geometry.Y)
                    # Add diameter dimension (not driven by default, so it drives the size)
                    diameter_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddDiameter(circle, dimTextPoint)
                    # Optionally, set the diameter value explicitly, e.g. 92 mm
                    diameter_dimension.Parameter.Expression = '92 mm'
                    
                    textPoint = tg.CreatePoint2d(10, 10)  # position of dimension text
                    angleDim = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddTwoLineAngle(line1, line2, textPoint)
                    angleDim.Parameter.Expression = "90.0 deg"
                    
                    circle_center = circle.CenterSketchPoint    # The SketchPoint at the center of the circle
                    line_endpoint = line2.EndSketchPoint

                    # coincident1 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(line2.StartSketchPoint, projectedCenter)
                    line2.StartSketchPoint.Merge(projectedCenter)
                    coincident_circle = bottom_jacket_nozzle4_sketch.GeometricConstraints.AddCoincident(circle_center, line_endpoint)
                    
                    

                    bottom_jacket_nozzle4_sketch.Solve()
                    bottom_jacket_nozzle4_sketch.UpdateProfiles()
                    bottom_jacket_nozzle4_sketch.Profiles.AddForSolid()
                    bottom_jacket_nozzle4_sketch.UpdateProfiles()

                    extrude_features  = part_def.Features.ExtrudeFeatures
                    extrude_def = extrude_features.CreateExtrudeDefinition(bottom_jacket_nozzle4_sketch.Profiles[0], 20482)
                    extrude_def.SetDistanceExtent(150, 20994)
                    extrude = extrude_features.Add(extrude_def)

                    extrude_4_n17 = extrude.Faces.Item(1).Geometry
                    base_pt_2 = extrude_4_n17.BasePoint
                    axis_vec_2 = extrude_4_n17.AxisVector
                    axis_4 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
                    axis_4.Name = "N17_Axis"
                    axis_4.Grounded = True

                    # Add second nozzle component
                    jacketnozzle_4 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    jacketnozzle_4.Grounded = False

                    L_occ = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="L_DN150")
                    xz_plane = L_occ.Definition.WorkPlanes["XZ Plane"]
                    xz_plane_proxy = L_occ.CreateGeometryProxy(xz_plane)

                    # Set position
                    transform_4 = tg.CreateMatrix()
                    transform_4.SetTranslation(tg.CreateVector(base_pt_2.X, base_pt_2.Y, base_pt_2.Z))
                    jacketnozzle_4.Transformation = transform_4

                    # Get proxies
                    nozzle4_proxies = self._get_geometry_proxies(jacketnozzle_4, axes=[AXIS_Y], planes=[PLANE_XY, PLANE_XZ])
                    y_axis_4 = nozzle4_proxies.get(AXIS_Y)
                    xy_plane_4 = nozzle4_proxies.get(PLANE_XY)
                    xz_plane_4 = nozzle4_proxies.get(PLANE_XZ)

                    # Add constraints
                    flush_4 = self._add_flush_constraint(main_assy_def, bottom_nozzle2_angled_plane, xy_plane_4)
                    mate_y_4 = self._add_mate_constraint(main_assy_def, axis_4, y_axis_4)
                    mate_xz_4 = self._add_mate_constraint(main_assy_def, xz_plane_4, xz_plane_proxy, "90 mm")

                    self.hide_workplanes_recursively(occurrence=jacketnozzle_4)

                    # Start cut revolve operation on first jacket nozzle:

                    # xz_plane_nozzle_3 = jacketnozzle_3.Definition.WorkPlanes["XY Plane"]
                    # bottom_nozzle1_angled_plane_proxy = jacketnozzle_3.CreateGeometryProxy(bottom_nozzle1_angled_plane)
                    fourth_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(bottom_nozzle2_angled_plane)
                    
                    bottom_jacket_nozzle4_y_axis = jacketnozzle_4.Definition.WorkAxes["Y Axis"]
                    bottom_jacket_nozzle4_y_axis_proxy = jacketnozzle_4.CreateGeometryProxy(bottom_jacket_nozzle4_y_axis)
                    bottom_jacket_nozzle4_y_axis_pg = fourth_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_jacket_nozzle4_y_axis_proxy)
                    bottom_jacket_nozzle4_y_axis_pg.CenterLine = True
                    
                    bottom_swg_dish = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="BTM-1950")
                    bottom_swg_dish_center_point = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkPoints["Center Point"])
                    bottom_swg_dish_center_proj = fourth_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_center_point)

                    bottom_swg_dish_y_axis = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkAxes["Y Axis"])
                    

                    bottom_swg_dish_y_axis_proj = fourth_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_y_axis)
                    bottom_swg_dish_y_axis_proj_start_pt = bottom_swg_dish_y_axis_proj.StartSketchPoint
                    # bottom_swg_dish_y_axis_proj.CenterLine = True

                    # Draw Circle
                    # center2d_point = tg.CreatePoint2d(0, 0)
                    textPoint = tg.CreatePoint2d(10, 10)
                    fourth_jacket_nozzle_circle = fourth_jacket_nozzle_length_cut_sketch.SketchCircles.AddByCenterRadius(bottom_swg_dish_y_axis_proj_start_pt.Geometry, 202.0)
                    dim = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddRadius(fourth_jacket_nozzle_circle, textPoint)
                    dim.Parameter.Expression = '2020 mm'
                    fourth_jacket_nozzle_circle.Construction = True
                    
                    fourth_jacket_nozzle_circle_center_pt = fourth_jacket_nozzle_circle.CenterSketchPoint

                    fourth_jacket_nozzle_circle_coincidence_2 = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_y_axis_proj, fourth_jacket_nozzle_circle_center_pt)
                    fourth_jacket_nozzle_circle_coincidence_1 = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_center_proj, fourth_jacket_nozzle_circle)
                    

                    rect1_width = 10.0
                    rect1_height = 5.0
                    center_x = bottom_swg_dish_center_proj.Geometry.X
                    center_y = bottom_swg_dish_center_proj.Geometry.Y

                    rect1_bottom_left_pt = tg.CreatePoint2d(center_x - rect1_width / 2, center_y)
                    rect1_top_right_pt = tg.CreatePoint2d(center_x + rect1_width / 2, center_y + rect1_height)
                    # Create 2D corner points in sketch space
                    # rect1_bottom_left_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_bottom_left_pt)  # Bottom-left
                    # rect1_top_right_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_top_right_pt)  # Top-right

                    # Add rectangle
                    rect1_lines = fourth_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(rect1_bottom_left_pt, rect1_top_right_pt)

                    fourth_line_of_rect1 = rect1_lines.Item(4)
                    collinear1 = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCollinear(bottom_jacket_nozzle4_y_axis_pg, fourth_line_of_rect1)

                    second_line_of_rect1 = rect1_lines.Item(2)

                    first_line_of_rect1 = rect1_lines.Item(1)
                    dimTextPt1 = tg.CreatePoint2d(-10, 10)  # Text placement
                    line_1_dimension = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(first_line_of_rect1.StartSketchPoint, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
                    line_1_dimension.Parameter.Expression = '50 mm'

                    
                    dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
                    line_1_dimension = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(second_line_of_rect1.StartSketchPoint, second_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
                    line_1_dimension.Parameter.Expression = '150 mm'

                    new_pt = tg.CreatePoint2d(10, -10)
                    new_sketch_pt = fourth_jacket_nozzle_length_cut_sketch.SketchPoints.Add(new_pt, False)
                    coincidence1_new_pt = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, fourth_jacket_nozzle_circle)

                    dimTextPt1 = tg.CreatePoint2d(10, 10)  # Text placement
                    line_1_dimension = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(new_sketch_pt, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
                    line_1_dimension.Parameter.Expression = '9 mm'

                    coincidence1_new_pt = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, second_line_of_rect1)

                    fourth_jacket_nozzle_length_cut_sketch.Solve()
                    fourth_jacket_nozzle_length_cut_sketch.UpdateProfiles()
                    fourth_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
                    fourth_jacket_nozzle_length_cut_sketch.UpdateProfiles()
                    fourth_cut_sketch_profile = fourth_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

                    part_def = inv_app.ActiveDocument.ComponentDefinition

                    fourth_cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
                    fourth_cut_sketch_revolve_feature = fourth_cut_sketch_revolve_feats.AddFull(fourth_cut_sketch_profile, bottom_jacket_nozzle4_y_axis_pg, 20482)

                    # Remove participants again
                    fourth_cut_sketch_revolve_feature.RemoveParticipant(bottom_swg_dish)
                    fourth_cut_sketch_revolve_feature.RemoveParticipant(glass_9100)


                    # New Sketch: For Nozzle inner cut (Extrude)
                    nozzle_4_yz_plane = jacketnozzle_4.Definition.WorkPlanes["YZ Plane"]
                    nozzle_4_yz_plane_proxy = jacketnozzle_4.CreateGeometryProxy(nozzle_4_yz_plane)
                    nozzle_4_yz_plane_sketch = main_assy_def.Sketches.Add(nozzle_4_yz_plane_proxy)

                    nozzle_4_y_axis = jacketnozzle_4.Definition.WorkAxes["Y Axis"]
                    nozzle_4_y_axis_proxy = jacketnozzle_4.CreateGeometryProxy(nozzle_4_y_axis)
                    nozzle_4_y_axis_pg = nozzle_4_yz_plane_sketch.AddByProjectingEntity(nozzle_4_y_axis_proxy)
                    nozzle_4_y_axis_pg.CenterLine = True

                    first_line_of_rect1_pg = nozzle_4_yz_plane_sketch.AddByProjectingEntity(first_line_of_rect1)

                    # Add rectangle 1
                    nozzle_4_sketch_rectangle = nozzle_4_yz_plane_sketch.SketchLines.AddAsTwoPointRectangle(tg.CreatePoint2d(0, -10), tg.CreatePoint2d(10, 0))
                    nozzle_4_sketch_rectangle_line1 = nozzle_4_sketch_rectangle.Item(1)
                    nozzle_4_sketch_rectangle_line2 = nozzle_4_sketch_rectangle.Item(2)
                    nozzle_4_sketch_rectangle_line3 = nozzle_4_sketch_rectangle.Item(3)
                    nozzle_4_sketch_rectangle_line4 = nozzle_4_sketch_rectangle.Item(4)

                    dimTextPt = tg.CreatePoint2d(15, -5)
                    nozzle_4_sketch_lin4_dim = nozzle_4_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_4_sketch_rectangle_line4.StartSketchPoint, nozzle_4_sketch_rectangle_line4.EndSketchPoint, 19203, dimTextPt)
                    nozzle_4_sketch_lin4_dim.Parameter.Expression = '48 mm'

                    dimTextPt = tg.CreatePoint2d(-10, 15)
                    nozzle_4_sketch_lin1_dim = nozzle_4_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_4_sketch_rectangle_line1.StartSketchPoint, nozzle_4_sketch_rectangle_line1.EndSketchPoint, 19203, dimTextPt)
                    nozzle_4_sketch_lin1_dim.Parameter.Expression = '38 mm'

                    nozzle_4_sketch_fillet_arc = nozzle_4_yz_plane_sketch.SketchArcs.AddByFillet(
                            nozzle_4_sketch_rectangle_line3,
                            nozzle_4_sketch_rectangle_line4,
                            "10 mm",
                            nozzle_4_sketch_rectangle_line3.StartSketchPoint.Geometry,
                            nozzle_4_sketch_rectangle_line4.EndSketchPoint.Geometry,
                        )
                    
                    arc_dim = nozzle_4_yz_plane_sketch.DimensionConstraints.AddArcLength(nozzle_4_sketch_fillet_arc, tg.CreatePoint2d(-5, 5))
                    arc_dim.Parameter.Expression = '10 mm'
                    
                    nozzle_4_yz_plane_sketch_verticle_align =  nozzle_4_yz_plane_sketch.GeometricConstraints.AddVerticalAlign(first_line_of_rect1_pg, nozzle_4_sketch_rectangle_line2.EndSketchPoint)

                    profile1 = nozzle_4_yz_plane_sketch.Profiles.AddForSolid()
                    nozzle_4_yz_plane_sketch.UpdateProfiles()
                    
                    # Add rectangle 2 -------------------- Second Rectangle -----------------------
                    nozzle_4_sketch_rectangle2 = nozzle_4_yz_plane_sketch.SketchLines.AddAsTwoPointRectangle(tg.CreatePoint2d(0, -10), tg.CreatePoint2d(10, 0))
                    nozzle_4_sketch_rectangle2_line1 = nozzle_4_sketch_rectangle2.Item(1)
                    nozzle_4_sketch_rectangle2_line2 = nozzle_4_sketch_rectangle2.Item(2)
                    nozzle_4_sketch_rectangle2_line3 = nozzle_4_sketch_rectangle2.Item(3)
                    nozzle_4_sketch_rectangle2_line4 = nozzle_4_sketch_rectangle2.Item(4)

                    dimTextPt = tg.CreatePoint2d(15, -5)
                    nozzle_4_sketch_lin4_dim2 = nozzle_4_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_4_sketch_rectangle2_line4.StartSketchPoint, nozzle_4_sketch_rectangle2_line4.EndSketchPoint, 19203, dimTextPt)
                    nozzle_4_sketch_lin4_dim2.Parameter.Expression = '48 mm'

                    dimTextPt = tg.CreatePoint2d(-10, 15)
                    nozzle_4_sketch_lin1_dim2 = nozzle_4_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_4_sketch_rectangle2_line1.StartSketchPoint, nozzle_4_sketch_rectangle2_line1.EndSketchPoint, 19203, dimTextPt)
                    nozzle_4_sketch_lin1_dim2.Parameter.Expression = '38 mm'

                    nozzle_4_sketch_fillet_arc2 = nozzle_4_yz_plane_sketch.SketchArcs.AddByFillet(
                            nozzle_4_sketch_rectangle2_line1,                  # Second sketch line (e.g. rectangle's 3rd line)
                            nozzle_4_sketch_rectangle2_line4,                  # First sketch line (e.g. rectangle's 2nd line)
                            "10 mm",                 # Fillet radius (use string to specify mm)=
                            nozzle_4_sketch_rectangle2_line1.EndSketchPoint.Geometry,  # Point on second line
                            nozzle_4_sketch_rectangle2_line4.StartSketchPoint.Geometry,   # Point on first line
                        )
                    
                    arc_dim = nozzle_4_yz_plane_sketch.DimensionConstraints.AddArcLength(nozzle_4_sketch_fillet_arc2, tg.CreatePoint2d(5, -5))
                    arc_dim.Parameter.Expression = '10 mm'
                    
                    nozzle_4_yz_plane_sketch_verticle_align2 =  nozzle_4_yz_plane_sketch.GeometricConstraints.AddVerticalAlign(first_line_of_rect1_pg, nozzle_4_sketch_rectangle2_line2.StartSketchPoint)

                    nozzle_4_yz_plane_sketch.GeometricConstraints.AddSymmetry( nozzle_4_sketch_rectangle2_line1, nozzle_4_sketch_rectangle_line3, nozzle_4_y_axis_pg)

                    dimTextPt = tg.CreatePoint2d(-10, 15)
                    nozzle_4_sketch_lin1_dim = nozzle_4_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_4_sketch_rectangle2_line2.StartSketchPoint, nozzle_4_sketch_rectangle_line2.EndSketchPoint, 19203, dimTextPt)
                    nozzle_4_sketch_lin1_dim.Parameter.Expression = '15 mm'

                    nozzle_4_yz_plane_sketch.Solve()
                    profile2 = nozzle_4_yz_plane_sketch.Profiles.AddForSolid()
                    nozzle_4_yz_plane_sketch.UpdateProfiles()

                    extrude_def2 = part_def.Features.ExtrudeFeatures.CreateExtrudeDefinition(profile2, 20482)
                    extrude_def2.SetDistanceExtent("150 mm", 20995)
                    extrude = part_def.Features.ExtrudeFeatures.Add(extrude_def2)

                    JKT_occ = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="JKT-2100")
                    extrude.RemoveParticipant(JKT_occ)

                    logger.info("End: Forth Jacket Nozzle at Bottom")
                    logger.info("End: jacketnozzle_n17_btm")
                
                elif item.get("component") == 'airvent_coupling_n11':
                    logger.info("Start: airvent_coupling_n11 (MS COUPLING)")
                    JSR_MSS = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="JSR-MSS-2100-10-00")
                    JSR_MSS_N13_Degree_plane = JSR_MSS.Definition.WorkPlanes["N13 DEGREE"]
                    JSR_MSS_N13_Degree_plane_proxy = JSR_MSS.CreateGeometryProxy(JSR_MSS_N13_Degree_plane)
                    JSR_MSS_sketch = main_assy_def.Sketches.Add(JSR_MSS_N13_Degree_plane_proxy)

                    JSR_MSS_N13_Axis = JSR_MSS.Definition.WorkAxes["N13 AXIS"]
                    JSR_MSS_N13_Axis_proxy = JSR_MSS.CreateGeometryProxy(JSR_MSS_N13_Axis)
                    JSR_MSS_N13_Axis_pg = JSR_MSS_sketch.AddByProjectingEntity(JSR_MSS_N13_Axis_proxy)
                    JSR_MSS_N13_Axis_pg.CenterLine = True

                    JSR_MSS_N13_REF_plane = JSR_MSS.Definition.WorkPlanes["REF PLANE N13"]
                    JSR_MSS_N13_REF_plane_proxy = JSR_MSS.CreateGeometryProxy(JSR_MSS_N13_REF_plane)
                    JSR_MSS_N13_REF_plane_proxy_pg = JSR_MSS_sketch.AddByProjectingEntity(JSR_MSS_N13_REF_plane_proxy)
                    JSR_MSS_N13_REF_plane_proxy_pg.Construction = True

                    # Draw the rectangle
                    rect_lines = JSR_MSS_sketch.SketchLines.AddAsThreePointRectangle(tg.CreatePoint2d(0, 0), tg.CreatePoint2d(0, 5) , tg.CreatePoint2d(10, 2.5))
                    JSR_MSS_collinear = JSR_MSS_sketch.GeometricConstraints.AddCollinear(JSR_MSS_N13_Axis_pg, rect_lines.Item(4))

                    # JSR_MSS_collinear = JSR_MSS_sketch.GeometricConstraints.AddCollinear(JSR_MSS_N13_Axis_pg, rect_lines.Item(2))

                    dimension1 = JSR_MSS_sketch.DimensionConstraints.AddTwoPointDistance(rect_lines.Item(1).StartSketchPoint, rect_lines.Item(1).EndSketchPoint, 19203, tg.CreatePoint2d(-10, 10), False)
                    dimension1.Parameter.Expression = '17.5 mm'

                    dimension2 = JSR_MSS_sketch.DimensionConstraints.AddTwoPointDistance(rect_lines.Item(2).StartSketchPoint, rect_lines.Item(2).EndSketchPoint, 19203, tg.CreatePoint2d(-15, 15), False)
                    dimension2.Parameter.Expression = '60 mm'

                    start_geom = rect_lines.Item(2).StartSketchPoint.Geometry
                    end_geom = rect_lines.Item(2).EndSketchPoint.Geometry

                    midpoint = tg.CreatePoint2d(
                        (start_geom.X + end_geom.X) / 2,
                        (start_geom.Y + end_geom.Y) / 2
                    )

                    midSketchPoint = JSR_MSS_sketch.SketchPoints.Add(midpoint)
                    point = JSR_MSS_sketch.GeometricConstraints.AddMidpoint(midSketchPoint, rect_lines.Item(2))

                    JSR_MSS_coincidence = JSR_MSS_sketch.GeometricConstraints.AddCoincident(midSketchPoint, JSR_MSS_N13_REF_plane_proxy_pg)

                    JSR_MSS_sketch.Solve()
                    JSR_MSS_sketch.UpdateProfiles()
                    JSR_MSS_sketch.Profiles.AddForSolid()
                    JSR_MSS_sketch.UpdateProfiles()

                    revolve_features = main_assy_def.Features.RevolveFeatures
                    revolve_feature = revolve_features.AddFull(JSR_MSS_sketch.Profiles.Item(1), JSR_MSS_N13_Axis_pg, 20482)

                    glass_9100 = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="GL_MBCE-06300-2020")
                    revolve_feature.RemoveParticipant(glass_9100)

                    ms_coupling = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    ms_coupling.Grounded = False
                    
                    ms_coupling_y_axis_proxy = ms_coupling.CreateGeometryProxy(ms_coupling.Definition.WorkAxes["Y Axis"])
                    ms_coupling_xy_plan_proxy = ms_coupling.CreateGeometryProxy(ms_coupling.Definition.WorkPlanes["XY Plane"])
                    ms_coupling_xz_plan_proxy = ms_coupling.CreateGeometryProxy(ms_coupling.Definition.WorkPlanes["XZ Plane"])
                    
                    mate_y_ms_coupling = main_assy_def.Constraints.AddMateConstraint2(ms_coupling_y_axis_proxy, JSR_MSS_N13_Axis_proxy, 0, 24833, 24833, 115459, None, None)
                    flush_ms_coupling_1 = main_assy_def.Constraints.AddFlushConstraint(ms_coupling_xy_plan_proxy, JSR_MSS_N13_Degree_plane_proxy, 0, None, None)
                    flush_ms_coupling_2 = main_assy_def.Constraints.AddFlushConstraint(ms_coupling_xz_plan_proxy, JSR_MSS_N13_REF_plane_proxy, "17 mm", None, None)
                    
                    self.hide_workplanes_recursively(occurrence=ms_coupling)
                    
                    # MS COUPLING TOP - End


                    # MS COUPLING BOTTOM - Start
                    # print("Bottom MS COUPLING Start")
                    logger.info("Start: Bottom MS Coupling")
                    main_xz_plane = main_assy_def.WorkPlanes["XZ Plane"]
                    main_xy_plane = main_assy_def.WorkPlanes["XY Plane"]
                    ms_coupling_btm_sketch= main_assy_def.Sketches.Add(main_xz_plane)
                    originPoint = main_assy_def.WorkPoints["Center Point"]
                    projectedCenter = ms_coupling_btm_sketch.AddByProjectingEntity(originPoint)

                    startPt = tg.CreatePoint2d(0, 0)
                    endPt = tg.CreatePoint2d(-23.35, 0)  # 370 mm in cm (as Inventor usually uses cm internally)

                    line1 = ms_coupling_btm_sketch.SketchLines.AddByTwoPoints(startPt, endPt)
                    line1.Construction = True
                    ms_coupling_btm_sketch.GeometricConstraints.AddHorizontal(line1)
                    ms_coupling_btm_sketch.GeometricConstraints.AddCoincident(line1.StartSketchPoint, projectedCenter)
                    dimTextPt = tg.CreatePoint2d(10, 10)
                    ms_coupling_btm_sketch.DimensionConstraints.AddTwoPointDistance(line1.EndSketchPoint, projectedCenter, 19203, dimTextPt, False)

                    endPt_line2 = tg.CreatePoint2d(23.35, 0)

                    line2 = ms_coupling_btm_sketch.SketchLines.AddByTwoPoints(startPt, endPt_line2)
                    line2.Construction = True
                    line2.StartSketchPoint.Merge(projectedCenter)

                    line2_endpoint = line2.EndSketchPoint
                    ms_coupling_btm_circle = ms_coupling_btm_sketch.SketchCircles.AddByCenterRadius(line2_endpoint, 3.5)
                    ms_coupling_btm_sketch.GeometricConstraints.AddCoincident(line2_endpoint, ms_coupling_btm_circle.CenterSketchPoint)
                    ms_coupling_btm_sketch.DimensionConstraints.AddTwoPointDistance(line2.EndSketchPoint, projectedCenter, 19203, dimTextPt, False)

                    textPoint = tg.CreatePoint2d(10, 10) 
                    line_angle = ms_coupling_btm_sketch.DimensionConstraints.AddTwoLineAngle(line1, line2, textPoint)
                    line_angle.Parameter.Expression = "180.0 deg"

                    dimTextPoint = tg.CreatePoint2d(20, 10)
                    diameter_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddDiameter(ms_coupling_btm_circle, dimTextPoint)
                    # Optionally, set the diameter value explicitly, e.g. 92 mm
                    diameter_dimension.Parameter.Expression = '35 mm'

                    ms_coupling_btm_sketch.Solve()
                    ms_coupling_btm_sketch.UpdateProfiles()
                    ms_coupling_btm_sketch.Profiles.AddForSolid()
                    ms_coupling_btm_sketch.UpdateProfiles()

                    extrude_features  = part_def.Features.ExtrudeFeatures
                    extrude_def = extrude_features.CreateExtrudeDefinition(ms_coupling_btm_sketch.Profiles[0], 20482)
                    extrude_def.SetDistanceExtent(150, 20994)
                    extrude = extrude_features.Add(extrude_def)

                    extrude_T11 = extrude.Faces.Item(1).Geometry
                    base_pt_2 = extrude_T11.BasePoint
                    axis_vec_2 = extrude_T11.AxisVector
                    axis_T11 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
                    axis_T11.Name = "T11_Axis"
                    axis_T11.Grounded = True

                    ms_coupling2 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    ms_coupling2.Grounded = False
                    
                    jacket_diapharm_ring = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="3616000548 01")
                    drain_mounting__plane_proxy = jacket_diapharm_ring.CreateGeometryProxy(jacket_diapharm_ring.Definition.WorkPlanes["DRAIN MOUNTING PLANE"])

                    ms_coupling_y_axis_proxy2 = ms_coupling2.CreateGeometryProxy(ms_coupling2.Definition.WorkAxes["Y Axis"])
                    ms_coupling_xy_plan_proxy2 = ms_coupling2.CreateGeometryProxy(ms_coupling2.Definition.WorkPlanes["XY Plane"])
                    ms_coupling_xz_plan_proxy2 = ms_coupling2.CreateGeometryProxy(ms_coupling2.Definition.WorkPlanes["XZ Plane"])
                    
                    mate_y_ms_coupling = main_assy_def.Constraints.AddMateConstraint2(ms_coupling_y_axis_proxy2, axis_T11, 0, 24833, 24833, 115459, None, None)
                    mate_ms_coupling_1 = main_assy_def.Constraints.AddMateConstraint(ms_coupling_xy_plan_proxy2, main_xy_plane, 0, 24833, 24833, None, None)
                    mate_ms_coupling_2 = main_assy_def.Constraints.AddMateConstraint(ms_coupling_xz_plan_proxy2, drain_mounting__plane_proxy, 0, 24833, 24833, None, None)
                    self.hide_workplanes_recursively(occurrence=ms_coupling2)
                    logger.info("End: Bottom MS Coupling")
                    logger.info("End: airvent_coupling_n11 (MS COUPLING)")

                elif item.get("component") == 'nozzle_500_0_gasket_1':
                    # print("manhole_gasket_1 constraint start")
                    logger.info("Start: n1_500_0_gasket_1 (manhole_gasket_1)")
                    monoblock = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="MBCE-06300-2020")
                    manhole_stump= self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="_MH_")
                    # manhole_stump = self.find_occurrence_by_keyword_recursive(occurrences=monoblock.SubOccurrences, target_keyword="3817-0018")
                    manhole_gasket_1 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    manhole_gasket_1.Grounded = False
                    manhole_stump_y_axis_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkAxes["Y Axis"])
                    manhole_gasket_1_y_axis_proxy = manhole_gasket_1.CreateGeometryProxy(manhole_gasket_1.Definition.WorkAxes["Y Axis"])

                    manhole_stump_xy_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["XY Plane"])
                    manhole_gasket_1_xy_plane_proxy = manhole_gasket_1.CreateGeometryProxy(manhole_gasket_1.Definition.WorkPlanes["XY Plane"])

                    manhole_stump_xz_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["XZ Plane"])
                    manhole_gasket_1_xz_plane_proxy = manhole_gasket_1.CreateGeometryProxy(manhole_gasket_1.Definition.WorkPlanes["XZ Plane"])

                    manhole_gasket_mate_1 = main_assy_def.Constraints.AddMateConstraint2(manhole_stump_y_axis_proxy, manhole_gasket_1_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    manhole_gasket_mate_2 = main_assy_def.Constraints.AddMateConstraint(manhole_stump_xy_plane_proxy, manhole_gasket_1_xy_plane_proxy, 0, 24833, 24833, None, None)
                    manhole_gasket_flush_1 = main_assy_def.Constraints.AddFlushConstraint(manhole_stump_xz_plane_proxy, manhole_gasket_1_xz_plane_proxy, 0, None, None)
                    self.hide_workplanes_recursively(occurrence=manhole_gasket_1)
                    logger.info("End: n1_500_0_gasket_1 (manhole_gasket_1)")

                elif item.get("component") == 'nozzle_500_0_manhole_protection_ring_1':
                    # print("bush_type_protection_ring start")
                    logger.info("Start: n1_500_0_manhole_protection_ring_1 (bush_type_protection_ring)")
                    # bush_type_protection_ring = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="3616000548 01")
                    PTFE_envelop = self.find_occurrence_recursive(occurrences=manhole_gasket_1.SubOccurrences, target_name='DN500_605_521_8.9_ROUND ENVELOPE_MANHOLE:1')
                    gasket_ref_plane = PTFE_envelop.CreateGeometryProxy(PTFE_envelop.Definition.WorkPlanes["GASKET REF PLANE"])
                    
                    bush_type_protection_ring = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    bush_type_protection_ring.Grounded = False

                    bush_type_protection_ring_y_axis_proxy = bush_type_protection_ring.CreateGeometryProxy(bush_type_protection_ring.Definition.WorkAxes["Y Axis"])
                    bush_type_protection_ring_xy_plane_proxy = bush_type_protection_ring.CreateGeometryProxy(bush_type_protection_ring.Definition.WorkPlanes["XY Plane"])
                    bush_type_protection_ring_xz_plane_proxy = bush_type_protection_ring.CreateGeometryProxy(bush_type_protection_ring.Definition.WorkPlanes["XZ Plane"])

                    bush_type_protection_ring_gasket_mate_1 = main_assy_def.Constraints.AddMateConstraint2(bush_type_protection_ring_y_axis_proxy, manhole_gasket_1_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    bush_type_protection_ring_gasket_mate_2 = main_assy_def.Constraints.AddMateConstraint(bush_type_protection_ring_xy_plane_proxy, manhole_gasket_1_xy_plane_proxy, 0, 24833, 24833, None, None)
                    bush_type_protection_ring_flush_1 = main_assy_def.Constraints.AddFlushConstraint(bush_type_protection_ring_xz_plane_proxy, gasket_ref_plane, "-30 mm ", None, None)
                    self.hide_workplanes_recursively(occurrence=bush_type_protection_ring)
                    logger.info("End: n1_500_0_manhole_protection_ring_1 (bush_type_protection_ring)")

                elif item.get("component") == 'nozzle_500_0_gasket_2':
                    # print("manhole_gasket_2 constraint start")
                    logger.info("Start: n1_500_0_gasket_2 (manhole_gasket_2)")
                    monoblock = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="MBCE-06300-2020")
                    manhole_stump= self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="_MH_")
                    # manhole_stump = self.find_occurrence_by_keyword_recursive(occurrences=monoblock.SubOccurrences, target_keyword="3817-0018")
                    manhole_gasket_2 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    manhole_gasket_2.Grounded = False
                    manhole_stump_y_axis_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkAxes["Y Axis"])
                    manhole_gasket_2_y_axis_proxy = manhole_gasket_2.CreateGeometryProxy(manhole_gasket_2.Definition.WorkAxes["Y Axis"])

                    manhole_stump_xy_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["XY Plane"])
                    manhole_gasket_2_xy_plane_proxy = manhole_gasket_2.CreateGeometryProxy(manhole_gasket_2.Definition.WorkPlanes["XY Plane"])

                    manhole_stump_xz_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["XZ Plane"])
                    manhole_gasket_2_xz_plane_proxy = manhole_gasket_2.CreateGeometryProxy(manhole_gasket_2.Definition.WorkPlanes["XZ Plane"])

                    manhole_gasket_2_mate_1 = main_assy_def.Constraints.AddMateConstraint2(manhole_stump_y_axis_proxy, manhole_gasket_2_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    manhole_gasket_2_mate_2 = main_assy_def.Constraints.AddMateConstraint(manhole_stump_xy_plane_proxy, manhole_gasket_2_xy_plane_proxy, 0, 24833, 24833, None, None)
                    manhole_gasket_2_flush_1 = main_assy_def.Constraints.AddFlushConstraint(bush_type_protection_ring_xz_plane_proxy, manhole_gasket_2_xz_plane_proxy, 0, None, None)
                    self.hide_workplanes_recursively(occurrence=manhole_gasket_2)

                    logger.info("End: n1_500_0_gasket_2 (manhole_gasket_2)")
                
                elif item.get("component") == 'nozzle_500_0_manhole_cover_1':
                    # print("manhole_cover start")
                    logger.info("Start: n1_500_0_manhole_cover_1 (manhole_cover)")
                    PTFE_envelop_2 = self.find_occurrence_recursive(occurrences=manhole_gasket_2.SubOccurrences, target_name='DN500_605_521_8.9_ROUND ENVELOPE_MANHOLE:1')
                    gasket_ref_plane_2 = PTFE_envelop_2.CreateGeometryProxy(PTFE_envelop_2.Definition.WorkPlanes["GASKET REF PLANE"])

                    manhole_cover = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    manhole_cover.Grounded = False

                    manhole_cover_y_axis_proxy = manhole_cover.CreateGeometryProxy(manhole_cover.Definition.WorkAxes["Y Axis"])
                    manhole_cover_xy_plane_proxy = manhole_cover.CreateGeometryProxy(manhole_cover.Definition.WorkPlanes["XY Plane"])
                    manhole_cover_xz_plane_proxy = manhole_cover.CreateGeometryProxy(manhole_cover.Definition.WorkPlanes["XZ Plane"])
                    manhole_cover_yz_plane_proxy = manhole_cover.CreateGeometryProxy(manhole_cover.Definition.WorkPlanes["YZ Plane"])
                    
                    manhole_cover_mate_1 = main_assy_def.Constraints.AddMateConstraint2(manhole_stump_y_axis_proxy, manhole_cover_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    manhole_cover_mate_2 = main_assy_def.Constraints.AddFlushConstraint(manhole_stump_xy_plane_proxy, manhole_cover_xy_plane_proxy, 0, None, None)
                    manhole_cover_flush_1 = main_assy_def.Constraints.AddFlushConstraint(manhole_cover_xz_plane_proxy, gasket_ref_plane_2, 0, None, None)
                    self.hide_workplanes_recursively(occurrence=manhole_cover)
                    logger.info("End: n1_500_0_manhole_cover_1 (manhole_cover)")
                    # print("manhole_cover end")
                
                elif item.get("component") == 'mhcclamp':
                    # print("manhole_c_clamp start")
                    logger.info("Start: mhcclamp (manhole_c_clamp)")
                    manhole_c_clamp = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    manhole_c_clamp.Grounded = False

                    # manhole_stump = self.find_occurrence_by_keyword_recursive(occurrences=monoblock.SubOccurrences, target_keyword="3817-0018")
                    manhole_stump= self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="_MH_")
                    # Get axis and plane
                    stump_y_axis_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkAxes["Y Axis"])
                    stump_xy_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["XY Plane"])
                    stump_xz_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["XZ Plane"])
                    
                    pt = stump_xy_plane_proxy.Plane.RootPoint
                    manhole_stump_origin_point = tg.CreatePoint(float(pt.X), float(pt.Y), float(pt.Z))

                    y_vector = stump_y_axis_proxy.Line.Direction  # UnitVector
                    z_vector = stump_xy_plane_proxy.Plane.Normal  # UnitVector
                    x_vector = z_vector.CrossProduct(y_vector)

                    # Create COM-safe unit vector for X
                    x_unit_vector = tg.CreateUnitVector(float(x_vector.X), float(x_vector.Y), float(x_vector.Z))

                    # Convert Y axis direction to Vector for rotation (not UnitVector!)
                    y_vector_for_rotation = tg.CreateVector(float(y_vector.X), float(y_vector.Y), float(y_vector.Z))

                    # Create rotation matrix and apply 15° rotation around Y vector
                    rotation_matrix = tg.CreateMatrix()
                    angle_rad = math.radians(15.0)
                    rotation_matrix.SetToRotation(angle_rad, y_vector_for_rotation, manhole_stump_origin_point)

                    # Rotate X axis
                    rotated_x_vector = x_unit_vector.Copy()
                    rotated_x_vector.TransformBy(rotation_matrix)

                    # Create new work plane
                    work_planes = main_assy_def.WorkPlanes
                    C_CLAMP_PLANE_15DEGREE = work_planes.AddFixed(manhole_stump_origin_point, rotated_x_vector, y_vector, False)
                    C_CLAMP_PLANE_15DEGREE.Name = "C_CLAMP_PLANE_15DEGREE"
                    C_CLAMP_PLANE_15DEGREE.Visible = False
                    C_CLAMP_PLANE_15DEGREE.Grounded = True

                    rotation_matrix_90 = tg.CreateMatrix()
                    rotation_matrix_90.SetToRotation(math.radians(90.0), y_vector_for_rotation, manhole_stump_origin_point)

                    # Step 3: Create new rotated vector (X vector of new plane)
                    rotated_x_vector_90 = rotated_x_vector.Copy()
                    rotated_x_vector_90.TransformBy(rotation_matrix_90)

                    # Step 4: Create new plane using rotated vector and same Y axis
                    C_CLAMP_PLANE_15_PLUS_90 = work_planes.AddFixed(
                        manhole_stump_origin_point,     # Same origin
                        rotated_x_vector_90,            # New X-axis vector
                        y_vector,                       # Same Y-axis (from stump)
                        False
                    )
                    C_CLAMP_PLANE_15_PLUS_90.Name = "C_CLAMP_PLANE_15_PLUS_90"
                    C_CLAMP_PLANE_15_PLUS_90.Visible = False
                    C_CLAMP_PLANE_15_PLUS_90.Grounded = True
                    
                    
                    j_bolt = self.find_occurrence_recursive(occurrences=manhole_c_clamp.SubOccurrences, target_name="C CLAMP J BOLT M24x125Lg_02-GPF-11620 R4")
                    J_BOLT_MOUNTING_PLANE_proxy = j_bolt.CreateGeometryProxy(j_bolt.Definition.WorkPlanes["J BOLT MOUNTING PLANE"])
                    J_BOLT_MOUNTING_PLANE_1_proxy = j_bolt.CreateGeometryProxy(j_bolt.Definition.WorkPlanes["J BOLT MOUNTING PLANE_1"])

                    manhole_c_clamp_xy_plane_proxy = manhole_c_clamp.CreateGeometryProxy(manhole_c_clamp.Definition.WorkPlanes["XY Plane"])


                    manhole_c_clamp_mate1 = main_assy_def.Constraints.AddMateConstraint(manhole_c_clamp_xy_plane_proxy, C_CLAMP_PLANE_15DEGREE, 0, 24833, 24833, None, None)
                    manhole_c_clamp_mate2 = main_assy_def.Constraints.AddMateConstraint(stump_xz_plane_proxy, J_BOLT_MOUNTING_PLANE_proxy, -3.7, 24833, 24833, None, None)
                    manhole_c_clamp_mate3 = main_assy_def.Constraints.AddMateConstraint(C_CLAMP_PLANE_15_PLUS_90, J_BOLT_MOUNTING_PLANE_1_proxy, 31.0, 24833, 24833, None, None)

                    clamp_collection_1 = inv_app.TransientObjects.CreateObjectCollection()
                    clamp_collection_1.Add(manhole_c_clamp)

                    # Step 2: Define angle offset (30 degrees in radians)
                    angle_offset_rad = math.radians(30)

                    # Step 3: Create the circular pattern
                    occurrence_patterns = main_assy_def.OccurrencePatterns
                    circular_pattern = occurrence_patterns.AddCircularPattern(
                        ParentComponents=clamp_collection_1,
                        AxisEntity=stump_y_axis_proxy,          # Rotation around the Y-axis of the stump
                        AxisEntityNaturalDirection=True,        # Right-hand rule
                        AngleOffset=angle_offset_rad,           # 30 degrees between instances
                        Count=12                                # Total 12 clamps
                    )
                    circular_pattern.OccurrencePatternElements.Item(3).Suppressed = True
                    circular_pattern.OccurrencePatternElements.Item(4).Suppressed = True

                    # -----------------------------------------------------

                    manhole_c_clamp_2 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    manhole_c_clamp_2.Grounded = False

                    j_bolt_2 = self.find_occurrence_recursive(occurrences=manhole_c_clamp_2.SubOccurrences, target_name="C CLAMP J BOLT M24x125Lg_02-GPF-11620 R4")
                    J_BOLT_MOUNTING_PLANE_proxy_2 = j_bolt_2.CreateGeometryProxy(j_bolt_2.Definition.WorkPlanes["J BOLT MOUNTING PLANE"])
                    J_BOLT_MOUNTING_PLANE_1_proxy_2 = j_bolt_2.CreateGeometryProxy(j_bolt_2.Definition.WorkPlanes["J BOLT MOUNTING PLANE_1"])
                    self.hide_workplanes_recursively(occurrence=manhole_c_clamp)
                    manhole_c_clamp_xy_plane_proxy_2 = manhole_c_clamp_2.CreateGeometryProxy(manhole_c_clamp_2.Definition.WorkPlanes["XY Plane"])

                    # Create rotation matrix and apply 70° rotation around Y vector
                    rotation_matrix = tg.CreateMatrix()
                    angle_rad = math.radians(70.0)
                    rotation_matrix.SetToRotation(angle_rad, y_vector_for_rotation, manhole_stump_origin_point)

                    # Rotate X axis
                    rotated_x_vector = x_unit_vector.Copy()
                    rotated_x_vector.TransformBy(rotation_matrix)

                    # Create new work plane
                    work_planes = main_assy_def.WorkPlanes
                    C_CLAMP_PLANE_70DEGREE = work_planes.AddFixed(manhole_stump_origin_point, rotated_x_vector, y_vector, False)
                    C_CLAMP_PLANE_70DEGREE.Name = "C_CLAMP_PLANE_70DEGREE"
                    C_CLAMP_PLANE_70DEGREE.Visible = False
                    C_CLAMP_PLANE_70DEGREE.Grounded = True

                    # Rotate X vector again by 90° around Y (from 70° → 160°)
                    rotation_matrix_90 = tg.CreateMatrix()
                    rotation_matrix_90.SetToRotation(math.radians(90.0), y_vector_for_rotation, manhole_stump_origin_point)

                    rotated_x_vector_160 = rotated_x_vector.Copy()
                    rotated_x_vector_160.TransformBy(rotation_matrix_90)

                    # Create new plane using rotated vector and same Y axis
                    C_CLAMP_PLANE_70_PLUS_90 = work_planes.AddFixed(
                        manhole_stump_origin_point,
                        rotated_x_vector_160,
                        y_vector,
                        False
                    )
                    C_CLAMP_PLANE_70_PLUS_90.Name = "C_CLAMP_PLANE_70_PLUS_90"
                    C_CLAMP_PLANE_70_PLUS_90.Visible = False
                    C_CLAMP_PLANE_70_PLUS_90.Grounded = True

                    clamp_collection_2 = inv_app.TransientObjects.CreateObjectCollection()
                    clamp_collection_2.Add(manhole_c_clamp_2)
                    
                    manhole_c_clamp_mate_70 = main_assy_def.Constraints.AddMateConstraint(manhole_c_clamp_xy_plane_proxy_2, C_CLAMP_PLANE_70DEGREE, 0, 24833, 24833, None, None)
                    manhole_c_clamp_mate_70 = main_assy_def.Constraints.AddMateConstraint(stump_xz_plane_proxy, J_BOLT_MOUNTING_PLANE_proxy_2, -3.7, 24833, 24833, None, None)
                    manhole_c_clamp_mate_70 = main_assy_def.Constraints.AddMateConstraint(C_CLAMP_PLANE_70_PLUS_90, J_BOLT_MOUNTING_PLANE_1_proxy_2, 31.0, 24833, 24833, None, None)

                    angle_offset_rad = math.radians(40)

                    # Step 3: Create the circular pattern
                    occurrence_patterns = main_assy_def.OccurrencePatterns
                    circular_pattern = occurrence_patterns.AddCircularPattern(
                        ParentComponents=clamp_collection_2,
                        AxisEntity=stump_y_axis_proxy,          # Rotation around the Y-axis of the stump
                        AxisEntityNaturalDirection=True,        # Right-hand rule
                        AngleOffset=angle_offset_rad,           # 30 degrees between instances
                        Count=2                                # Total 2 clamps
                    )
                    logger.info("End: mhcclamp (manhole_c_clamp)")
                    # print("manhole_c_clamp end")

                elif item.get("component") == 'nozzle_500_0_gasket_3':

                    # print("manhole_sight_glass_gasket start")
                    logger.info("Start: n1_500_0_gasket_3 (manhole_sight_glass_gasket)")

                    manhole_sight_glass_gasket = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    manhole_sight_glass_gasket.Grounded = False

                    manhole_sight_glass_gasket_y_axis_proxy = manhole_sight_glass_gasket.CreateGeometryProxy(manhole_sight_glass_gasket.Definition.WorkAxes["Y Axis"])
                    # manhole_cover_y_axis_proxy

                    manhole_sight_glass_gasket_xz_axis_proxy = manhole_sight_glass_gasket.CreateGeometryProxy(manhole_sight_glass_gasket.Definition.WorkPlanes["XZ Plane"])
                    TOP_PART = self.find_occurrence_recursive(occurrences=manhole_cover.SubOccurrences, target_name='24-GPF-0280 R0_TOP PART FOR 100NB PAD NOZZLE_DIN')
                    top_part_xz_proxy = TOP_PART.CreateGeometryProxy(TOP_PART.Definition.WorkPlanes["XZ Plane"]) # 41.5 mm

                    manhole_sight_glass_gasket_xy_axis_proxy = manhole_sight_glass_gasket.CreateGeometryProxy(manhole_sight_glass_gasket.Definition.WorkPlanes["XY Plane"])
                    # manhole_cover_xy_plane_proxy
                    
                    manhole_sight_glass_gasket_mate = main_assy_def.Constraints.AddMateConstraint2(manhole_sight_glass_gasket_y_axis_proxy, manhole_cover_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    manhole_sight_glass_gasket_flush_1 = main_assy_def.Constraints.AddFlushConstraint(manhole_sight_glass_gasket_xy_axis_proxy, manhole_cover_xy_plane_proxy, 0, None, None)
                    manhole_sight_glass_gasket_flush_2 = main_assy_def.Constraints.AddFlushConstraint(manhole_sight_glass_gasket_xz_axis_proxy, top_part_xz_proxy, -4.15, None, None)
                    self.hide_workplanes_recursively(occurrence=manhole_sight_glass_gasket)
                    logger.info("End: n1_500_0_gasket_3 (manhole_sight_glass_gasket)")
                    # print("manhole_sight_glass_gasket end")

                elif item.get("component") == 'springbalanceassembly':

                    # print("Start: spring_balance_assembly")
                    logger.info("Start: springbalanceassembly (spring_balance_assembly)")

                    # Check if required components exist
                    if manhole_cover is None or manhole_stump is None:
                        logger.warning("Skipping spring balance assembly: manhole_cover or manhole_stump not found")
                        print("Skipping spring_balance_assembly: manhole_cover or manhole_stump not available")
                        continue

                    spring_balance_assembly = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    spring_balance_assembly.Grounded = False

                    hing = self.find_occurrence_by_keyword_recursive(occurrences=manhole_cover.SubOccurrences, target_keyword="38131000-1001") #38131000-1001
                    if hing is None:
                        logger.warning("Skipping spring balance assembly constraints: hinge not found")
                        print("End: spring_balance_assembly (hinge not found)")
                        continue

                    hing_Spring_balance_Axis_proxy = hing.CreateGeometryProxy(hing.Definition.WorkAxes["Spring_balance_Axis"])

                    stump_yz_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["YZ Plane"])
                    spring_balance_assembly_axis_proxy = spring_balance_assembly.CreateGeometryProxy(spring_balance_assembly.Definition.WorkAxes["Spring_balance_Axis"])
                    spring_balance_assembly_xy_plane_proxy = spring_balance_assembly.CreateGeometryProxy(spring_balance_assembly.Definition.WorkPlanes["XY Plane"])
                    spring_balance_assembly_yz_plane_proxy = spring_balance_assembly.CreateGeometryProxy(spring_balance_assembly.Definition.WorkPlanes["YZ Plane"])

                    spring_balance_assembly_mate_1 = main_assy_def.Constraints.AddMateConstraint2(hing_Spring_balance_Axis_proxy, spring_balance_assembly_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    spring_balance_assembly_flush_1 = main_assy_def.Constraints.AddFlushConstraint(manhole_cover_yz_plane_proxy, spring_balance_assembly_yz_plane_proxy, 0, None, None)
                    spring_balance_assembly_angle_xy = main_assy_def.Constraints.AddAngleConstraint(manhole_cover_xy_plane_proxy, spring_balance_assembly_xy_plane_proxy, 0, 78593, None, None, None)
                    self.hide_workplanes_recursively(occurrence=spring_balance_assembly)

                    # print("End: spring_balance_assembly")
                    logger.info("End: springbalanceassembly (spring_balance_assembly)")
                
                elif item.get("component") == 'nozzle_500_0_toughenedglass_1':
                    # print("Start: manhole_sight_glass")
                    logger.info("Start: n1_500_0_toughenedglass_1 (manhole_sight_glass)")

                    manhole_sight_glass = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    manhole_sight_glass.Grounded = False

                    manhole_sight_glass_y_axis_proxy = manhole_sight_glass.CreateGeometryProxy(manhole_sight_glass.Definition.WorkAxes["Y Axis"])
                    manhole_sight_glass_xy_plane_proxy = manhole_sight_glass.CreateGeometryProxy(manhole_sight_glass.Definition.WorkPlanes["XY Plane"])
                    manhole_sight_glass_yz_plane_proxy = manhole_sight_glass.CreateGeometryProxy(manhole_sight_glass.Definition.WorkPlanes["YZ Plane"])
                    manhole_sight_glass_xz_plane_proxy = manhole_sight_glass.CreateGeometryProxy(manhole_sight_glass.Definition.WorkPlanes["XZ Plane"])
                    manhole_sight_glass_ass_plane_proxy = manhole_sight_glass.CreateGeometryProxy(manhole_sight_glass.Definition.WorkPlanes["ASSEMBLY PLANE"])
                    
                    SLIT_ENVELOPE = self.find_occurrence_recursive(occurrences=manhole_sight_glass_gasket.SubOccurrences, target_name="SLIT ENVELOPE")
                    gasket_ref_plane = SLIT_ENVELOPE.CreateGeometryProxy(SLIT_ENVELOPE.Definition.WorkPlanes["GASKET REF PLANE"])

                    manhole_sight_glass_mate1 = main_assy_def.Constraints.AddMateConstraint2(manhole_sight_glass_y_axis_proxy, manhole_cover_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    manhole_sight_glass_mate2 = main_assy_def.Constraints.AddMateConstraint2(manhole_sight_glass_xz_plane_proxy, gasket_ref_plane, 0, 24833, 24833, 115459, None, None)
                    self.hide_workplanes_recursively(occurrence=manhole_sight_glass)
                    
                    logger.info("End: n1_500_0_toughenedglass_1 (manhole_sight_glass)")
                    # print("End: manhole_sight_glass")
                
                elif item.get("component") == 'nozzle_500_0_sight_light_glass_flange_1':
                    # print("Start: manhole_sight_flange")
                    logger.info("Start: n1_500_0_sight/light_glass_flange_1 (manhole_sight_flange)")
                    manhole_sight_flange = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    manhole_sight_flange.Grounded = False

                    manhole_sight_flange_y_axis_proxy = manhole_sight_flange.CreateGeometryProxy(manhole_sight_flange.Definition.WorkAxes["Y Axis"])
                    manhole_sight_flange_fastener_assly_axis_proxy = manhole_sight_flange.CreateGeometryProxy(manhole_sight_flange.Definition.WorkAxes["Fastener Assly Axis"])
                    manhole_sight_flange_ass_plane_proxy = manhole_sight_flange.CreateGeometryProxy(manhole_sight_flange.Definition.WorkPlanes["ASSEMBLY PLANE"])
                    manhole_sight_flange_xy_plane_proxy = manhole_sight_flange.CreateGeometryProxy(manhole_sight_flange.Definition.WorkPlanes["XY PLANE"])
                    manhole_sight_flange_xz_plane_proxy = manhole_sight_flange.CreateGeometryProxy(manhole_sight_flange.Definition.WorkPlanes["XZ PLANE"])

                    manhole_sight_flange_mate1 = main_assy_def.Constraints.AddMateConstraint2(manhole_sight_flange_y_axis_proxy, manhole_sight_glass_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    manhole_sight_glass_gasket_mate_1 = main_assy_def.Constraints.AddMateConstraint(manhole_sight_glass_ass_plane_proxy, manhole_sight_flange_ass_plane_proxy, -0.3, 24833, 24833, None, None)
                    # manhole_sight_glass_gasket_flush_2 = main_assy_def.Constraints.AddMateConstraint(manhole_sight_glass_ass_plane_proxy, manhole_sight_flange_ass_plane_proxy, -0.3, None, None)
                    manhole_sight_glass_gasket_mate_2 = main_assy_def.Constraints.AddMateConstraint(manhole_cover_xy_plane_proxy, manhole_sight_flange_xy_plane_proxy, 0, 24833, 24833, None, None)
                    # manhole_sight_glass_gasket_flush_1 = main_assy_def.Constraints.AddMateConstraint(manhole_cover_xy_plane_proxy, manhole_sight_flange_xy_plane_proxy, 0, None, None)
                    self.hide_workplanes_recursively(occurrence=manhole_sight_flange)

                    logger.info("End: n1_500_0_sight/light_glass_flange_1 (manhole_sight_flange)")
                    # print("End: manhole_sight_flange")
                
                elif item.get("component") == 'nozzle_500_0_washer_1':
                        # print("Start: manhole_washer")
                        logger.info("Start: n1_500_0_washer_1 (manhole_washer)")
                        comp = 'manhole_washer'
                        comp_splits = comp.split('_')
                        nozzle_name = comp_splits[0]
                        nozzle_size = comp_splits[1]

                        manhole_washer = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                        manhole_washer.Grounded = False

                        manhole_washer_y_axis_proxy = manhole_washer.CreateGeometryProxy(manhole_washer.Definition.WorkAxes["Y Axis"])
                        manhole_washer_xy_plane_proxy = manhole_washer.CreateGeometryProxy(manhole_washer.Definition.WorkPlanes["XY PLANE"])
                        manhole_washer_xz_plane_proxy = manhole_washer.CreateGeometryProxy(manhole_washer.Definition.WorkPlanes["XZ PLANE"])
                        manhole_washer_fastner_assly_plane_proxy = manhole_washer.CreateGeometryProxy(manhole_washer.Definition.WorkPlanes["Fastener Assly Plane"])

                        manhole_washer_mate_1 = main_assy_def.Constraints.AddMateConstraint2(manhole_washer_y_axis_proxy, manhole_sight_flange_fastener_assly_axis_proxy, 0, 24833, 24833, 115459, None, None)
                        manhole_washer_mate_2 = main_assy_def.Constraints.AddMateConstraint(manhole_washer_fastner_assly_plane_proxy, manhole_sight_flange_xz_plane_proxy, 0, 24833, 24833, None, None)
                        self.hide_workplanes_recursively(occurrence=manhole_washer)
                        logger.info("End: n1_500_0_washer_1 (manhole_washer)")

                elif item.get("component") == 'nozzle_500_0_bolt_stud_1':
                        # print("Start: manhole_fastener")
                        logger.info("Start: n1_500_0_bolt/stud_1 (manhole_fastener)")
                        comp = 'manhole_fastener'
                        comp_splits = comp.split('_')
                        nozzle_name = comp_splits[0]
                        nozzle_size = comp_splits[1]

                        manhole_fastener = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                        manhole_fastener.Grounded = False

                        manhole_fastener_y_axis_proxy = manhole_fastener.CreateGeometryProxy(manhole_fastener.Definition.WorkAxes["Y Axis"])
                        manhole_fastener_xy_plane_proxy = manhole_fastener.CreateGeometryProxy(manhole_fastener.Definition.WorkPlanes["XY PLANE"])
                        manhole_fastener_xz_plane_proxy = manhole_fastener.CreateGeometryProxy(manhole_fastener.Definition.WorkPlanes["XZ PLANE"])

                        manhole_fastener_mate_1 = main_assy_def.Constraints.AddMateConstraint2(manhole_fastener_y_axis_proxy, manhole_washer_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                        manhole_washer_mate_2 = main_assy_def.Constraints.AddMateConstraint(manhole_fastener_xz_plane_proxy, manhole_washer_xz_plane_proxy, 0, 24833, 24833, None, None)


                        manhole_fastener_collection = inv_app.TransientObjects.CreateObjectCollection()
                        manhole_fastener_collection.Add(manhole_washer)
                        manhole_fastener_collection.Add(manhole_fastener)

                        angle = math.radians(360/8)

                        occurrence_patterns = main_assy_def.OccurrencePatterns
                        circular_pattern = occurrence_patterns.AddCircularPattern(
                            ParentComponents=manhole_fastener_collection,
                            AxisEntity=manhole_sight_flange_y_axis_proxy,
                            AxisEntityNaturalDirection=True,
                            AngleOffset=angle,
                            Count=8
                        )

                        self.hide_workplanes_recursively(occurrence=manhole_fastener)
                        logger.info("End: n1_500_0_bolt/stud_1 (manhole_fastener)")

                elif item.get("component") == 'coc_gasket':
                    # print("Start: coc_gasket")
                    logger.info("Start: coc_gasket")
                    coc_gasket = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    coc_gasket.Grounded = False
                    coc_gasket_y_axis_proxy = coc_gasket.CreateGeometryProxy(coc_gasket.Definition.WorkAxes["Y Axis"])
                    coc_gasket_xy_plane_proxy = coc_gasket.CreateGeometryProxy(coc_gasket.Definition.WorkPlanes["XY PLANE"])
                    coc_gasket_xz_plane_proxy = coc_gasket.CreateGeometryProxy(coc_gasket.Definition.WorkPlanes["XZ PLANE"])

                    coc_body_flange = self.find_occurrence_by_keyword_recursive(occurrences=monoblock.SubOccurrences, target_keyword="3802CSEQ-0002")
                    coc_body_flange_y_axis_proxy = coc_body_flange.CreateGeometryProxy(coc_body_flange.Definition.WorkAxes["Y Axis"])
                    coc_body_flange_xy_plane_proxy = coc_body_flange.CreateGeometryProxy(coc_body_flange.Definition.WorkPlanes["XY PLANE"])
                    coc_body_flange_xz_plane_proxy = coc_body_flange.CreateGeometryProxy(coc_body_flange.Definition.WorkPlanes["XZ PLANE"])

                    coc_gasket_mate1 = main_assy_def.Constraints.AddMateConstraint2(coc_gasket_y_axis_proxy, coc_body_flange_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    coc_gasket_flush_1 = main_assy_def.Constraints.AddFlushConstraint(coc_gasket_xy_plane_proxy, coc_body_flange_xy_plane_proxy, 0, None, None)
                    coc_gasket_flush_2 = main_assy_def.Constraints.AddFlushConstraint(coc_gasket_xz_plane_proxy, coc_body_flange_xz_plane_proxy, 0, None, None)
                    self.hide_workplanes_recursively(occurrence=coc_gasket)
                    logger.info("End: coc_gasket")
                    # print("End: coc_gasket")

                elif item.get("component") == 'coc':
                    logger.info(f"Start: {item.get("component")}")
                    if coc_gasket is None:
                        print("Warning: coc_gasket not found, skipping coc constraints")
                        continue
                    coc = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    coc.Grounded = False
                    coc_y_axis_proxy = coc.CreateGeometryProxy(coc.Definition.WorkAxes["Y Axis"])
                    coc_xy_plane_proxy = coc.CreateGeometryProxy(coc.Definition.WorkPlanes["XY PLANE"])
                    coc_xz_plane_proxy = coc.CreateGeometryProxy(coc.Definition.WorkPlanes["XZ PLANE"])
                    coc_yz_plane_proxy = coc.CreateGeometryProxy(coc.Definition.WorkPlanes["YZ PLANE"])

                    ENVELOPE_BODY_FLANGE = self.find_occurrence_recursive(occurrences=coc_gasket.SubOccurrences, target_name='DN800_875_800_12.1_ROUND ENVELOPE_BODY FLANGE')
                    coc_gasket_ref_plane = ENVELOPE_BODY_FLANGE.CreateGeometryProxy(ENVELOPE_BODY_FLANGE.Definition.WorkPlanes["GASKET REF PLANE"])

                    coc_mate1 = main_assy_def.Constraints.AddMateConstraint2(coc_y_axis_proxy, coc_gasket_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    coc_mate2 = main_assy_def.Constraints.AddMateConstraint(coc_xy_plane_proxy, coc_gasket_xy_plane_proxy, 0, 24833, 24833, None, None)
                    coc_flush_2 = main_assy_def.Constraints.AddFlushConstraint(coc_xz_plane_proxy, coc_gasket_ref_plane, 0, None, None)
                    self.hide_workplanes_recursively(occurrence=coc)

                    logger.info(f"End: {item.get("component")}")

                elif item.get("component") == 'bfcclamp':

                    logger.info(f"Start: {item.get("component")} (coc_c_clamp)")
                    if coc is None or coc_body_flange is None:
                        print("Warning: coc or coc_body_flange not found, skipping bfcclamp constraints")
                        continue
                    coc_c_clamp = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    coc_c_clamp.Grounded = False
                    coc_c_clamp_xy_plane_proxy = coc_c_clamp.CreateGeometryProxy(coc_c_clamp.Definition.WorkPlanes["XY PLANE"])

                    j_bolt = self.find_occurrence_recursive(occurrences=coc_c_clamp.SubOccurrences, target_name="SA 307 GR B_C CLAMP J BOLT M24x100Lg_02-GPF-11620 R4")
                    J_BOLT_MOUNTING_PLANE_proxy = j_bolt.CreateGeometryProxy(j_bolt.Definition.WorkPlanes["J BOLT MOUNTING PLANE"])
                    J_BOLT_MOUNTING_PLANE_1_proxy = j_bolt.CreateGeometryProxy(j_bolt.Definition.WorkPlanes["J BOLT MOUNTING PLANE_1"])

                    coc_c_clamp_mate_1 = main_assy_def.Constraints.AddMateConstraint(coc_c_clamp_xy_plane_proxy, coc_xy_plane_proxy, 0, 24833, 24833, None, None)
                    coc_c_clamp_mate_2 = main_assy_def.Constraints.AddMateConstraint(coc_body_flange_xz_plane_proxy, J_BOLT_MOUNTING_PLANE_proxy, -4.1, 24833, 24833, None, None)
                    coc_c_clamp_mate_3 = main_assy_def.Constraints.AddMateConstraint(coc_yz_plane_proxy, J_BOLT_MOUNTING_PLANE_1_proxy, 44.5, 24833, 24833, None, None)

                    coc_c_clamp_collection = inv_app.TransientObjects.CreateObjectCollection()
                    coc_c_clamp_collection.Add(coc_c_clamp)

                    angle = math.radians(360/24)

                    occurrence_patterns = main_assy_def.OccurrencePatterns
                    circular_pattern = occurrence_patterns.AddCircularPattern(
                        ParentComponents=coc_c_clamp_collection,
                        AxisEntity=coc_y_axis_proxy,            # Rotation around the Y-axis of the stump
                        AxisEntityNaturalDirection=True,        # Right-hand rule
                        AngleOffset=angle,                      # 15 degrees between instances
                        Count=24                                # Total 24 clamps
                    )
                    self.hide_workplanes_recursively(occurrence=coc_c_clamp)

                    logger.info(f"End: {item.get("component")} (coc_c_clamp)")
                
                elif item.get("component") == 'nozzle_200_d_gasket_1' or item.get("component") == 'nozzle_200_d_gasket':

                    logger.info(f"Start: {item.get("component")} (center_nozzle_gasket)")
                    center_nozzle_gasket = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    center_nozzle_gasket.Grounded = False
                    center_nozzle_gasket_y_axis_proxy = center_nozzle_gasket.CreateGeometryProxy(center_nozzle_gasket.Definition.WorkAxes["Y Axis"])
                    center_nozzle_gasket_xy_plane_proxy = center_nozzle_gasket.CreateGeometryProxy(center_nozzle_gasket.Definition.WorkPlanes["XY PLANE"])
                    center_nozzle_gasket_xz_plane_proxy = center_nozzle_gasket.CreateGeometryProxy(center_nozzle_gasket.Definition.WorkPlanes["XZ PLANE"])

                    coc_stub_end = self.find_occurrence_by_keyword_recursive(occurrences=coc.SubOccurrences, target_keyword="3801CSEQ-0272")
                    coc_stub_end_y_axis_proxy = coc_stub_end.CreateGeometryProxy(coc_stub_end.Definition.WorkAxes["Y Axis"])
                    coc_stub_end_xy_plane_proxy = coc_stub_end.CreateGeometryProxy(coc_stub_end.Definition.WorkPlanes["XY PLANE"])
                    coc_stub_end_xz_plane_proxy = coc_stub_end.CreateGeometryProxy(coc_stub_end.Definition.WorkPlanes["XZ PLANE"])

                    center_nozzle_gasket_mate_1 = main_assy_def.Constraints.AddMateConstraint2(coc_stub_end_y_axis_proxy, center_nozzle_gasket_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    center_nozzle_gasket_flush_1 = main_assy_def.Constraints.AddFlushConstraint(coc_stub_end_xy_plane_proxy, center_nozzle_gasket_xy_plane_proxy, 0, None, None)
                    center_nozzle_gasket_flush_2 = main_assy_def.Constraints.AddFlushConstraint(coc_stub_end_xz_plane_proxy, center_nozzle_gasket_xz_plane_proxy, 0, None, None)
                    self.hide_workplanes_recursively(occurrence=center_nozzle_gasket)

                    logger.info(f"End: {item.get("component")} (center_nozzle_gasket)")

                elif item.get("component") == 'driveassembly':

                    logger.info(f"Start: {item.get("component")}")
                    # DBR-500-01-00 R1_CE_5KL_6.3KL_STD
                    drive_assembly = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    drive_assembly.Grounded = False
                    drive_assembly_y_axis_proxy = drive_assembly.CreateGeometryProxy(drive_assembly.Definition.WorkAxes["Y Axis"])
                    drive_assembly_xy_plane_proxy = drive_assembly.CreateGeometryProxy(drive_assembly.Definition.WorkPlanes["XY PLANE"])
                    drive_assembly_xz_plane_proxy = drive_assembly.CreateGeometryProxy(drive_assembly.Definition.WorkPlanes["XZ PLANE"])

                    main_xy_plane = main_assy_def.WorkPlanes["XY Plane"]

                    drive_base_ring = self.find_occurrence_recursive(occurrences=drive_assembly.SubOccurrences, target_name="DBR-500-01-00 R1_CE_5KL_6.3KL_STD")
                    DBR_MOUNTING_PLANE_proxy = drive_base_ring.CreateGeometryProxy(drive_base_ring.Definition.WorkPlanes["DBR_MOUNTING"])

                    drive_assembly_mate_1 = main_assy_def.Constraints.AddMateConstraint2(drive_assembly_y_axis_proxy, coc_stub_end_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    drive_assembly_flush_1 = main_assy_def.Constraints.AddFlushConstraint(drive_assembly_xy_plane_proxy, main_xy_plane, 0, None, None)
                    drive_assembly_flush_2 = main_assy_def.Constraints.AddFlushConstraint(coc_stub_end_xz_plane_proxy, DBR_MOUNTING_PLANE_proxy, 2.1, None, None)
                    self.hide_workplanes_recursively(occurrence=drive_assembly)

                    logger.info(f"End: {item.get("component")}")

                elif item.get("component") == 'shaftclosure':

                    logger.info(f"Start: {item.get("component")} (mechanical_seal)")
                    mechanical_seal = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                    mechanical_seal.Grounded = False
                    mechanical_seal_y_axis_proxy = mechanical_seal.CreateGeometryProxy(mechanical_seal.Definition.WorkAxes["Y Axis"])
                    mechanical_seal_fastener_assly_axis_proxy = mechanical_seal.CreateGeometryProxy(mechanical_seal.Definition.WorkAxes["Fastener Assly Axis for seal"])
                    mechanical_seal_xy_plane_proxy = mechanical_seal.CreateGeometryProxy(mechanical_seal.Definition.WorkPlanes["XY PLANE"])
                    mechanical_seal_xz_plane_proxy = mechanical_seal.CreateGeometryProxy(mechanical_seal.Definition.WorkPlanes["XZ PLANE"])
                    mechanical_seal_fast_plane_proxy = mechanical_seal.CreateGeometryProxy(mechanical_seal.Definition.WorkPlanes["Fastener mounting plane for seal"])

                    pad_plate = self.find_occurrence_by_keyword_recursive(occurrences=drive_assembly.SubOccurrences, target_keyword="7052-0019")
                    pad_plate_xz_plane_proxy = pad_plate.CreateGeometryProxy(pad_plate.Definition.WorkPlanes["XZ PLANE"])

                    mechanical_seal_mate_1 = main_assy_def.Constraints.AddMateConstraint2(main_y_axis, mechanical_seal_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                    mechanical_seal_flush_1 = main_assy_def.Constraints.AddFlushConstraint(mechanical_seal_xz_plane_proxy, pad_plate_xz_plane_proxy, -5.3, None, None)
                    mechanical_seal_mate_2 = main_assy_def.Constraints.AddMateConstraint(mechanical_seal_xy_plane_proxy, main_xy_plane, 0, 24833, 24833, None, None)
                    self.hide_workplanes_recursively(occurrence=mechanical_seal)

                    logger.info(f"End: {item.get("component")} (mechanical_seal)")

                # Start: mechanical_seal_washer
                elif item.get("component") == 'mechanical_seal_washer':

                        logger.info(f"Start: {item.get("component")}")
                        comp = 'mechanical_seal_washer'
                        comp_splits = comp.split('_')
                        nozzle_name = comp_splits[0]
                        nozzle_size = comp_splits[1]

                        mechanical_seal_washer = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                        mechanical_seal_washer.Grounded = False

                        mechanical_seal_washer_y_axis_proxy = mechanical_seal_washer.CreateGeometryProxy(mechanical_seal_washer.Definition.WorkAxes["Y Axis"])
                        mechanical_seal_washer_xy_plane_proxy = mechanical_seal_washer.CreateGeometryProxy(mechanical_seal_washer.Definition.WorkPlanes["XY PLANE"])
                        mechanical_seal_washer_xz_plane_proxy = mechanical_seal_washer.CreateGeometryProxy(mechanical_seal_washer.Definition.WorkPlanes["XZ PLANE"])
                        # mechanical_seal_washer_fastner_assly_plane_proxy = mechanical_seal_washer.CreateGeometryProxy(mechanical_seal_washer.Definition.WorkPlanes["Fastener Assly Plane"])

                        mechanical_seal_washer_mate_1 = main_assy_def.Constraints.AddMateConstraint2(mechanical_seal_washer_y_axis_proxy, mechanical_seal_fastener_assly_axis_proxy, 0, 24833, 24833, 115459, None, None)
                        manhole_washer_mate_2 = main_assy_def.Constraints.AddMateConstraint(mechanical_seal_washer_xz_plane_proxy, mechanical_seal_fast_plane_proxy, 0.35, 24833, 24833, None, None)
                        self.hide_workplanes_recursively(occurrence=mechanical_seal_washer)

                        logger.info(f"End: {item.get("component")}")
                # End: mechanical_seal_washer
                
                # Start: mechanical_seal_fastener
                elif item.get("component") == 'mechanical_seal_fastener':

                        logger.info(f"Start: {item.get("component")}")
                        comp = 'mechanical_seal_fastener'
                        comp_splits = comp.split('_')
                        nozzle_name = comp_splits[0]
                        nozzle_size = comp_splits[1]

                        mechanical_seal_fastener = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                        mechanical_seal_fastener.Grounded = False

                        mechanical_seal_fastener_y_axis_proxy = mechanical_seal_fastener.CreateGeometryProxy(mechanical_seal_fastener.Definition.WorkAxes["Y Axis"])
                        mechanical_seal_fastener_xy_plane_proxy = mechanical_seal_fastener.CreateGeometryProxy(mechanical_seal_fastener.Definition.WorkPlanes["XY PLANE"])
                        mechanical_seal_fastener_xz_plane_proxy = mechanical_seal_fastener.CreateGeometryProxy(mechanical_seal_fastener.Definition.WorkPlanes["XZ PLANE"])

                        mechanical_seal_fastener_mate_1 = main_assy_def.Constraints.AddMateConstraint2(mechanical_seal_fastener_y_axis_proxy, mechanical_seal_washer_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                        mechanical_seal_fastener_mate_2 = main_assy_def.Constraints.AddMateConstraint(mechanical_seal_fastener_xz_plane_proxy, mechanical_seal_washer_xz_plane_proxy, 0, 24833, 24833, None, None)

                        self.hide_workplanes_recursively(occurrence=mechanical_seal_fastener)

                        mechanical_seal_fastener_collection = inv_app.TransientObjects.CreateObjectCollection()
                        mechanical_seal_fastener_collection.Add(mechanical_seal_washer)
                        mechanical_seal_fastener_collection.Add(mechanical_seal_fastener)

                        angle = math.radians(360/8)

                        occurrence_patterns = main_assy_def.OccurrencePatterns
                        circular_pattern = occurrence_patterns.AddCircularPattern(
                            ParentComponents=mechanical_seal_fastener_collection,
                            AxisEntity=mechanical_seal_y_axis_proxy,
                            AxisEntityNaturalDirection=True,
                            AngleOffset=angle,
                            Count=8
                        )

                        logger.info(f"End: {item.get("component")}")
                # End: mechanical_seal_fastener

                # Start: Agitator
                elif item.get("component") == 'agitator':

                        logger.info(f"Start: {item.get("component")}")
                        agitator = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                        agitator.Grounded = False
                        agitator_y_axis_proxy = agitator.CreateGeometryProxy(agitator.Definition.WorkAxes["Y Axis"])
                        agitator_xy_plane_proxy = agitator.CreateGeometryProxy(agitator.Definition.WorkPlanes["XY PLANE"])
                        agitator_xz_plane_proxy = agitator.CreateGeometryProxy(agitator.Definition.WorkPlanes["XZ PLANE"])

                        pre_machine_connected_head = self.find_occurrence_by_keyword_recursive(occurrences=agitator.SubOccurrences, target_keyword="5566-0091")
                        pre_machine_connected_head_xz_plane_proxy = pre_machine_connected_head.CreateGeometryProxy(pre_machine_connected_head.Definition.WorkPlanes["XZ PLANE"])

                        distance = 54.0
                        add_distance = 0.50
                        total_distance = distance + add_distance
                        agitator_mate_1 = main_assy_def.Constraints.AddMateConstraint2(main_y_axis, agitator_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                        agitator_flush_1 = main_assy_def.Constraints.AddFlushConstraint(main_xy_plane, agitator_xy_plane_proxy, 0, None, None)
                        agitator_flush_2 = main_assy_def.Constraints.AddFlushConstraint(DBR_MOUNTING_PLANE_proxy, pre_machine_connected_head_xz_plane_proxy, 54.5, None, None)
                        self.hide_workplanes_recursively(occurrence=agitator)

                        logger.info(f"End: {item.get("component")}")
                # End: Agitator

                # Vessel nozzles (nozzle_{size}_{degree}_{fitting}) are handled by
                # dynamic handlers dispatched via _get_component_handler()

            so_no = model_details['details']['sono']
            capacity = model_details['details']['capacity']
            reactor = model_details['details']['reactor']
            model = model_details['details']['model']
            so_no_splits = so_no.split("_")
            file_name = f"{so_no_splits[0]}_{model}"
            # "D:\\Vault\\Designs\\ASSEMBLY\\SO NO"
            folder_name = f"D:\\Vault\\Designs\\ASSEMBLY\\SO NO\\{so_no}"
            file_path = f"{folder_name}\\{file_name}.iam"
            inv_doc = inv_app.ActiveDocument
            inv_doc.SaveAs(file_path, True)
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
    
    def find_occurrence_recursive(self, occurrences, target_name):
        target_lower = target_name.lower()  # Case-insensitive comparison
        for occ in occurrences:
            name = occ.Name.lower()
            display_name = occ.Definition.Document.DisplayName.lower()
            if target_lower in name or target_lower in display_name:
                return occ
            if hasattr(occ, "SubOccurrences") and occ.SubOccurrences.Count > 0:
                found = self.find_occurrence_recursive(occ.SubOccurrences, target_name)
                if found:
                    return found
        return None
    
    def find_occurrence_by_keyword_recursive(self, occurrences, target_keyword):
        target_lower = target_keyword.lower()  # Normalize for case-insensitive matching

        for occ in occurrences:
            try:
                # Confirm the occurrence has a valid Definition
                if not hasattr(occ, 'Definition') or occ.Definition is None:
                    continue

                # Confirm the Definition has a Document
                if not hasattr(occ.Definition, 'Document') or occ.Definition.Document is None:
                    continue

                # Get the keyword field from Summary Information
                keywords = occ.Definition.Document.PropertySets['Summary Information']['KeyWords'].Value
                if keywords and target_lower in keywords.lower():
                    return occ  # ✅ Found matching occurrence

            except Exception:
                pass  # Ignore issues and continue

            # Recurse into sub-occurrences if this is a subassembly
            if hasattr(occ, "SubOccurrences") and occ.SubOccurrences.Count > 0:
                found = self.find_occurrence_by_keyword_recursive(occ.SubOccurrences, target_keyword)
                if found:
                    return found

        return None  # ❌ No match found

    def find_occurrences_by_expression(self, sub_occurrences, target_expression):
        """
        Search sub-occurrences for components containing a parameter with the given expression.
        
        Args:
            sub_occurrences: Inventor.ComponentOccurrences object
            target_expression (str): The expression string to match (case-insensitive)

        Returns:
            List of matching ComponentOccurrence objects
        """
        matching = []
        
        def format_number(s):
            """Formats a string to a float with one or two decimal points."""
            if s == '0':
                return f"{0.0:.1f}"
            try:
                # Convert to a float and format to two decimal places
                num = float(s)
                return f"{num:.2f}"
            except ValueError:
                return "Invalid input"

        def recursive_search(occurrences):
            for occ in occurrences:
                try:
                    
                    if occ.Name == 'CT-1950-20-STD-IH-00 R0_SWAGGED TOP DISHED END_STD_CE-5-6.3KL:1' or 'CLEAT' in occ.Name or 'LL-053' in occ.Name:
                        continue

                    definition = occ.Definition

                    # Check only PartDocuments (DocumentType = 1)
                    if not hasattr(definition, 'Parameters') or occ.Definition is None:
                        continue
                    all_params = definition.Parameters.ModelParameters
                    for param in all_params:
                        expr = param.Expression.strip()
                        ori_val = param.Value
                        ori_unit = param.Units
                        val = float(format_number(target_expression))
                        print("Original Value: ", ori_val)
                        print("Original Unit: ", ori_unit)
                        if ori_val == val and ori_unit == 'deg' :
                            print(f"[MATCH] Found in {occ.Name} — Expression: {expr}")
                            matching.append(occ)
                            break  

                        # if expr.lower() == target_expression.lower() :
                        #     print(f"[MATCH] Found in {occ.Name} — Expression: {expr}")
                        #     matching.append(occ)
                        #     break  # Stop checking other params in this occurrence
                    

                    # Confirm the occurrence has a valid Definition
                    if not hasattr(occ, 'SubOccurrences') or occ.Definition is None:
                        continue
                    # Go deeper into nested occurrences if they exist
                    # if occ.SubOccurrences.Count > 0:
                    #     recursive_search(occ.SubOccurrences)

                except Exception as e:
                    print(f"Error processing {occ.Name}: {e}")

        recursive_search(sub_occurrences)
        return matching

    def find_named_workplane_in_occurrence(self, occurrences, target_name):
        for occurrence in occurrences:
            try:
                # Check if the occurrence has a Definition with WorkPlanes
                if hasattr(occurrence, 'Definition') and hasattr(occurrence.Definition, 'WorkPlanes'):
                    wp = occurrence.Definition.WorkPlanes[target_name]
                    if wp is not None:
                        return occurrence.CreateGeometryProxy(wp)

                # Recurse into child occurrences if any
                if hasattr(occurrence.Definition, 'Occurrences'):
                    result = self.find_named_workplane_in_occurrence(occurrence.Definition.Occurrences, target_name)
                    if result:
                        return result
            except Exception:
                # Skip problematic or invalid occurrences
                pass

        return None

    def add_axes_for_holes(self, tg, occ, main_assy_def, name_axes=True, construction=False):
        """
        Adds Work Axes through the centers of all hole features from a part occurrence
        in the assembly context. Correctly handles proxies and vector transforms.
        """
        comp_def = occ.Definition
        work_axes = main_assy_def.WorkAxes

        hole = comp_def.Features.HoleFeatures['Hole 1']

        # Find the main cylindrical face
        cyl_face = next((f for f in hole.Faces if f.SurfaceType == 5891), None)
        if not cyl_face:
            print(f"⚠️ No cylindrical face for hole '{hole.Name}'. Skipping.")

        cyl_surf = cyl_face.Geometry
        axis_vec_model = cyl_surf.AxisVector

        # Validate axis vector
        # if axis_vec_model.Length < 1e-9:
        #     print(f"⚠️ Axis vector for hole '{hole.Name}' is invalid. Skipping.")

        # Get the hole center point (model object)
        if hole.HoleCenterPoints.Count == 0:
            print(f"⚠️ No center point for hole '{hole.Name}'. Skipping.")

        hole_center_pt_model = hole.HoleCenterPoints.Item(1)

        # Create geometry proxy in assembly
        try:
            point_proxy = occ.CreateGeometryProxy(hole_center_pt_model)
        except Exception as e:
            print(f"❌ Failed to create geometry proxy for point of '{hole.Name}': {e}")

        # Transform axis vector to assembly context
        try:
            axis_vector_asm = tg.CreateUnitVector(axis_vec_model.X, axis_vec_model.Y, axis_vec_model.Z)
            axis_vector_asm.TransformBy(occ.Transformation)
        except Exception as e:
            print(f"❌ Failed to transform axis vector for '{hole.Name}': {e}")

        # Add the work axis
        try:
            work_axis = work_axes.AddFixed(point_proxy, axis_vector_asm, construction)
            if name_axes:
                work_axis.Name = f"{occ.Name}_{hole.Name}_Axis"
            print(f"✅ Work axis created in assembly for '{occ.Name}:{hole.Name}'")
        except Exception as e:
            print(f"❌ Inventor failed to create WorkAxis for '{occ.Name}:{hole.Name}': {e}")

    def hide_workplanes_recursively(self, occurrence):
        """
        Recursively hide all work planes in an occurrence and its sub-occurrences.

        Args:
            occurrence: Inventor ComponentOccurrence
        """
        try:
            definition = getattr(occurrence, "Definition", None)
            if definition is None:
                return

            # Hide WorkPlanes via proxy
            if hasattr(definition, "WorkPlanes") and definition.WorkPlanes is not None:
                for plane in definition.WorkPlanes:
                    try:
                        # Create the proxy in the context of the assembly occurrence
                        plane_proxy = occurrence.CreateGeometryProxy(plane)
                        plane_proxy.Visible = False
                    except Exception as e:
                        # Log but continue - some planes may not support visibility changes
                        logger.debug(f"Could not hide workplane in '{getattr(occurrence, 'Name', 'Unknown')}': {e}")

            # Recurse into SubOccurrences (if any)
            if hasattr(occurrence, "SubOccurrences") and occurrence.SubOccurrences is not None:
                for subOcc in occurrence.SubOccurrences:
                    self.hide_workplanes_recursively(occurrence=subOcc)

        except Exception as e:
            logger.warning(f"Error hiding workplanes in occurrence '{getattr(occurrence, 'Name', 'Unknown')}': {e}")

    def get_all_parameters_recursively(self, sub_occurrences):
        """
        Recursively collects parameter names and values from all occurrences.

        Args:
            sub_occurrences: Inventor.ComponentOccurrences collection

        Returns:
            List[Dict[str, Any]]: [
                {"Occurrence": "Part1:1", "ParameterName": "Width", "Value": 150.0},
                {"Occurrence": "Part1:1", "ParameterName": "Height", "Value": 200.0},
                ...
            ]
        """
        results = []

        def recursive_collect(occurrences):
            for occ in occurrences:
                try:
                    definition = occ.Definition
                    if not hasattr(definition, 'Parameters'):
                        continue  # skip if no parameters (like constraints-only or invalid occurrences)

                    # Collect all parameters (Model + User + Reference)
                    for param in definition.Parameters:
                        try:
                            results.append({
                                "Occurrence": occ.Name,
                                "ParameterName": param.Name,
                                "Value": param.Value  # already numeric (in document units)
                            })
                        except Exception as e:
                            logger.debug(f"Could not read parameter in {occ.Name}: {e}")
                            continue

                    # Recurse into sub-assemblies if any
                    if hasattr(definition, 'Occurrences') and definition.Occurrences.Count > 0:
                        recursive_collect(definition.Occurrences)

                except Exception as e:
                    logger.warning(f"Error collecting parameters from {occ.Name}: {e}")

        recursive_collect(sub_occurrences)
        return results

    def get_work_axis(self, work_axes, axis_name):
        for axis in work_axes:
            if axis_name.lower() in axis.Name.lower():
                return axis
        return None

    def get_work_plane(self, work_planes, plane_name):
        for plane in work_planes:
            if plane_name.lower() in plane.Name.lower():
                return plane
        return None

    def get_work_plane_by_degree(self, work_planes, target_degree, tolerance=1.0, exclude_planes=None):
        """
        Find a work plane by its rotational angle around the Y-axis.

        The angle is calculated from the X and Z components of the plane normal
        using atan2 to get the full 0-360 degree range.

        Args:
            work_planes: Collection of work planes to search
            target_degree: Target rotation angle in degrees (0-360)
            tolerance: Acceptable difference in degrees (default 1.0)
            exclude_planes: List of plane Names to skip (already used)

        Returns:
            WorkPlane object if found, None otherwise
        """
        if exclude_planes is None:
            exclude_planes = []

        target_deg = float(target_degree) % 360  # Normalize to 0-360

        for plane in work_planes:
            try:
                # Skip if already used
                plane_name = getattr(plane, 'Name', None)
                if plane_name and plane_name in exclude_planes:
                    continue

                normal = plane.Plane.Normal

                # Calculate rotational angle around Y-axis (azimuthal angle in XZ plane)
                angle_rad = math.atan2(normal.X, normal.Z)
                angle_deg = math.degrees(angle_rad)

                # Normalize to 0-360 range
                if angle_deg < 0:
                    angle_deg += 360

                # Compare using tolerance (handle wrap-around at 360/0)
                diff = abs(angle_deg - target_deg)
                if diff > 180:
                    diff = 360 - diff

                if diff <= tolerance:
                    return plane

            except Exception as e:
                logger.debug(
                    f"Could not evaluate plane '{getattr(plane, 'Name', '?')}': {e}"
                )
                continue

        return None

    def get_y_parallel_axis_from_plane(self,
        work_axes,
        plane,
        ref_point=None,
        point_tol=1e-3,
        dir_tol=1e-6
    ):
        """
        Find a Y-parallel WorkAxis that lies in the given WorkPlane,
        excluding the global Y-axis.

        Args:
            work_axes: Collection of Inventor WorkAxes
            plane: Inventor WorkPlane
            ref_point: Optional (x, y, z) tuple to disambiguate axes
            point_tol: Distance tolerance
            dir_tol: Direction tolerance

        Returns:
            Matching WorkAxis or None
        """
        plane_geom = plane.Plane
        n = plane_geom.Normal
        o = plane_geom.RootPoint

        for axis in work_axes:
            try:
                line = axis.Line
                rp = line.RootPoint
                d = line.Direction

                # 1️⃣ Must be parallel to Y-axis
                if abs(abs(d.Y) - 1.0) > dir_tol:
                    continue

                # 2️⃣ Axis must lie in plane (point-in-plane test)
                dist = abs(
                    n.X * (rp.X - o.X) +
                    n.Y * (rp.Y - o.Y) +
                    n.Z * (rp.Z - o.Z)
                )
                if dist > point_tol:
                    continue

                # 3️⃣ Exclude global Y-axis (origin check)
                if (
                    abs(rp.X) < point_tol and
                    abs(rp.Z) < point_tol
                ):
                    continue

                # 4️⃣ Optional: match against a known reference point
                if ref_point is not None:
                    dx = rp.X - ref_point[0]
                    dy = rp.Y - ref_point[1]
                    dz = rp.Z - ref_point[2]
                    if (dx*dx + dy*dy + dz*dz) > (point_tol * point_tol):
                        continue

                return axis

            except Exception:
                continue

        return None

    def get_workplanes_by_degrees(
        self,
        work_planes,
        target,
        tolerance=2.0,
        exclude_parallel=True
    ):
        initial_target = float(target) % 360.0
        target = 360 - initial_target
        
        result = {}

        plane_angles = []

        for wp in work_planes:
            try:
                n = wp.Plane.Normal

                if exclude_parallel and abs(n.Y) > 0.999:
                    continue

                angle = math.degrees(math.atan2(n.X, n.Z)) % 360.0
                # angle = math.degrees(math.atan2(n.Z, n.X)) % 360

                plane_angles.append((wp, angle))

            except Exception:
                continue

        used_plane_names = set()

        
        best_plane = None
        best_diff = None

        for wp, angle in plane_angles:
            name = getattr(wp, "Name", None)
            if name in used_plane_names:
                continue

            diff = abs(angle - target)
            if diff > 180:
                diff = 360 - diff

            if diff <= tolerance:
                if best_diff is None or diff < best_diff:
                    best_diff = diff
                    best_plane = wp

        if best_plane:
            target = 360 - target
            result[target] = best_plane
            used_plane_names.add(best_plane.Name)

        return best_plane

