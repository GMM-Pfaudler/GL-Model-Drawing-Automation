import math
import win32com.client
import win32gui
import time
import os
from services.inventor_helper_service import FirstJacketNozzleBuilder


class Inventor:
    def __init__(self):
        pass

    def open(self, files):
        part_path = files[0]
        if not os.path.isfile(part_path):
            raise FileNotFoundError(f"File not found: {part_path}")
        
        invApp = win32com.client.Dispatch("Inventor.Application")
        invApp.Visible = True

        part_doc = invApp.Documents.Open(part_path)
        print("Opened:", part_doc.DisplayName)
        time.sleep(1)

        window_title = invApp.Caption
        hwnd = win32gui.FindWindow(None, window_title)

        if hwnd:
            win32gui.ShowWindow(hwnd, 5)  # SW_SHOW
            win32gui.SetForegroundWindow(hwnd)
            print("Inventor window brought to the front.")
            return True
        else:
            print("Could not find the Inventor window.")
            return False
        
    def generate(self, components):
        # Start Inventor
        inv_app = win32com.client.Dispatch("Inventor.Application")
        inv_app.Visible = True

        # Get TransientGeometry
        tg = inv_app.TransientGeometry

        # Create a new Assembly document: Main Assembly
        main_assy_doc = inv_app.Documents.Add("12291", inv_app.FileManager.GetTemplateFile("12291", "8963"), True)
        main_assy_def = main_assy_doc.ComponentDefinition
        monoblock = jacket = diapharm = sidebracket = jacketnozzle = None

        for idx, item in enumerate(components):
            if item["component"] == 'monoblock':
                monoblock = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                monoblock.Grounded = False

                # Main Assembly Work Axes and Work Planes
                main_y_axis = main_assy_def.WorkAxes["Y Axis"]
                main_xy_plane = main_assy_def.WorkPlanes["XY Plane"]
                main_xz_plane = main_assy_def.WorkPlanes["XZ Plane"]

                # Monoblock Work Axes and Work Planes
                monoblock_y_axis = monoblock.CreateGeometryProxy(monoblock.Definition.WorkAxes["Y Axis"]) # This is important !!
                monoblock_xy_plane = monoblock.CreateGeometryProxy(monoblock.Definition.WorkPlanes["XY Plane"])
                monoblock_xz_plane = monoblock.CreateGeometryProxy(monoblock.Definition.WorkPlanes["XZ Plane"])
                
                # Constraints for Monoblock        
                monoblock_mate_y = main_assy_def.Constraints.AddMateConstraint2(main_y_axis, monoblock_y_axis, 0, 24833, 24833, 115459, None, None)
                monoblock_flush_xy = main_assy_def.Constraints.AddFlushConstraint(main_xy_plane, monoblock_xy_plane, 0, None, None)
                monoblock_flush_xz = main_assy_def.Constraints.AddFlushConstraint(main_xz_plane, monoblock_xz_plane, 0, None, None)
            
            elif item["component"] == 'jacket':
                print("Start jacket")
                jacket = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                jacket.Grounded = False

                # Monoblock Work Axes and Work Planes
                monoblock_y_axis = monoblock.CreateGeometryProxy(monoblock.Definition.WorkAxes["Y Axis"]) # This is important !!
                monoblock_xy_plane = monoblock.CreateGeometryProxy(monoblock.Definition.WorkPlanes["XY Plane"])
                monoblock_xz_plane = monoblock.CreateGeometryProxy(monoblock.Definition.WorkPlanes["XZ Plane"])

                # Jacket Work Axes and Work Planes
                jacket_y_axis = jacket.CreateGeometryProxy(jacket.Definition.WorkAxes["Y Axis"])
                jacket_xy_plane = jacket.CreateGeometryProxy(jacket.Definition.WorkPlanes["XY Plane"])
                jacket_xz_plane = jacket.CreateGeometryProxy(jacket.Definition.WorkPlanes["XZ Plane"])
                
                # Constraints for Jacket        
                jacket_mate_y = main_assy_def.Constraints.AddMateConstraint2(monoblock_y_axis, jacket_y_axis, 0, 24833, 24833, 115459, None, None)
                jacket_flush_xy = main_assy_def.Constraints.AddFlushConstraint(monoblock_xy_plane, jacket_xy_plane, 0, None, None)
                jacket_flush_xz = main_assy_def.Constraints.AddFlushConstraint(jacket_xz_plane, monoblock_xz_plane, "52 mm", None, None)

                print("End jacket")

                # JSR CUT
                print("JSR mounting cut start")
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
                glass_9100 = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="9100")
                revolve_feature.RemoveParticipant(glass_9100)
                jacket_shell = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="10Tx2100x")
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

                print("print")

            elif item["component"] == 'diapharmring':
                print("Start diapharmring")
                diapharm = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                diapharm.Grounded = False

                btm_jcr = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="BTM JSR")

                # Bottom JSR Work Axes and Work Planes
                btm_jcr_y_axis = btm_jcr.CreateGeometryProxy(btm_jcr.Definition.WorkAxes["Y Axis"])
                btm_jcr_xy_plane = btm_jcr.CreateGeometryProxy(btm_jcr.Definition.WorkPlanes["XY Plane"])
                btm_jcr_xz_plane = btm_jcr.CreateGeometryProxy(btm_jcr.Definition.WorkPlanes["XZ Plane"])
                
                # Diapharm Ring Work Axes and Work Planes
                diapharm_y_axis = diapharm.CreateGeometryProxy(diapharm.Definition.WorkAxes["Y Axis"])
                diapharm_xy_plane = diapharm.CreateGeometryProxy(diapharm.Definition.WorkPlanes["XY Plane"])
                diapharm_xz_plane = diapharm.CreateGeometryProxy(diapharm.Definition.WorkPlanes["XZ Plane"])
                
                # Constraints for Diapharm Ring
                diapharm_mate_y = main_assy_def.Constraints.AddMateConstraint2(btm_jcr_y_axis, diapharm_y_axis, 0, 24833, 24833, 115459, None, None)
                diapharm_flush_xy = main_assy_def.Constraints.AddFlushConstraint(btm_jcr_xy_plane, diapharm_xy_plane, 0, None, None)
                diapharm_flush_xz = main_assy_def.Constraints.AddFlushConstraint(diapharm_xz_plane, btm_jcr_xz_plane, "40 mm", None, None)     

                print("Start Bottom JSR Cut")
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

                print("End diapharmring")

            elif item["component"] == 'sidebracket':
                print("Start sidebracket")
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
                sidebracket_y_axis = sidebracket.CreateGeometryProxy(sidebracket.Definition.WorkAxes["Y Axis"])
                sidebracket_xy_plane = sidebracket.CreateGeometryProxy(sidebracket.Definition.WorkPlanes["XY Plane"])
                sidebracket_xz_plane = sidebracket.CreateGeometryProxy(sidebracket.Definition.WorkPlanes["XZ Plane"])

                # Constraints for Side Bracket
                sidebracket_mate_y = main_assy_def.Constraints.AddMateConstraint2(jacket_y_axis, sidebracket_y_axis, 0, 24833, 24833, 115459, None, None)
                # sidebracket_flush_xy = main_assy_def.Constraints.AddFlushConstraint(jacket_xy_plane, sidebracket_xy_plane, 0, None, None)
                sidebracket_angle_xy = main_assy_def.Constraints.AddAngleConstraint(jacket_xy_plane, sidebracket_xy_plane, 0, 78593, None, None, None)
                sidebracket_flush_xz = main_assy_def.Constraints.AddFlushConstraint(sidebracket_xz_plane, ref_plane_proxy_top, "535 mm", None, None)

                # Adding 4 side bracket at 90.0 degree with corresponds to Y-axis
                transient_objs = inv_app.TransientObjects
                object_collection = transient_objs.CreateObjectCollection()
                object_collection.Add(sidebracket)
                pattern_axis = monoblock.CreateGeometryProxy(monoblock.Definition.WorkAxes["Y Axis"])
                main_assy_def.OccurrencePatterns.AddCircularPattern(object_collection, pattern_axis, True, "90 deg", 4)
                
                print("End sidebracket")

            elif item["component"] == 'jacketnozzle_shell':
                # builder = FirstJacketNozzleBuilder(inv_app, tg, main_assy_def, monoblock, item)
                # builder.build_first_jacket_nozzle()
                # # ---------------------------------------------------- First Jacket Nozzle at Top (Shell) Start ------------------------------------------
                # Set rotation angle - New Plane
                print("First Jacket Nozzle at Top (Shell) Start")
                shell_nozzle1_angle = -28
                angle_rad = math.radians(shell_nozzle1_angle)
                origin = tg.CreatePoint(0.0, 0.0, 0.0)
                x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
                y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

                # Add Work Plane: N16_Plane
                shell_nozzle1_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
                shell_nozzle1_angled_plane.Visible = True
                shell_nozzle1_angled_plane.Name = "N16_Plane"
                shell_nozzle1_angled_plane.Grounded = True

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

                main_N16_Plane = main_assy_def.WorkPlanes['N16_Plane']
                main_N16_Axis = main_assy_def.WorkAxes["N16_Axis"]
                jacket_shell = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="10Tx2100x")
                jacket_shell_face = jacket_shell.Definition.SurfaceBodies[0].Faces[0]
                shell_face_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_face)

                # Adding Constraints

                jacket_nozzle_flush = main_assy_def.Constraints.AddFlushConstraint(main_N16_Plane, shell_jacket_nozzle1_xy_plane, 0, None, None)
                jacket_nozzle_mate_y = main_assy_def.Constraints.AddMateConstraint2(main_N16_Axis, shell_jacket_nozzle1_y_axis, 0, 24833, 24833, 115459, None, None)
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

                print("First Jacket Nozzle at Top (Shell) Finish")
                # ------------------------------ First Jacket Nozzle at Top (Shell) Finish ------------------------------------------------------------


                # ------------------------------ Second Jacket Nozzle at Top (Shell) Start ------------------------------------------------------------
                # === NEW Nozzle at -208 Degrees ===
                # Set rotation angle for second nozzle
                print("Second Jacket Nozzle at Top (Shell) Start")
                shell_nozzle2_angle = -135
                shell_nozzle2_angle_rad = math.radians(shell_nozzle2_angle)
                x_axis_2 = tg.CreateUnitVector(math.cos(shell_nozzle2_angle_rad), 0.0, -math.sin(shell_nozzle2_angle_rad))
                y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)
                origin = tg.CreatePoint(0.0, 0.0, 0.0)

                # Create new plane for second nozzle
                shell_nozzle2_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis_2, y_axis)
                shell_nozzle2_angled_plane.Visible = True
                shell_nozzle2_angled_plane.Grounded = True
                shell_nozzle2_angled_plane.Name = "N15_Plane"

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
                y_axis_2 = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2.Definition.WorkAxes["Y Axis"])
                xy_plane_2 = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2.Definition.WorkPlanes["XY Plane"])
                xz_plane_2 = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2.Definition.WorkPlanes["XZ Plane"])
                shell_face_proxy_2 = jacket_shell.CreateGeometryProxy(jacket_shell_face)

                # Add constraints
                flush_2 = main_assy_def.Constraints.AddFlushConstraint(shell_nozzle2_angled_plane, xy_plane_2, 0, None, None)
                mate_y_2 = main_assy_def.Constraints.AddMateConstraint2(axis_2, y_axis_2, 0, 24833, 24833, 115459, None, None)
                tangent_2 = main_assy_def.Constraints.AddTangentConstraint(xz_plane_2, shell_face_proxy_2, False, "140 mm")

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


                print("Second Jacket Nozzle at Top (Shell) Finish")
                # ------------------------------ Second Jacket Nozzle at Top (Shell) Finish ------------------------------------------------------------

            elif item["component"] == 'jacketnozzle_bottom':
                # ------------------------------ Third Jacket Nozzle at Bottom Start ------------------------------------------------------------
                print("Third Jacket Nozzle at Bottom Start")
                bottom_nozzle1_angle = -90
                angle_rad = math.radians(bottom_nozzle1_angle)
                origin = tg.CreatePoint(0.0, 0.0, 0.0)
                x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
                y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

                # Add Work Plane: N11_Plane
                bottom_nozzle1_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
                bottom_nozzle1_angled_plane.Visible = True
                bottom_nozzle1_angled_plane.Name = "N11_Plane"
                bottom_nozzle1_angled_plane.Grounded = True

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
                y_axis_3 = jacketnozzle_3.CreateGeometryProxy(jacketnozzle_3.Definition.WorkAxes["Y Axis"])
                xy_plane_3 = jacketnozzle_3.CreateGeometryProxy(jacketnozzle_3.Definition.WorkPlanes["XY Plane"])
                xz_plane_3 = jacketnozzle_3.CreateGeometryProxy(jacketnozzle_3.Definition.WorkPlanes["XZ Plane"])
                # xy_plane_main = main_assy_def.WorkPlanes['XY Plane']

                # Add constraints
                flush_3 = main_assy_def.Constraints.AddFlushConstraint(bottom_nozzle1_angled_plane, xy_plane_3, 0, None, None)
                mate_y_3 = main_assy_def.Constraints.AddMateConstraint2(axis_3, y_axis_3, 0, 24833, 24833, 115459, None, None)
                mate_xz_3 = main_assy_def.Constraints.AddMateConstraint2(xz_plane_3, xz_plane_proxy, "90 mm", 24833, 24833, 115460, None, None)

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

                print("Third Jacket Nozzle at Bottom End")
                # ------------------------------ Third Jacket Nozzle at Bottom End ------------------------------------------------------------

                # ------------------------------ Forth Jacket Nozzle at Bottom Start ------------------------------------------------------------
                print("Forth Jacket Nozzle at Bottom Start")

                bottom_nozzle2_angle = -270
                angle_rad = math.radians(bottom_nozzle2_angle)
                origin = tg.CreatePoint(0.0, 0.0, 0.0)
                x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
                y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

                # Add Work Plane: N17_Plane
                bottom_nozzle2_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
                bottom_nozzle2_angled_plane.Visible = True
                bottom_nozzle2_angled_plane.Name = "N17_Plane"
                bottom_nozzle2_angled_plane.Grounded = True

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
                y_axis_4 = jacketnozzle_4.CreateGeometryProxy(jacketnozzle_4.Definition.WorkAxes["Y Axis"])
                xy_plane_4 = jacketnozzle_4.CreateGeometryProxy(jacketnozzle_4.Definition.WorkPlanes["XY Plane"])
                xz_plane_4 = jacketnozzle_4.CreateGeometryProxy(jacketnozzle_4.Definition.WorkPlanes["XZ Plane"])
                # xy_plane_main = main_assy_def.WorkPlanes['XY Plane']

                # Add constraints
                flush_4 = main_assy_def.Constraints.AddFlushConstraint(bottom_nozzle2_angled_plane, xy_plane_4, 0, None, None)
                mate_y_4 = main_assy_def.Constraints.AddMateConstraint2(axis_4, y_axis_4, 0, 24833, 24833, 115459, None, None)
                mate_xz_4 = main_assy_def.Constraints.AddMateConstraint2(xz_plane_4, xz_plane_proxy, "90 mm", 24833, 24833, 115460, None, None)

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

                print("Forth Jacket Nozzle at Bottom End")
            
            elif item.get("component") == 'ms_coupling':
                print("Start MS COUPLING")
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

                glass_9100 = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="GL_MBCE-06300-2020-000")
                revolve_feature.RemoveParticipant(glass_9100)

                ms_coupling = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                ms_coupling.Grounded = False
                
                ms_coupling_y_axis_proxy = ms_coupling.CreateGeometryProxy(ms_coupling.Definition.WorkAxes["Y Axis"])
                ms_coupling_xy_plan_proxy = ms_coupling.CreateGeometryProxy(ms_coupling.Definition.WorkPlanes["XY Plane"])
                ms_coupling_xz_plan_proxy = ms_coupling.CreateGeometryProxy(ms_coupling.Definition.WorkPlanes["XZ Plane"])
                
                mate_y_ms_coupling = main_assy_def.Constraints.AddMateConstraint2(ms_coupling_y_axis_proxy, JSR_MSS_N13_Axis_proxy, 0, 24833, 24833, 115459, None, None)
                flush_ms_coupling_1 = main_assy_def.Constraints.AddFlushConstraint(ms_coupling_xy_plan_proxy, JSR_MSS_N13_Degree_plane_proxy, 0, None, None)
                flush_ms_coupling_2 = main_assy_def.Constraints.AddFlushConstraint(ms_coupling_xz_plan_proxy, JSR_MSS_N13_REF_plane_proxy, "17 mm", None, None)
                
                # MS COUPLING TOP - End


                # MS COUPLING BOTTOM - Start
                print("Bottom MS COUPLING Start")
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


                print(JSR_MSS)

            elif item.get("component") == 'manhole_gasket_1':
                print("manhole_gasket constraint start")
                monoblock = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="MBCE-06300-2020-000")
                # manhole_stump= self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="01-GPF-9891 R2_20Tx500NBx95HT_MH_SA836M:1")
                manhole_stump = self.find_occurrence_by_keyword_recursive(occurrences=monoblock.SubOccurrences, target_keyword="3817-0018")
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

            
            elif item.get("component") == 'bush_type_protection_ring':
                print("bush_type_protection_ring start")
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


            elif item.get("component") == 'manhole_gasket_2':
                print("manhole_gasket_2 constraint start")
                monoblock = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="MBCE-06300-2020-000")
                # manhole_stump= self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="01-GPF-9891 R2_20Tx500NBx95HT_MH_SA836M:1")
                manhole_stump = self.find_occurrence_by_keyword_recursive(occurrences=monoblock.SubOccurrences, target_keyword="3817-0018")
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
            
            elif item.get("component") == 'manhole_cover':
                print("manhole_cover start")
                PTFE_envelop_2 = self.find_occurrence_recursive(occurrences=manhole_gasket_2.SubOccurrences, target_name='DN500_605_521_8.9_ROUND ENVELOPE_MANHOLE:1')
                gasket_ref_plane_2 = PTFE_envelop_2.CreateGeometryProxy(PTFE_envelop_2.Definition.WorkPlanes["GASKET REF PLANE"])

                manhole_cover = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                manhole_cover.Grounded = False

                manhole_cover_y_axis_proxy = manhole_cover.CreateGeometryProxy(manhole_cover.Definition.WorkAxes["Y Axis"])
                manhole_cover_xy_plane_proxy = manhole_cover.CreateGeometryProxy(manhole_cover.Definition.WorkPlanes["XY Plane"])
                manhole_cover_xz_plane_proxy = manhole_cover.CreateGeometryProxy(manhole_cover.Definition.WorkPlanes["XZ Plane"])
                
                manhole_cover_mate_1 = main_assy_def.Constraints.AddMateConstraint2(manhole_stump_y_axis_proxy, manhole_cover_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                manhole_cover_mate_2 = main_assy_def.Constraints.AddFlushConstraint(manhole_stump_xy_plane_proxy, manhole_cover_xy_plane_proxy, 0, None, None)
                manhole_cover_flush_1 = main_assy_def.Constraints.AddFlushConstraint(manhole_cover_xz_plane_proxy, gasket_ref_plane_2, 0, None, None)

                print("manhole_cover end")
            
            elif item.get("component") == 'manhole_c_clamp':
                print("manhole_c_clamp start")

                manhole_c_clamp = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                manhole_c_clamp.Grounded = False

                manhole_stump = self.find_occurrence_by_keyword_recursive(occurrences=monoblock.SubOccurrences, target_keyword="3817-0018")
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
                print("manhole_c_clamp end")

            elif item.get("component") == 'manhole_sight_glass_gasket':

                print("manhole_sight_glass_gasket start")

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

                print("manhole_sight_glass_gasket end")

            elif item.get("component") == 'spring_balance_assembly':

                print("Start: spring_balance_assembly")

                spring_balance_assembly = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                spring_balance_assembly.Grounded = False

                manhole_stump = self.find_occurrence_by_keyword_recursive(occurrences=monoblock.SubOccurrences, target_keyword="3817-0018")
                stump_xy_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["XY Plane"])
                # stump_xz_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["XZ Plane"])
                stump_yz_plane_proxy = manhole_stump.CreateGeometryProxy(manhole_stump.Definition.WorkPlanes["YZ Plane"])

                spring_balance_assembly_xy_plane_proxy = spring_balance_assembly.CreateGeometryProxy(spring_balance_assembly.Definition.WorkPlanes["XY Plane"])
                spring_balance_assembly_yz_plane_proxy = spring_balance_assembly.CreateGeometryProxy(spring_balance_assembly.Definition.WorkPlanes["YZ Plane"])

                spring_balance_assembly_flush_1 = main_assy_def.Constraints.AddFlushConstraint(spring_balance_assembly_xy_plane_proxy, stump_xy_plane_proxy, -32.3, None, None)
                spring_balance_assembly_angle_xy = main_assy_def.Constraints.AddAngleConstraint(stump_xy_plane_proxy, spring_balance_assembly_xy_plane_proxy, 0, 78593, None, None, None)
                spring_balance_assembly_flush_2 = main_assy_def.Constraints.AddFlushConstraint(spring_balance_assembly_yz_plane_proxy, stump_yz_plane_proxy, 0.0, None, None)
            
            elif item.get("component") == 'manhole_sight_glass':
                print("Start: manhole_sight_glass")

                manhole_sight_glass = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                manhole_sight_glass.Grounded = False

                manhole_sight_glass_y_axis_proxy = manhole_sight_glass.CreateGeometryProxy(manhole_sight_glass.Definition.WorkAxes["Y Axis"])
                manhole_sight_glass_xy_plane_proxy = manhole_sight_glass.CreateGeometryProxy(manhole_sight_glass.Definition.WorkPlanes["XY Plane"])
                manhole_sight_glass_yz_plane_proxy = manhole_sight_glass.CreateGeometryProxy(manhole_sight_glass.Definition.WorkPlanes["YZ Plane"])
                manhole_sight_glass_xz_plane_proxy = manhole_sight_glass.CreateGeometryProxy(manhole_sight_glass.Definition.WorkPlanes["XZ Plane"])
                
                SLIT_ENVELOPE = self.find_occurrence_recursive(occurrences=manhole_sight_glass_gasket.SubOccurrences, target_name="DN100_158_105_5.2_SLIT ENVELOPE")
                gasket_ref_plane = SLIT_ENVELOPE.CreateGeometryProxy(SLIT_ENVELOPE.Definition.WorkPlanes["GASKET REF PLANE"])

                manhole_sight_glass_mate1 = main_assy_def.Constraints.AddMateConstraint2(manhole_sight_glass_y_axis_proxy, manhole_cover_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                manhole_sight_glass_mate2 = main_assy_def.Constraints.AddMateConstraint2(manhole_sight_glass_xz_plane_proxy, gasket_ref_plane, 0, 24833, 24833, 115459, None, None)
                print("End: manhole_sight_glass")
            
            elif item.get("component") == 'manhole_sight_flange':
                print("Start: manhole_sight_flange")

                manhole_sight_flange = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
                manhole_sight_flange.Grounded = False

                manhole_sight_flange_y_axis_proxy = manhole_sight_flange.CreateGeometryProxy(manhole_sight_flange.Definition.WorkAxes["Y Axis"])
                manhole_sight_flange_ass_plane_proxy = manhole_sight_flange.CreateGeometryProxy(manhole_sight_flange.Definition.WorkPlanes["ASSEMBLY PLANE"])
                manhole_sight_flange_xy_plane_proxy = manhole_sight_flange.CreateGeometryProxy(manhole_sight_flange.Definition.WorkPlanes["XY PLANE"])

                manhole_sight_flange_mate1 = main_assy_def.Constraints.AddMateConstraint2(manhole_sight_flange_y_axis_proxy, manhole_sight_glass_y_axis_proxy, 0, 24833, 24833, 115459, None, None)
                manhole_sight_glass_gasket_flush_2 = main_assy_def.Constraints.AddFlushConstraint(manhole_sight_glass_xz_plane_proxy, manhole_sight_flange_ass_plane_proxy, 0.3, None, None)
                manhole_sight_flange_mate2 = main_assy_def.Constraints.AddMateConstraint(manhole_cover_xy_plane_proxy, manhole_sight_flange_xy_plane_proxy, 0, 24833, 24833, None, None)

                print("End: manhole_sight_flange")
        return True
    
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



    # def find_named_workplane_in_occurrence(self, occurrences, target_name):
    #     try:
    #         for occurrence in occurrences:
    #             wp = occurrence.Definition.WorkPlanes.Item(target_name)
    #             if wp is not None:
    #                 return occurrence.CreateGeometryProxy(wp)
    #             else:
    #                 if hasattr(occurrence.Definition, "Occurrences"):
    #                     for sub_occ in occurrence.Definition.Occurrences:
    #                         result = self.find_named_workplane_in_occurrence(sub_occ, target_name)
    #                         if result:
    #                             return result
    #     except:
    #         pass  # Not a part or not accessible
    #     return None


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
