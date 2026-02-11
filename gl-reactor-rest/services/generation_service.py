import json
import os
import re
import logging
from datetime import datetime
from services.vault_service import Vault
from services.inventor_service import Inventor
from repositories.mongo_db import Mongo

# Configure logging with date-wise file logging
LOG_DIR = r"D:\GL\logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    console_handler.setFormatter(console_format)

    log_filename = os.path.join(LOG_DIR, f"generation_{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s [%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s')
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# =============================================================================
# DYNAMIC NOZZLE CONFIGURATION
# =============================================================================

# Size-to-fastener count mapping (derives fastener count from nozzle size)
FASTENER_COUNT_BY_SIZE = {
    "50": 4,
    "80": 4,
    "100": 8,
    "150": 8,
    "200": 8,
    "250": 12,
    "300": 12,
    "350": 16,
    "400": 16,
    "500": 20,   # Manhole
}

def get_fastener_count(nozzle_size: str) -> int:
    """Derive fastener count from nozzle size."""
    size = str(nozzle_size).strip()
    return FASTENER_COUNT_BY_SIZE.get(size, 8)  # Default to 8

# Component type priority for assembly order
# Must match dependency chain: manhole → coc → center_nozzle → drive → vessel nozzles
COMPONENT_TYPE_PRIORITY = {
    "monoblock": 0,
    "jacket": 1,
    "diaphragmring": 2,
    "sidebracket": 3,
    "earthing": 4,
    "jacket_nozzle": 5,
    "manhole": 6,           # size=500 (special handling)
    "manhole_accessory": 7, # mhcclamp, springbalanceassembly (depend on manhole)
    "coc": 8,               # coc_gasket, coc, bfcclamp (depend on manhole)
    "center_nozzle": 9,     # degree=d (depends on coc)
    "drive_assembly": 10,   # driveassembly, shaftclosure, mechanical_seal_*, agitator
    "vessel_nozzle": 11,    # any number of nozzles
    "accessory": 12,        # remaining accessories
}

# Fitting sub-priority within a nozzle (assembly sequence)
FITTING_SUB_PRIORITY = {
    "split_flange": 0,
    "gasket": 1,
    "blind_cover": 2,
    "baffle": 2,
    "toughened_glass": 2,
    "manhole_protection_ring": 2,
    "sight_light_glass_flange": 3,   # Must be AFTER toughened_glass (needs toughened_glass_xz_proxy)
    "bolt_stud": 4,
    "washer": 5,
    "nut": 6,
}

# Drive assembly sequence and sub-components order
# Top-level sequence: driveassembly → shaftclosure → mechanical_seal → agitator
# Sub-components are internal parts of driveassembly (higher priority numbers)
DRIVE_ASSEMBLY_PRIORITY = {
    "driveassembly": 0,
    "drive_assembly": 0,
    "shaftclosure": 1,
    "shaft_closure": 1,
    "mechanical_seal_washer": 2,
    "mechanical_seal_fastener": 3,
    "agitator": 4,
    # Sub-components of drive assembly (internal parts)
    "drivebasering": 10,
    "drive_base_ring": 10,
    "padplate": 11,
    "pad_plate": 11,
    "lanternsupport": 12,
    "lantern_support": 12,
    "lanternguard": 13,
    "lantern_guard": 13,
    "agitatorgear_coupling": 14,
    "agitator_gear_coupling": 14,
    "adaptorgearbox": 15,
    "adapter_gearbox_model": 15,
}

# Pattern to identify jacket nozzles (still uses jacketnozzle_ prefix)
JACKET_NOZZLE_PATTERN = re.compile(r'^jacketnozzle_', re.IGNORECASE)

def classify_component(component_name: str) -> str:
    """Classify a component by its type based on naming patterns.

    Nozzle classification is property-based using the nozzle_ prefix:
    - nozzle_{size}_{degree}_{fitting} where size=500 → manhole
    - nozzle_{size}_d_{fitting} (degree=d) → center_nozzle
    - nozzle_{size}_{degree}_{fitting} (otherwise) → vessel_nozzle
    """
    name = component_name.lower().strip()

    # Exact matches first
    if name == "monoblock":
        return "monoblock"
    if name == "jacket":
        return "jacket"
    if name == "diaphragmring":
        return "diaphragmring"
    if name in ("sidebracket", "side_bracket"):
        return "sidebracket"
    if name == "earthing":
        return "earthing"

    # Jacket nozzle pattern (still uses jacketnozzle_ prefix)
    if JACKET_NOZZLE_PATTERN.match(name):
        return "jacket_nozzle"

    # Nozzle classification by parsed properties (name-independent)
    if name.startswith("nozzle_"):
        parts = name.split("_")
        if len(parts) >= 3:
            size = parts[1]
            degree = parts[2]
            if size == "500":
                return "manhole"
            if degree in ('d', '-', '', 'none'):
                return "center_nozzle"
            return "vessel_nozzle"

    # Manhole accessories (depend on manhole_cover)
    if name in ("mhcclamp", "mhc_clamp", "springbalanceassembly"):
        return "manhole_accessory"

    # COC group (coc_gasket → coc → bfcclamp, center_nozzle depends on coc)
    if name in ("coc_gasket", "coc", "bfcclamp", "bf_c_clamp"):
        return "coc"

    # Drive assembly components (after center_nozzle)
    if name in ("driveassembly", "drive_assembly", "shaftclosure", "shaft_closure",
                "agitator", "mechanical_seal_washer", "mechanical_seal_fastener"):
        return "drive_assembly"
    for key in DRIVE_ASSEMBLY_PRIORITY:
        if key in name:
            return "drive_assembly"

    # Remaining accessories
    if name in ("sensor", "gearbox", "motor", "nameplatebracket", "name_plate_bracket"):
        return "accessory"
    if name.startswith("airvent"):
        return "accessory"

    return "accessory"  # Default

def extract_degree(component_name: str) -> int:
    """Extract degree value from component name like 'nozzle_150_60_split_flange'.

    New pattern: nozzle_{size}_{degree}_{fitting}[_{id}]
    Degree is at index 2 (after 'nozzle' and size).
    """
    parts = component_name.lower().split('_')
    # New pattern: nozzle_size_degree_fitting
    if parts[0] == 'nozzle' and len(parts) >= 3:
        degree_str = parts[2]
        if degree_str in ('d', '-', '', 'none'):
            return 0
        try:
            return int(degree_str)
        except ValueError:
            return 0
    return 0

def extract_fitting(component_name: str) -> str:
    """Extract fitting type from component name like 'nozzle_150_60_split_flange_1'.

    New pattern: nozzle_{size}_{degree}_{fitting}[_{id}]
    Fitting parts start at index 3 (after 'nozzle', size, degree).
    """
    parts = component_name.lower().split('_')
    # New pattern: nozzle_size_degree_fitting[_id]
    if parts[0] == 'nozzle' and len(parts) >= 4:
        fitting_parts = parts[3:]
        # Remove trailing numeric ID if present
        if fitting_parts and fitting_parts[-1].isdigit():
            fitting_parts = fitting_parts[:-1]
        return '_'.join(fitting_parts)
    return ""

def get_dynamic_priority(component_name: str) -> tuple:
    """
    Generate priority dynamically from component metadata.
    Returns tuple (type_priority, degree, fitting_priority) for sorting.
    """
    comp_type = classify_component(component_name)
    type_priority = COMPONENT_TYPE_PRIORITY.get(comp_type, 100)

    # For manhole: preserve original JSON fittings order via entry_id tiebreaker.
    # Manhole has complex interleaved order (gasket → ring → gasket → cover)
    # that can't be expressed by fitting_priority alone.
    if comp_type == "manhole":
        degree = extract_degree(component_name)
        return (type_priority, degree, 0)

    # For vessel/center nozzles: sort by degree, then by fitting type
    if comp_type in ("vessel_nozzle", "center_nozzle"):
        degree = extract_degree(component_name)
        fitting = extract_fitting(component_name)
        fitting_priority = FITTING_SUB_PRIORITY.get(fitting, 10)
        return (type_priority, degree, fitting_priority)

    # For drive assembly: use sub-component order
    # Match longest key first to avoid "agitator" matching "agitator_gear_coupling"
    if comp_type == "drive_assembly":
        name_lower = component_name.lower()
        best_match = None
        best_priority = 100
        for key, priority in DRIVE_ASSEMBLY_PRIORITY.items():
            if key in name_lower and (best_match is None or len(key) > len(best_match)):
                best_match = key
                best_priority = priority
        return (type_priority, best_priority, 0)

    return (type_priority, 0, 0)


class Generation:
    def __init__(self):
        self.vault = Vault()
        self.inventor = Inventor()
        self.mongo = Mongo(db="testdb")

    def get_component_list(self, model_details):
        keys = list(model_details['details'].keys())
        if len(keys) < 1:
            print("Invalid component_details structure")
            return False
        so_value = model_details['details'][keys[0]]
        folder_name = f"D:\\GL\\SO\\{so_value}"
        file_path = f"{folder_name}\\{so_value}.json"
        # ✅ Load existing data
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as file:
                    data_list = json.load(file)
                    if not isinstance(data_list, list):
                        raise ValueError("JSON structure must be a list of dicts.")
            except json.JSONDecodeError:
                print("Invalid JSON format, starting with empty list.")
                data_list = []
            except Exception as e:
                print(f"Error reading file: {e}")
                return []
        return data_list
    
    def extract_item_codes(self, obj, component=None):
        item_codes = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if 'itemCode' in key:
                    item_entry = {
                        'itemCode': value,
                        'component': component or 'Unknown'
                    }

                    # If this is a nozzle, add the nozzle name
                    if component and component.lower() == 'nozzle' and 'nozzle' in obj:
                        item_entry['nozzle'] = obj['nozzle']

                    item_codes.append(item_entry)

                elif isinstance(value, dict):
                    next_component = value.get('component', component)
                    item_codes.extend(self.extract_item_codes(value, next_component))

                elif isinstance(value, list):
                    # Special case: check if list of nozzles
                    if key == 'nozzles':
                        for nozzle_obj in value:
                            item_codes.extend(self.extract_item_codes(nozzle_obj, 'Nozzle'))
                    else:
                        for item in value:
                            item_codes.extend(self.extract_item_codes(item, component))

        return item_codes

    def get_item_code_by_component(self, components, comp_details):
        keys = list(comp_details['details'].keys())
        if len(keys) < 1:
            print("Invalid component_details structure")
            return False
        comp = comp_details['details'][keys[1]]
        result = [d for d in components if comp in d]
        model_info = result[0][comp].get("model_info", {})
        item_code = model_info.get("itemCode")
        return [item_code]

    def get_item_codes(self, components_details):
        item_codes = []
        for entry in components_details:
            for outer_dict in entry.values():
                model_info = outer_dict.get("model_info", {})
                item_code = model_info.get("itemCode")
                if item_code:
                    item_codes.append(item_code)
        print(item_codes)
        return item_codes

    def flatten_components(self, data):
        id = 0
        flat_list = []
        target_components = {
            'namePlateBracket', 'driveHood', 'diaphragmRing', 'springBalanceAssembly',
            'MHCClamp', 'coc', 'bfCClamp', 'agitator', 'shaftclosure', 'gearbox', 'motor'
        }
        def normalize_name(name):
            """Normalize component or fitting names: lowercase + underscores for spaces/special chars."""
            return re.sub(r'[^a-zA-Z0-9]+', '_', name.strip().lower()).strip('_')

        for comp_dict in data:
            component_name = next(iter(comp_dict))
            if component_name == 'monoblock':
                id = 0
                for comp_key, comp_val in comp_dict.items():
                    # Normalize top-level component name
                    comp_name = normalize_name(comp_key)

                    # Extract model info
                    model_info = comp_val.get('model_info', {})
                    itemcode = model_info.get('itemCode', '')
                    drawingnumber = model_info.get('drawingNumber', '')
                    model = model_info.get('model', '')

                    id += 1
                    # Add main component
                    flat_list.append({
                        'id': id,
                        'comp': comp_name,
                        'partnumber': drawingnumber,
                        'member': '',
                        'itemcode': itemcode,
                        'sub_components': []
                    })

                    # Process all nozzles
                    for k, v in comp_val.items():
                        if k.startswith('nozzle_'):
                            try:
                                nozzle_data = json.loads(v)
                            except Exception:
                                continue

                            nozzle_no = nozzle_data.get('nozzleNo', '')
                            size = nozzle_data.get('size', '')
                            degree = nozzle_data.get('degree', '')
                            fittings = nozzle_data.get('fittings', [])
                            fasteners = nozzle_data.get('Fastner', [])  # ✅ handle fasteners too

                            # Combine fittings + fasteners
                            all_subs = fittings + fasteners

                            for fitting in all_subs:
                                fname_raw = fitting.get('name', '')
                                fname = normalize_name(fname_raw)
                                fitemcode = fitting.get('itemCode', '')
                                fdrawing = fitting.get('drawingNumber', '')

                                # Construct component name (name-independent)
                                if degree in ('', '-', None):
                                    comp_name_full = f"nozzle_{size}_d_{fname}"
                                else:
                                    comp_name_full = f"nozzle_{size}_{degree}_{fname}"

                                fitting_comp = normalize_name(comp_name_full)

                                id += 1
                                flat_list.append({
                                    'id': id,
                                    'comp': fitting_comp,
                                    'partnumber': fdrawing,
                                    'member': '',
                                    'itemcode': fitemcode,
                                    'sub_components': []
                                })


            if component_name == 'jacket':
                
                jacket_data = comp_dict['jacket']
                comp_name = jacket_data.get('component', 'Unknown')

                # Jacket itself
                if 'jacket' in jacket_data:
                    id = id + 1
                    j = jacket_data['jacket']
                    flat_list.append({
                        'id': id,
                        'comp': normalize_name(comp_name),
                        'partnumber': j.get('drawingNumberJacket', ''),
                        'member': '',
                        'itemcode': j.get('itemCodeJacket', ''),
                        'sub_components': []
                    })

                # Support
                if 'support' in jacket_data:
                    id = id + 1
                    s = jacket_data['support']
                    flat_list.append({
                        'id': id,
                        'comp': normalize_name(s.get('component', 'Support')),
                        'partnumber': s.get('drawingNumberJacketSupport', ''),
                        'member': '',
                        'itemcode': s.get('itemCodeJacketSupport', ''),
                        'sub_components': []
                    })

                # Earthing
                if 'earthing' in jacket_data:
                    id = id + 1
                    e = jacket_data['earthing']
                    flat_list.append({
                        'id': id,
                        'comp': normalize_name('Earthing'),
                        'partnumber': e.get('drawingNumberJacketEarthing', ''),
                        'member': '',
                        'itemcode': e.get('itemCodeJacketEarthing', ''),
                        'sub_components': []
                    })

                # Nozzles (list)
                if 'nozzles' in jacket_data:
                    for n in jacket_data['nozzles']:
                        id = id + 1
                        flat_list.append({
                            'id': id,
                            'comp': normalize_name(f"{component_name} Nozzle {n.get('nozzle', '')}"),
                            'partnumber': n.get('drawingNumber', ''),
                            'member': '',
                            'itemcode': n.get('itemCode', ''),
                            'sub_components': []
                        })

            if component_name == 'sensor':
                key = next(iter(comp_dict))
                data = comp_dict[key]

                comp_name = data.get('component', key)

                # Iterate through subcomponents
                for sub_key, sub_data in data.items():
                    if sub_key in ['component', 'model_info']:
                        continue  # skip metadata
                    
                    if isinstance(sub_data, dict):
                        id = id + 1
                        model_info = sub_data.get('model_info', {})
                        flat_list.append({
                            'id': id,
                            'comp': normalize_name(f"{comp_name}  {sub_key.capitalize()}"),
                            'partnumber': model_info.get('drawingNumber', ''),
                            'member': '',
                            'itemcode': model_info.get('itemCode', ''),
                            'sub_components': []
                        })

            if component_name == 'driveAssembly':
                key = next(iter(comp_dict))
                data = comp_dict[key]

                comp_name = data.get('component', key)

                # Iterate through subcomponents
                for sub_key, sub_data in data.items():
                    if sub_key in ['component', 'model_info']:
                        continue  # skip metadata

                    if isinstance(sub_data, dict):
                        # Try to find drawingNumber and itemCode (the keys can vary slightly)
                        drawing_number = next((v for k, v in sub_data.items() if 'drawingNumber' in k), None)
                        item_code = next((v for k, v in sub_data.items() if 'itemCode' in k), None)
                        id = id + 1
                        flat_list.append({
                            'id': id,
                            'comp': normalize_name(f"{comp_name} {sub_key}"),
                            'partnumber': drawing_number or '',
                            'member': '',
                            'itemcode': item_code or '',
                            'sub_components': []
                        })
            
            if component_name == 'airVentCouplingPlug':
                key = next(iter(comp_dict))
                data = comp_dict[key]

                comp_name = key[0].upper() + key[1:]  # capitalize nicely

                # Handle nozzle list
                if 'nozzles' in data:
                    for nozzle in data['nozzles']:
                        id = id + 1
                        flat_list.append({
                            'id': id,
                            'comp': normalize_name(f"{comp_name} {nozzle.get('nozzle', '')}"),
                            'partnumber': nozzle.get('drawingNumber', ''),
                            'member': '',
                            'itemcode': nozzle.get('itemCode', ''),
                            'sub_components': []
                        })
            
            if component_name == 'insulation':
                key = next(iter(comp_dict))
                data = comp_dict[key]

                comp_name = data.get('component', key)

                # Iterate through all potential subcomponents
                for sub_key, sub_data in data.items():
                    if sub_key in ['component', 'model_info', 'insulationReq', 'insulationType']:
                        continue  # skip metadata

                    if isinstance(sub_data, dict):
                        # Find the drawing number and item code
                        drawing_number = next((v for k, v in sub_data.items() if 'drawingNumber' in k), None)
                        item_code = next((v for k, v in sub_data.items() if 'itemCode' in k), None)
                        id = id + 1
                        flat_list.append({
                            'id': id,
                            'comp': normalize_name(f"{comp_name} {sub_key[0].upper() + sub_key[1:]}"),
                            'partnumber': drawing_number or '',
                            'member': '',
                            'itemcode': item_code or '',
                            'sub_components': []
                        })

            if component_name in target_components:
                key, data = next(iter(comp_dict.items()))

                comp_name = data.get('component', key)
                model_info = data.get('model_info', {})

                id = id + 1
                flat_list.append({
                    'id': id,
                    'comp': normalize_name(comp_name),
                    'partnumber': model_info.get('drawingNumber', ''),
                    'member': '',
                    'itemcode': model_info.get('itemCode', ''),
                    'sub_components': []
                })
            
        return flat_list

    def build_standard_model(self, data):
        """Build standardized model structure from list of component dicts."""

        # Initialize base structure
        standard_model = {
            "reactor": "",
            "model": "",
            "standard": "NON-GMP",
            "model_info": {
                "glass": "",
                "ndt": "",
                "temp": "",
                "pressure": ""
            },
            "components": {}
        }

        component_index = 1

        for item in data:
            component_name, component_data = next(iter(item.items()))

            # --- Common model_info extraction ---
            model_info = component_data.get("model_info", {})
            if model_info:
                standard_model["reactor"] = model_info.get("model", "")
                standard_model["model"] = model_info.get("reactor", "")
                standard_model["model_info"]["glass"] = model_info.get("glass", "")
                standard_model["model_info"]["ndt"] = model_info.get("ndt", "")
                standard_model["model_info"]["temp"] = model_info.get("designTemperature", "")
                standard_model["model_info"]["pressure"] = model_info.get("designPressure", "")

            configurations = {}

            # --- Component-specific parsing logic ---
            if component_name.lower() == "monoblock":
                configurations = {
                    "id": component_data.get("id", ""),
                    "osTOos": component_data.get("osTos", ""),
                    "insulation_on_top": component_data.get("insulationOnTop", ""),
                    "spillage_collection_tray": component_data.get("spilageCollectionTray", ""),
                    "lifting_moc": component_data.get("liftingMOC", ""),
                    "top_dished_end_thickness": component_data.get("topDishedEndThickness", ""),
                    "inner_shell_thickness": component_data.get("innerShellThickness", ""),
                    "bottom_dished_end_thickness": component_data.get("bottomDishedEndThickness", ""),
                    "drawing_number": model_info.get("drawingNumber", ""),
                    "item_code": model_info.get("itemCode", "")
                }

                # Parse nozzles (JSON strings)
                nozzles = {}
                for k, v in component_data.items():
                    if k.startswith("nozzle_"):
                        try:
                            nozzle_dict = json.loads(v)
                            idx = len(nozzles) + 1
                            nozzles[str(idx)] = {
                                "nozzle_name": nozzle_dict.get("nozzleNo", ""),
                                "size": nozzle_dict.get("size", ""),
                                "drilling_standard": nozzle_dict.get("drillingStandard", ""),
                                "degree": nozzle_dict.get("degree", ""),
                                "radius": nozzle_dict.get("radius", ""),
                                "location": nozzle_dict.get("location", ""),
                                "fittings": nozzle_dict.get("fittings", {}),
                                "fasteners": nozzle_dict.get("Fastner", {})
                            }
                        except json.JSONDecodeError:
                            continue
                configurations["nozzles"] = nozzles

            elif component_name.lower() == "jacket":
                jacket_data = component_data.get("jacket", {})
                support_data = component_data.get("support", {})
                earthing_data = component_data.get("earthing", {})
                nozzle_list = component_data.get("nozzles", [])

                configurations = {
                    "jacket": jacket_data,
                    "support": support_data,
                    "earthing": earthing_data,
                }

                # Add jacket nozzles
                nozzles = {}
                for i, n in enumerate(nozzle_list, start=1):
                    nozzles[str(i)] = {
                        "nozzle_name": n.get("nozzle", ""),
                        "size": n.get("size", ""),
                        "degree": n.get("degree", ""),
                        "location": n.get("location", ""),
                        "drawing_number": n.get("drawingNumber", ""),
                        "item_code": n.get("itemCode", "")
                    }
                configurations["nozzles"] = nozzles

            elif component_name.lower() == "diaphragmring":
                configurations = {
                    "ring_material": component_data.get("ringMaterial", ""),
                    "nozzle_size": component_data.get("nozzleSize", ""),
                    "drawing_number": component_data.get("model_info", "").get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", "").get("itemCode", "")
                }

            elif component_name.lower() == "springbalanceassembly":
                configurations = {
                    "assembly_name": component_data.get("mhCoverBalanceAssembly", ""),
                    "assembly_size": component_data.get("springbalanceassemblySize", ""),
                    "assembly_type": component_data.get("springbalanceassemblyType", ""),
                    "assembly_material": component_data.get("springbalanceassemblyMaterial", ""),
                    "drawing_number": component_data.get("model_info", "").get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", "").get("itemCode", "")
                }

            elif component_name.lower() == "mhcclamp":
                configurations = {
                    "material": component_data.get("mhCClampMaterial", ""),
                    "size": component_data.get("mhCClampSize", ""),
                    "drawing_number": component_data.get("model_info", "").get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", "").get("itemCode", "")
                }

            elif component_name.lower() == "coc":
                configurations = {
                    "coc_size": component_data.get("cocSize", ""),
                    "drawing_number": component_data.get("model_info", "").get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", "").get("itemCode", "")
                }
            
            elif component_name.lower() == "bfcclamp":
                configurations = {
                    "material": component_data.get("bfCClampMaterial", ""),
                    "size": component_data.get("bfCClampSize", ""),
                    "quantity": component_data.get("bfCClampQty", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "sensor":
                dial_thermo = component_data.get("dialThermo", {})
                configurations = {
                    "sensor_type": dial_thermo.get("sensorType", ""),
                    "length": dial_thermo.get("dialThermoLength", ""),
                    "drawing_number": dial_thermo.get("dialThermoDrawingNumber", ""),
                    "item_code": dial_thermo.get("dialThermoItemCode", "")
                }

            elif component_name.lower() == "agitator":
                single_flight = component_data.get("singleFlightData", {})
                double_flight = component_data.get("doubleFlightData", {})
                triple_flight = component_data.get("tripleFlightData", {})
                special_flight = component_data.get("specialFlightData", {})

                configurations = {
                    "shaft_dia": component_data.get("shaftDia", ""),
                    "sealing_type": component_data.get("sealingType", ""),
                    "volume_marking": component_data.get("volumeMarking", ""),
                    "hastalloy_sleeve": component_data.get("hastalloySleeve", ""),
                    "agitator_height": component_data.get("agitatorHeight", ""),
                    "flight": component_data.get("flight", ""),
                    "single_flight": single_flight,
                    "double_flight": double_flight,
                    "triple_flight": triple_flight,
                    "special_flight": special_flight,
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "shaftclosure":
                configurations = {
                    "shaft_dia": component_data.get("shaftclosureDia", ""),
                    "type": component_data.get("shaftclosureType", ""),
                    "make": component_data.get("shaftclosureMake", ""),
                    "sealing": component_data.get("shaftclosureSealing", ""),
                    "housing": component_data.get("shaftclosureHousing", ""),
                    "inboard_face": component_data.get("shaftclosureInboardFace", ""),
                    "outboard_face": component_data.get("shaftclosureOutboardFace", ""),
                    "other": component_data.get("shaftclosureOther", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "gearbox":
                configurations = {
                    "make": component_data.get("gearboxMake", ""),
                    "type": component_data.get("gearboxType", ""),
                    "model": component_data.get("gearboxModel", ""),
                    "ratio": component_data.get("gearboxRatio", ""),
                    "frame": component_data.get("gearboxFrame", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "motor":
                configurations = {
                    "make": component_data.get("motorMake", ""),
                    "type": component_data.get("motorType", ""),
                    "mounting": component_data.get("motorMouting", ""),
                    "hp": component_data.get("motorHP", ""),
                    "standard": component_data.get("motorStandard", ""),
                    "frame": component_data.get("motorFrame", ""),
                    "temp_class": component_data.get("motorTempClass", ""),
                    "gas_group": component_data.get("motorGasGroup", ""),
                    "protection": component_data.get("motorProtection", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "driveassembly":
                configurations = {
                    "drive_base_ring": component_data.get("driveBaseRing", {}),
                    "pad_plate": component_data.get("padPlat", {}),
                    "lantern_support": component_data.get("lanternSupport", {}),
                    "lantern_guard": component_data.get("lanternGuard", {}),
                    "agitator_gear_coupling": component_data.get("agitatorGearCoupling", {}),
                    "adapter_gearbox_model": component_data.get("adaptorGearBoxModel", {}),
                    "bearing": component_data.get("bearing", {}),
                    "sleeve": component_data.get("sleeve", {}),
                    "oil_seal": component_data.get("oilSeal", {}),
                    "circlip": component_data.get("circlip", {}),
                    "lock_nut": component_data.get("lockNut", {}),
                    "lock_washer": component_data.get("lockWasher", {}),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "nameplatebracket":
                configurations = {
                    "material": component_data.get("npbMaterial", ""),
                    "type": component_data.get("npbType", ""),
                    "mounting": component_data.get("npbMounting", ""),
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }

            elif component_name.lower() == "airventcouplingplug":
                nozzles = {}
                for i, n in enumerate(component_data.get("nozzles", []), start=1):
                    nozzles[str(i)] = {
                        "nozzle_name": n.get("nozzle", ""),
                        "type": n.get("type", ""),
                        "location": n.get("location", ""),
                        "length": n.get("length", ""),
                        "size": n.get("size", ""),
                        "material": n.get("material", ""),
                        "drawing_number": n.get("drawingNumber", ""),
                        "item_code": n.get("itemCode", "")
                    }

                configurations = {
                    "nozzles": nozzles,
                    "drawing_number": component_data.get("model_info", {}).get("drawingNumber", ""),
                    "item_code": component_data.get("model_info", {}).get("itemCode", "")
                }


            else:
                # fallback: include all simple key-values
                configurations = {k: v for k, v in component_data.items() if not isinstance(v, (dict, list))}

            # Add component into main dict
            standard_model["components"][str(component_index)] = {
                "component": component_name,
                "configurations": configurations
            }
            component_index += 1

        return standard_model
    
    def extract_component_data(self, data: dict):
        """
        Extract standardized component and subcomponent data
        from a standard model dictionary — UPDATED for nested monoblock.
        """

        results = []
        id_counter = 1

        def make_entry(comp, itemcode, drawing_number, member="", subs=[],
                       fastener_count=None, nozzle_size=None, nozzle_degree=None, nozzle_location=None,
                       gasket_offset=None):
            nonlocal id_counter
            entry = {
                "id": id_counter,
                "comp": comp.lower(),
                "partnumber": drawing_number or "",
                "member": member,
                "itemcode": itemcode or "",
                "sub_components": subs or []
            }
            # Add nozzle metadata if provided (for dynamic handling)
            if fastener_count is not None:
                entry["fastener_count"] = fastener_count
            if nozzle_size is not None:
                entry["nozzle_size"] = nozzle_size
            if nozzle_degree is not None:
                entry["nozzle_degree"] = nozzle_degree
            if nozzle_location is not None:
                entry["nozzle_location"] = nozzle_location
            if gasket_offset is not None:
                entry["gasket_offset"] = gasket_offset
            id_counter += 1
            return entry

        # ---------------------------
        # NEW: Recursive collector
        # ---------------------------
        def collect_nested_components(node, collected):
            """
            Recursively collect sub-component items:
                - name / member
                - drawing_number / drawingNumber
                - item_code / itemCode
            """
            if isinstance(node, dict):
                member = node.get("name")
                drawing = node.get("drawing_number") or node.get("drawingNumber")
                itemcode = node.get("item_code") or node.get("itemCode")

                # If this dict resembles a part line, add it
                if member or drawing or itemcode:
                    collected.append({
                        "member": member or "",
                        "partnumber": drawing or "",
                        "itemcode": itemcode or ""
                    })

                # Continue recursion
                for v in node.values():
                    collect_nested_components(v, collected)

            elif isinstance(node, list):
                for elem in node:
                    collect_nested_components(elem, collected)

        components = data.get("components", {})

        for key, comp_data in components.items():
            comp_name = comp_data.get("component", "").lower()
            config = comp_data.get("configurations", {})
            
            # --- MONOBLOCK ---
            if comp_name == "monoblock":

                # Create main monoblock entry
                results.append(make_entry(
                    "monoblock",
                    config.get("item_code"),
                    config.get("drawing_number"),
                    member="",
                    subs=[]
                ))

                nozzles = config.get("nozzles", {})

                for _, nozzle in nozzles.items():
                    nozzle_name = nozzle.get("nozzle_name", "").lower()
                    size = str(nozzle.get("size", "")).lower()
                    degree = str(nozzle.get("degree", "")).lower()
                    if degree in ('-', '', 'none') or degree is None:
                        degree = 'D'

                    # Derive fastener count from nozzle size
                    fastener_count = get_fastener_count(size)

                    fittings = nozzle.get("fittings", [])
                    # Check if this nozzle has toughened_glass (sight glass nozzle)
                    has_sight_glass = any(
                        'toughened_glass' in f.get('name', '').lower().replace('/', ' ').replace(' ', '_')
                        for f in fittings
                    )
                    for fit in fittings:
                        member = fit.get("name", "").lower().replace("/", " ").replace(" ", "_")
                        drawing = fit.get("drawingNumber")
                        itemcode = fit.get("itemCode")
                        fit_id = fit.get("id", 1)

                        # FITTING comp → nozzle_500_0_gasket_1 (name-independent)
                        comp_id = f"nozzle_{size}_{degree}_{member}_{fit_id}"

                        # Sight glass nozzles use gasket offset 2.0 (others use default 2.2)
                        g_offset = 2.0 if (has_sight_glass and 'gasket' in member) else None

                        # Add fitting entry with nozzle metadata
                        results.append(make_entry(
                            comp_id,
                            itemcode,
                            drawing,
                            member="",
                            subs=[],
                            fastener_count=fastener_count,
                            nozzle_size=size,
                            nozzle_degree=degree,
                            gasket_offset=g_offset
                        ))

                    # FASTENERS - include fastener_count for circular pattern
                    fasteners = nozzle.get("fasteners", [])
                    for fast in fasteners:
                        fast_name = fast.get("name", "").lower().replace("/", " ").replace(" ", "_")
                        fast_draw = fast.get("drawingNumber")
                        fast_item = fast.get("itemCode")

                        # FASTENER comp → nozzle_500_0_bolt/stud (name-independent)
                        fast_comp_id = f"nozzle_{size}_{degree}_{fast_name}"

                        results.append(make_entry(
                            fast_comp_id,
                            fast_item,
                            fast_draw,
                            member="",
                            subs=[],
                            fastener_count=fastener_count,
                            nozzle_size=size,
                            nozzle_degree=degree
                        ))

                continue



            # -------------------------------------------------
            # REMAINING COMPONENTS (unchanged)
            # -------------------------------------------------

            # --- JACKET ---
            if comp_name == "jacket":
                jacket = config.get("jacket", {})
                support = config.get("support", {})
                earthing = config.get("earthing", {})
                nozzles = config.get("nozzles", {})

                # Jacket base entry
                results.append(make_entry(
                    "jacket",
                    jacket.get("itemCodeJacket"),
                    jacket.get("drawingNumberJacket")
                ))

                # Jacket nozzles - include degree and location for dynamic handling
                for _, nz in nozzles.items():
                    nz_size = str(nz.get("size", "80"))
                    nz_degree = str(nz.get("degree", "0"))
                    nz_location = nz.get("location", "SHELL")
                    results.append(make_entry(
                        f"jacketnozzle_{nz.get('nozzle_name')}_{nz_location}",
                        nz.get("item_code"),
                        nz.get("drawing_number"),
                        nozzle_size=nz_size,
                        nozzle_degree=nz_degree,
                        nozzle_location=nz_location
                    ))

                # Support
                if support:
                    results.append(make_entry(
                        support.get("component", "sidebracket"),
                        support.get("itemCodeJacketSupport"),
                        support.get("drawingNumberJacketSupport")
                    ))

                # Earthing
                if earthing:
                    results.append(make_entry(
                        "earthing",
                        earthing.get("itemCodeJacketEarthing"),
                        earthing.get("drawingNumberJacketEarthing")
                    ))

                continue

            # --- DIAPHRAGMRING ---
            if comp_name == "diaphragmring":
                results.append(make_entry(
                    "diaphragmring",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))
                continue

            # --- SPRING BALANCE ASSEMBLY ---
            if comp_name == "springbalanceassembly":
                results.append(make_entry(
                    "springbalanceassembly",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))
                continue

            # --- MHC Clamp ---
            if comp_name == "mhcclamp":
                results.append(make_entry(
                    "mhcclamp",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))
                continue

            # --- SENSOR ---
            if comp_name == "sensor":
                results.append(make_entry(
                    "sensor",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))
                continue

            # --- COC ---
            if comp_name == "coc":
                # Emit coc_gasket alongside coc (previously hardcoded insert)
                results.append(make_entry(
                    "coc_gasket",
                    "T1-0104",
                    ""
                ))
                results.append(make_entry(
                    "coc",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))
                continue

            # --- BF C Clamp ---
            if comp_name == "bfcclamp":
                results.append(make_entry(
                    "bfCClamp",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))
                continue

            # --- AGITATOR ---
            if comp_name == "agitator":
                results.append(make_entry(
                    "agitator",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))
                continue

            # --- SHAFT CLOSURE ---
            if comp_name == "shaftclosure":
                results.append(make_entry(
                    "shaftclosure",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))
                # Emit mechanical seal components alongside shaftclosure (previously hardcoded inserts)
                results.append(make_entry(
                    "mechanical_seal_washer",
                    "13WS0013",
                    ""
                ))
                results.append(make_entry(
                    "mechanical_seal_fastener",
                    "13CS0237",
                    ""
                ))
                continue

            # --- GEARBOX ---
            if comp_name == "gearbox":
                results.append(make_entry("gearbox", "", ""))
                continue

            # --- MOTOR ---
            if comp_name == "motor":
                results.append(make_entry("motor", "", ""))
                continue

            # --- DRIVE ASSEMBLY ---
            if comp_name == "driveassembly":
                subconfigs = config
                results.append(make_entry(
                    comp_name,
                    "",
                    "",
                    member="HD100M-60-160-015-DM-0007_RATIO_14_CGL_IE3_GL.iam"
                ))

                for sub_name, sub_conf in subconfigs.items():
                    if isinstance(sub_conf, dict):
                        results.append(make_entry(sub_name, "", ""))
                continue

            # --- NAME PLATE BRACKET ---
            if comp_name == "nameplatebracket":
                results.append(make_entry(
                    "nameplatebracket",
                    config.get("item_code"),
                    config.get("drawing_number")
                ))
                continue

            # --- AIR VENT (NOZZLES) ---
            if comp_name == "airventcouplingplug":
                for _, nz in config.get("nozzles", {}).items():
                    results.append(make_entry(
                        f"airvent_{nz.get('type', '').lower()}_{nz.get('nozzle_name', '').lower()}",
                        nz.get("item_code"),
                        nz.get("drawing_number")
                    ))
                continue

            # --- DEFAULT ---
            itemcode = config.get("item_code") or next(
                (v for k, v in config.items() if "itemcode" in k.lower()), "")
            drawing_number = config.get("drawing_number") or next(
                (v for k, v in config.items() if "drawing" in k.lower()), "")
            results.append(make_entry(comp_name, itemcode, drawing_number))

        return results
    
    def sort_key(self, entry):
        """
        Dynamic sort key based on component type, degree, and fitting order.
        Uses get_dynamic_priority() for flexible nozzle ordering.
        """
        comp_name = entry.get("comp", "")
        priority = get_dynamic_priority(comp_name)
        # Append entry ID as tiebreaker to maintain stable order
        return (*priority, entry.get("id", 0))

    def generate_model(self, model_details):
        """
        Generate a 3D model by extracting component data, retrieving files from Vault,
        and triggering Inventor automation.

        Args:
            model_details: Dictionary containing model configuration and specifications

        Returns:
            bool: True if model generation succeeded, False otherwise
        """
        components = self.get_component_list(model_details=model_details)
        standard_model = self.build_standard_model(data=components)
        components_details = self.extract_component_data(data=standard_model)
        results = sorted(components_details, key=self.sort_key)

        downloaded_components_files = self.vault.find_files_by_item_codes(item_codes=results)
        is_generated = self.inventor.generate(components=downloaded_components_files, model_details=model_details)
        return is_generated
    
    def open_component(self, compo_details):
        components = self.get_component_list(model_details=compo_details)
        item_code = self.get_item_code_by_component(components=components, comp_details=compo_details)
        downloaded_components_files = self.vault.find_files_by_item_codes(item_codes=item_code)
        print(downloaded_components_files)
        result = self.inventor.open(downloaded_components_files)
        return result