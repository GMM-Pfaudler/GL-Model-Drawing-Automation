import math
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class FirstJacketNozzleBuilder:

    def __init__(self, inv_app, tg, main_assy_def, monoblock, item):
        self.inv_app = inv_app
        self.tg = tg
        self.main_assy_def = main_assy_def
        self.monoblock = monoblock
        self.item = item

    def create_point2d_mid(self, pt1, pt2):
        """Returns a 2D midpoint for dimension text placement."""
        mid_x = (pt1.Geometry.X + pt2.Geometry.X) / 2
        mid_y = (pt1.Geometry.Y + pt2.Geometry.Y) / 2
        return self.tg.CreatePoint2d(mid_x, mid_y)

    def find_occurrence(self, occurrences, name):
        return self.find_occurrence_recursive(occurrences=occurrences, target_name=name)
    
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

    def add_jacket_nozzle_top(self):
        logger.info("Starting: First Jacket Nozzle at Top (Shell)")
        try:
            # --- Setup Angled Plane ---
            angle_deg = -28
            angle_rad = math.radians(angle_deg)
            origin = self.tg.CreatePoint(0.0, 0.0, 0.0)
            x_axis = self.tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
            y_axis = self.tg.CreateUnitVector(0.0, 1.0, 0.0)

            angled_plane = self.main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
            angled_plane.Name = "N16_Plane"
            angled_plane.Visible = True
            angled_plane.Grounded = True

            # --- Add Sketch ---
            sketch = self.main_assy_def.Sketches.Add(angled_plane)
            y_axis_proj = sketch.AddByProjectingEntity(self.main_assy_def.WorkAxes["Y Axis"])

            # --- Rectangle Geometry ---
            width, height = 10.0, 5.0
            pt1 = sketch.ModelToSketchSpace(self.tg.CreatePoint(-width / 2, 0, 0))
            pt2 = sketch.ModelToSketchSpace(self.tg.CreatePoint(width / 2, height, 0))
            rect_lines = sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)

            bottom_line = rect_lines.Item(1)
            bottom_line.Centerline = True

            # --- Project XZ Plane from L_nozzle ---
            l_nozzle_occ = self.find_occurrence(occurrences=self.monoblock.SubOccurrences, name="L_DN150")
            if not l_nozzle_occ:
                raise Exception("L_DN150 occurrence not found.")

            xz_plane = l_nozzle_occ.Definition.WorkPlanes["XZ Plane"]
            xz_plane_proxy = l_nozzle_occ.CreateGeometryProxy(xz_plane)
            projected_line = sketch.AddByProjectingEntity(xz_plane_proxy)

            if not hasattr(projected_line, "StartSketchPoint"):
                raise Exception("Projected entity is not a SketchLine.")

            # --- Dimension Constraints ---
            pt1 = bottom_line.StartSketchPoint
            pt2 = projected_line.StartSketchPoint

            if not pt1 or not pt2:
                raise Exception("SketchPoint missing for dimension.")

            text_pt = self.create_point2d_mid(pt1, pt2)
            dim_constraints = sketch.DimensionConstraints
            dim = dim_constraints.AddTwoPointDistance(pt1, pt2, 19202, text_pt, False)
            dim.Parameter.Expression = "2350 mm"

            # --- Collinear Constraint ---
            second_line = rect_lines.Item(2)
            sketch.GeometricConstraints.AddCollinear(y_axis_proj, second_line)

            return sketch, rect_lines

        except Exception as e:
            logger.error(f"Error in adding jacket nozzle top: {e}")
            raise
        else:
            logger.info("Completed: First Jacket Nozzle at Top (Shell)")

    def create_revolve_feature(self, sketch, rect_lines, feature_name="RevolveFeature"):
        """
        Creates a revolve feature using a rectangle's sketch lines.
        
        Parameters:
            sketch: The sketch containing the rectangle.
            rect_lines: The rectangle's SketchLines collection.
            feature_name: Optional name for logging purposes.
        
        Returns:
            The created revolve feature.
        """
        try:
            # Extract rectangle lines
            first_line = rect_lines.Item(1)  # Bottom edge (centerline)
            second_line = rect_lines.Item(2)
            third_line = rect_lines.Item(3)
            fourth_line = rect_lines.Item(4)

            # Dimension 1: Horizontal (between 2nd and 4th line start points)
            dim1_pt1 = second_line.StartSketchPoint
            dim1_pt2 = fourth_line.StartSketchPoint
            if not dim1_pt1 or not dim1_pt2:
                raise ValueError("Failed to get sketch points for horizontal dimension.")
            dim1_mid = self.create_point2d_mid(dim1_pt1, dim1_pt2)
            horizontal_dim = sketch.DimensionConstraints.AddTwoPointDistance(dim1_pt1, dim1_pt2, 19203, dim1_mid, False)
            horizontal_dim.Parameter.Expression = "5000 mm"

            # Dimension 2: Vertical (between 1st and 3rd line start points)
            dim2_pt1 = first_line.StartSketchPoint
            dim2_pt2 = third_line.StartSketchPoint
            if not dim2_pt1 or not dim2_pt2:
                raise ValueError("Failed to get sketch points for vertical dimension.")
            dim2_mid = self.create_point2d_mid(dim2_pt1, dim2_pt2)
            vertical_dim = sketch.DimensionConstraints.AddTwoPointDistance(dim2_pt1, dim2_pt2, 19202, dim2_mid, False)
            vertical_dim.Parameter.Expression = "45 mm"

            # Finalize sketch
            sketch.Solve()
            sketch.UpdateProfiles()
            sketch.Profiles.AddForSolid()
            sketch.UpdateProfiles()
            profile = sketch.Profiles.Item(1)

            # Revolve feature
            part_def = self.inv_app.ActiveDocument.ComponentDefinition
            revolve = part_def.Features.RevolveFeatures.AddFull(profile, first_line, 20482)

            logger.info(f"{feature_name} created successfully.")
            return revolve

        except Exception as e:
            logger.error(f"Failed to create {feature_name}: {e}")
            raise


    # def create_revolve_feature(self, sketch, rect_lines, feature_name="RevolveFeature"):
    #     """Creates a revolve feature from a sketch and axis line."""
    #     try:              
    #         first_line = rect_lines.Item(1)
    #         second_line = rect_lines.Item(2)
    #         third_line = rect_lines.Item(3)
    #         fourth_line = rect_lines.Item(4)

    #         # Get sketch points from each line
    #         second_line_start_pt1 = second_line.StartSketchPoint
    #         fourth_line_start_pt2 = fourth_line.StartSketchPoint

    #         # Validate points
    #         if second_line_start_pt1 is None or fourth_line_start_pt2 is None:
    #             raise Exception("One or both sketch points are None.")

    #         # Compute midpoint for dimension text placement
    #         mid_x = (second_line_start_pt1.Geometry.X + fourth_line_start_pt2.Geometry.X) / 2
    #         mid_y = (second_line_start_pt1.Geometry.Y + fourth_line_start_pt2.Geometry.Y) / 2
    #         text_point = self.tg.CreatePoint2d(mid_x, mid_y)

    #         horizontal_dim = sketch.DimensionConstraints.AddTwoPointDistance(second_line_start_pt1, fourth_line_start_pt2, 19203, text_point, False)

    #         # Set the dimension to the actual rectangle width (10.0 mm)
    #         horizontal_dim.Parameter.Expression = "5000 mm"

    #         # # Get first and third lines of the rectangle
    #         # first_line = rect_lines.Item(1)   # Bottom edge
    #         # third_line = rect_lines.Item(3)   # Top edge

    #         # Get sketch points (use start point for consistency)
    #         first_line_start_pt1 = first_line.StartSketchPoint
    #         third_line_start_pt2 = third_line.StartSketchPoint

    #         # Validate points
    #         if first_line_start_pt1 is None or third_line_start_pt2 is None:
    #             raise Exception("One or both sketch points are None.")

    #         # Compute midpoint for dimension text
    #         mid_x = (first_line_start_pt1.Geometry.X + third_line_start_pt2.Geometry.X) / 2
    #         mid_y = (first_line_start_pt1.Geometry.Y + third_line_start_pt2.Geometry.Y) / 2
    #         text_point = self.tg.CreatePoint2d(mid_x, mid_y)

    #         # Add vertical dimension
    #         vertical_dim = sketch.DimensionConstraints.AddTwoPointDistance(first_line_start_pt1, third_line_start_pt2, 19202, text_point, False)

    #         # Set the value (height of the rectangle)
    #         vertical_dim.Parameter.Expression = "45 mm"

    #         sketch.Solve()
    #         sketch.UpdateProfiles()
    #         sketch.Profiles.AddForSolid()
    #         sketch.UpdateProfiles()
    #         profile = sketch.Profiles.Item(1)

    #         part_def = self.inv_app.ActiveDocument.ComponentDefinition
    #         revolve_feats = part_def.Features.RevolveFeatures
    #         revolve = revolve_feats.AddFull(profile, first_line, 20482)

    #         logger.info(f"{feature_name} created successfully.")
    #         return revolve
    #     except Exception as e:
    #         logger.error(f"Failed to create {feature_name}: {e}")
    #         raise

    def remove_participants(self, feature):
        """Removes specified components from feature participants."""
        try:
            inner_shell = self.find_occurrence(occurrences=self.monoblock.SubOccurrences, name="INNER SHELL")
            glass_9100 = self.find_occurrence(occurrences=self.monoblock.SubOccurrences, name="9100")

            if inner_shell:
                feature.RemoveParticipant(inner_shell)
            if glass_9100:
                feature.RemoveParticipant(glass_9100)

            logger.info("Participants removed successfully.")
        except Exception as e:
            logger.warning(f"Failed to remove participants: {e}")

    def add_axis_from_cylinder(self, revolve_feature, axis_name="N16_Axis"):
        """Adds a fixed work axis from the first cylindrical face of a revolve."""
        try:
            cylinder = revolve_feature.Faces.Item(1).Geometry
            axis = self.main_assy_def.WorkAxes.AddFixed(cylinder.BasePoint, cylinder.AxisVector, False)
            axis.Name = axis_name
            axis.Grounded = True
            logger.info(f"Axis '{axis_name}' added.")
            return axis
        except Exception as e:
            logger.error(f"Failed to add axis '{axis_name}': {e}")
            raise

    def place_component(self, filepath, base_point):
        """Places a component at a specific base point."""
        try:
            matrix = self.tg.CreateMatrix()
            translation_vector = self.tg.CreateVector(base_point.X, base_point.Y, base_point.Z)
            matrix.SetTranslation(translation_vector)

            occurrence = self.main_assy_def.Occurrences.Add(filepath, self.tg.CreateMatrix())
            occurrence.Transformation = matrix
            occurrence.Grounded = False
            logger.info(f"Component placed at: {base_point}")
            return occurrence
        except Exception as e:
            logger.error(f"Failed to place component: {e}")
            raise

    def add_constraints(self, shell_jacket_nozzle1, base_plane_name="N16_Plane", axis_name="N16_Axis"):
        """Adds assembly constraints between nozzle and jacket shell."""
        try:
            flush = self.main_assy_def.Constraints.AddFlushConstraint(
                self.main_assy_def.WorkPlanes[base_plane_name],
                shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkPlanes["XY Plane"]),
                0, None, None
            )
            mate = self.main_assy_def.Constraints.AddMateConstraint2(
                self.main_assy_def.WorkAxes[axis_name],
                shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkAxes["Y Axis"]),
                0, 24833, 24833, 115459, None, None
            )

            shell_proxy = self.find_occurrence(occurrences=self.main_assy_def.Occurrences, name="10Tx2100x")
            face = shell_proxy.Definition.SurfaceBodies[0].Faces[0]
            shell_face_proxy = shell_proxy.CreateGeometryProxy(face)

            tangent = self.main_assy_def.Constraints.AddTangentConstraint(
                shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkPlanes["XZ Plane"]),
                shell_face_proxy,
                False, "140 mm"
            )
            logger.info("Assembly constraints added.")
        except Exception as e:
            logger.error(f"Failed to add constraints: {e}")
            raise

    def cut_jacket_nozzle_length(self, nozzle_occurrence, axis_name="Y Axis"):
        """Performs revolve cut operation on nozzle."""
        try:
            yz_plane = nozzle_occurrence.Definition.WorkPlanes["YZ Plane"]
            yz_plane_proxy = nozzle_occurrence.CreateGeometryProxy(yz_plane)
            cut_sketch = self.main_assy_def.Sketches.Add(yz_plane_proxy)

            shell_proxy = self.find_occurrence(occurrences=self.main_assy_def.Occurrences, name="10Tx2100x")
            edge = shell_proxy.Definition.SurfaceBodies[0].Edges.Item(7)
            edge_proxy = shell_proxy.CreateGeometryProxy(edge)
            edge_proj = cut_sketch.AddByProjectingEntity(edge_proxy)

            nozzle_axis = nozzle_occurrence.Definition.WorkAxes[axis_name]
            nozzle_axis_proxy = nozzle_occurrence.CreateGeometryProxy(nozzle_axis)
            axis_proj = cut_sketch.AddByProjectingEntity(nozzle_axis_proxy)
            axis_proj.CenterLine = True

            pt2d = self.tg.CreatePoint2d(0.0, 0.0)
            skpt = cut_sketch.SketchPoints.Add(pt2d, False)

            width, height = 5.0, 15.0
            pt1 = cut_sketch.ModelToSketchSpace(self.tg.CreatePoint(0.0, 0.0, 0.0))
            pt2 = cut_sketch.ModelToSketchSpace(self.tg.CreatePoint(width, height, 0.0))
            rect = cut_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)

            fourth_line_end = rect.Item(3).EndSketchPoint
            geo_const = cut_sketch.GeometricConstraints
            geo_const.AddHorizontalAlign(fourth_line_end, skpt)
            geo_const.AddCollinear(axis_proj, rect.Item(3), True, True)
            geo_const.AddCoincident(skpt, edge_proj)

            dim_constraints = cut_sketch.DimensionConstraints

            mid = self.create_point2d_mid(fourth_line_end, skpt)
            dim1 = dim_constraints.AddTwoPointDistance(fourth_line_end, skpt, 19203, mid, False)
            dim1.Parameter.Expression = "2 mm"

            start_pt = rect.Item(3).StartSketchPoint
            mid = self.create_point2d_mid(start_pt, fourth_line_end)
            dim2 = dim_constraints.AddTwoPointDistance(start_pt, fourth_line_end, 19203, mid, False)
            dim2.Parameter.Expression = "150 mm"

            line2 = rect.Item(2)
            mid = self.create_point2d_mid(line2.StartSketchPoint, line2.EndSketchPoint)
            dim3 = dim_constraints.AddTwoPointDistance(line2.StartSketchPoint, line2.EndSketchPoint, 19203, mid, False)
            dim3.Parameter.Expression = "50 mm"

            # Finalize sketch
            cut_sketch.Solve()
            cut_sketch.UpdateProfiles()
            cut_sketch.Profiles.AddForSolid()
            cut_sketch.UpdateProfiles()
            profile = cut_sketch.Profiles.Item(1)

            # Revolve feature
            part_def = self.inv_app.ActiveDocument.ComponentDefinition
            revolve_cut = part_def.Features.RevolveFeatures.AddFull(profile, axis_proj, 20482)
            
            self.remove_participants(revolve_cut)

            logger.info("Jacket nozzle cut completed.")
        except Exception as e:
            logger.error(f"Failed to cut jacket nozzle: {e}")
            raise

    def build_first_jacket_nozzle(self):
        sketch, rect_lines = self.add_jacket_nozzle_top()

        # sketch = self.main_assy_def.Sketches.Item(self.main_assy_def.Sketches.Count)  # Last added sketch
        # bottom_line = sketch.SketchLines.Item(1)

        revolve = self.create_revolve_feature(sketch=sketch, rect_lines=rect_lines)
        self.remove_participants(revolve)
        axis = self.add_axis_from_cylinder(revolve)

        nozzle_occ = self.place_component(self.item["filepath"], revolve.Faces.Item(1).Geometry.BasePoint)
        self.add_constraints(nozzle_occ)
        self.cut_jacket_nozzle_length(nozzle_occ)

        logger.info("First Jacket Nozzle at Top (Shell) Finish")
