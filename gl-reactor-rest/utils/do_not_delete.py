#  elif item["component"] == 'jacketnozzle_shell':
#                 # builder = FirstJacketNozzleBuilder(inv_app, tg, main_assy_def, monoblock, item)
#                 # builder.build_first_jacket_nozzle()
#                 # # ---------------------------------------------------- First Jacket Nozzle at Top (Shell) Start ------------------------------------------
#                 # Set rotation angle - New Plane
#                 print("First Jacket Nozzle at Top (Shell) Start")
#                 shell_nozzle1_angle = -28
#                 angle_rad = math.radians(shell_nozzle1_angle)
#                 origin = tg.CreatePoint(0.0, 0.0, 0.0)
#                 x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
#                 y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

#                 # Add Work Plane: N16_Plane
#                 shell_nozzle1_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
#                 shell_nozzle1_angled_plane.Visible = True
#                 shell_nozzle1_angled_plane.Name = "N16_Plane"
#                 shell_nozzle1_angled_plane.Grounded = True

#                 # Add Sketch
#                 shell_jacket_nozzle1_sketch = main_assy_def.Sketches.Add(shell_nozzle1_angled_plane)

#                 # Add Y-axis project geometry
#                 main_y_axis = main_assy_def.WorkAxes["Y Axis"]
#                 yaxis_pg = shell_jacket_nozzle1_sketch.AddByProjectingEntity(main_y_axis)

#                 L_nozzle_occ = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="L_DN150")

#                 width = 10.0
#                 height = 5.0
#                 # Create 2D corner points in sketch space
#                 bottom_left_pt = shell_jacket_nozzle1_sketch.ModelToSketchSpace(tg.CreatePoint(-width/2, 0, 0))  # Bottom-left
#                 top_right_pt = shell_jacket_nozzle1_sketch.ModelToSketchSpace(tg.CreatePoint(width/2, height, 0))  # Top-right

#                 # Add rectangle
#                 rect_lines = shell_jacket_nozzle1_sketch.SketchLines.AddAsTwoPointRectangle(bottom_left_pt, top_right_pt)

#                 # Get bottom line (first item)
#                 bottom_line = rect_lines.Item(1)
#                 bottom_line.Centerline = True
                                
#                 # Get the XZ plane of L_nozzle_occ
#                 L_nozzle_xz_plane = L_nozzle_occ.Definition.WorkPlanes["XZ Plane"]
#                 L_nozzle_xz_plane_proxy = L_nozzle_occ.CreateGeometryProxy(L_nozzle_xz_plane)

#                 # Project XZ plane into the sketch
#                 proj_line = shell_jacket_nozzle1_sketch.AddByProjectingEntity(L_nozzle_xz_plane_proxy)

#                 # Ensure the projected line is valid
#                 if not hasattr(proj_line, "StartSketchPoint"):
#                     raise Exception("Projected XZ plane did not return a SketchLine.")

#                 # Get points from bottom line and projected line
#                 bottom_line_start_pt1 = bottom_line.StartSketchPoint
#                 project_line_start_pt2 = proj_line.StartSketchPoint

#                 # Validate points
#                 if bottom_line_start_pt1 is None or project_line_start_pt2 is None:
#                     raise Exception("One or both SketchPoints are None.")

#                 # Create a text point for dimension label (optional but required by API)
#                 # Use midpoint between pt1 and pt2 as a reasonable label position
#                 mid_x = (bottom_line_start_pt1.Geometry.X + project_line_start_pt2.Geometry.X) / 2
#                 mid_y = (bottom_line_start_pt1.Geometry.Y + project_line_start_pt2.Geometry.Y) / 2
#                 text_point = inv_app.TransientGeometry.CreatePoint2d(mid_x, mid_y)

#                 # Add vertical dimension constraint
#                 dim_constraints = shell_jacket_nozzle1_sketch.DimensionConstraints
#                 dimension = dim_constraints.AddTwoPointDistance(bottom_line_start_pt1, project_line_start_pt2, 19202, text_point, False)

#                 # Set the distance value (assuming mm)
#                 dimension.Parameter.Expression = '2350 mm'

#                 second_line = rect_lines.Item(2)  

#                 # Add collinear constraint
#                 geo_constraints = shell_jacket_nozzle1_sketch.GeometricConstraints
#                 geo_constraints.AddCollinear(yaxis_pg, second_line)

#                 # Get second and fourth lines of the rectangle
#                 fourth_line = rect_lines.Item(4)  # Likely the right vertical edge

#                 # Get sketch points from each line
#                 second_line_start_pt1 = second_line.StartSketchPoint
#                 fourth_line_start_pt2 = fourth_line.StartSketchPoint

#                 # Validate points
#                 if second_line_start_pt1 is None or fourth_line_start_pt2 is None:
#                     raise Exception("One or both sketch points are None.")

#                 # Compute midpoint for dimension text placement
#                 mid_x = (second_line_start_pt1.Geometry.X + fourth_line_start_pt2.Geometry.X) / 2
#                 mid_y = (second_line_start_pt1.Geometry.Y + fourth_line_start_pt2.Geometry.Y) / 2
#                 text_point = inv_app.TransientGeometry.CreatePoint2d(mid_x, mid_y)

#                 # Add horizontal dimension constraint
#                 dim_constraints = shell_jacket_nozzle1_sketch.DimensionConstraints
#                 horizontal_dim = dim_constraints.AddTwoPointDistance(second_line_start_pt1, fourth_line_start_pt2, 19203, text_point, False)

#                 # Set the dimension to the actual rectangle width (10.0 mm)
#                 horizontal_dim.Parameter.Expression = "5000 mm"

#                 # Get first and third lines of the rectangle
#                 first_line = rect_lines.Item(1)   # Bottom edge
#                 third_line = rect_lines.Item(3)   # Top edge

#                 # Get sketch points (use start point for consistency)
#                 first_line_start_pt1 = first_line.StartSketchPoint
#                 third_line_start_pt2 = third_line.StartSketchPoint

#                 # Validate points
#                 if first_line_start_pt1 is None or third_line_start_pt2 is None:
#                     raise Exception("One or both sketch points are None.")

#                 # Compute midpoint for dimension text
#                 mid_x = (first_line_start_pt1.Geometry.X + third_line_start_pt2.Geometry.X) / 2
#                 mid_y = (first_line_start_pt1.Geometry.Y + third_line_start_pt2.Geometry.Y) / 2
#                 text_point = inv_app.TransientGeometry.CreatePoint2d(mid_x, mid_y)

#                 # Add vertical dimension
#                 vertical_dim = shell_jacket_nozzle1_sketch.DimensionConstraints.AddTwoPointDistance(first_line_start_pt1, third_line_start_pt2, 19202, text_point, False)

#                 # Set the value (height of the rectangle)
#                 vertical_dim.Parameter.Expression = "45 mm"

#                 # Solve the sketch: Needs to update profile after adding for solid.
#                 shell_jacket_nozzle1_sketch.Solve()
#                 shell_jacket_nozzle1_sketch.UpdateProfiles()
#                 shell_jacket_nozzle1_sketch.Profiles.AddForSolid()
#                 shell_jacket_nozzle1_sketch.UpdateProfiles()

#                 # === Step 1: Get the profile from the sketch ===
#                 profile = shell_jacket_nozzle1_sketch.Profiles.Item(1)  # Assumes rectangle forms a closed profile

#                 # === Step 2: Get the axis (centerline) ===
#                 axis_line = bottom_line  # Bottom line marked as Centerline earlier

#                 # === Step 3: Access the part definition (not assembly) ===
#                 # This must be run inside a part document, not an assembly
#                 # For example, if you're in jacketnozzle component part:
#                 part_def = inv_app.ActiveDocument.ComponentDefinition  # Must be a PartDocument

#                 # === Step 4: Revolve the sketch using AddFull ===
#                 revolve_features = part_def.Features.RevolveFeatures
#                 revolve_feature = revolve_features.AddFull(profile, axis_line, 20482)

#                 # Remove participants - components or occurrences
#                 # 1) Remove Inner shell
#                 inner_shell = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="INNER SHELL")
#                 revolve_feature.RemoveParticipant(inner_shell)
#                 # 2) Remove 9100 glass 
#                 glass_9100 = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="9100")
#                 revolve_feature.RemoveParticipant(glass_9100)

#                 # Adding Axis
#                 cylinder = revolve_feature.Faces.Item(1).Geometry  # Should be a cylinder
#                 base_pt = cylinder.BasePoint
#                 axis_vec = cylinder.AxisVector
#                 work_axis = main_assy_def.WorkAxes.AddFixed(base_pt, axis_vec, False)
#                 work_axis.Name = "N16_Axis"
#                 work_axis.Grounded = True

#                 shell_jacket_nozzle1 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 shell_jacket_nozzle1.Grounded = False

#                 # Create a transform matrix (identity to start)
#                 transform = tg.CreateMatrix()
#                 translation_vector = tg.CreateVector(base_pt.X, base_pt.Y, base_pt.Z)
#                 transform.SetTranslation(translation_vector)
#                 shell_jacket_nozzle1.Transformation = transform

#                 # Attach Jacket Nozzle with Jacket
#                 shell_jacket_nozzle1_y_axis = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkAxes["Y Axis"])
#                 shell_jacket_nozzle1_xy_plane = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkPlanes["XY Plane"])
#                 shell_jacket_jacket_nozzle1_xz_plane = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkPlanes["XZ Plane"])

#                 main_N16_Plane = main_assy_def.WorkPlanes['N16_Plane']
#                 main_N16_Axis = main_assy_def.WorkAxes["N16_Axis"]
#                 jacket_shell = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="10Tx2100x")
#                 jacket_shell_face = jacket_shell.Definition.SurfaceBodies[0].Faces[0]
#                 shell_face_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_face)

#                 # Adding Constraints

#                 jacket_nozzle_flush = main_assy_def.Constraints.AddFlushConstraint(main_N16_Plane, shell_jacket_nozzle1_xy_plane, 0, None, None)
#                 jacket_nozzle_mate_y = main_assy_def.Constraints.AddMateConstraint2(main_N16_Axis, shell_jacket_nozzle1_y_axis, 0, 24833, 24833, 115459, None, None)
#                 jacket_nozzle_tangent = main_assy_def.Constraints.AddTangentConstraint(shell_jacket_jacket_nozzle1_xz_plane, shell_face_proxy, False, "140 mm")


#                 # Start cut operation on first jacket nozzle:
#                 yz_plane = shell_jacket_nozzle1.Definition.WorkPlanes["YZ Plane"]
#                 yz_plane_proxy = shell_jacket_nozzle1.CreateGeometryProxy(yz_plane)
#                 first_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(yz_plane_proxy)

#                 jacket_shell_edge = jacket_shell.Definition.SurfaceBodies[0].Edges.Item(7) # 
#                 jacket_shell_edge_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_edge)
#                 jacket_shell_edge_pg = first_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(jacket_shell_edge_proxy)

#                 shell_jacket_nozzle1_y_axis = shell_jacket_nozzle1.Definition.WorkAxes["Y Axis"]
#                 shell_jacket_nozzle1_y_axis_proxy = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1_y_axis)
#                 shell_jacket_nozzle1_y_axis_pg = first_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(shell_jacket_nozzle1_y_axis_proxy)
#                 shell_jacket_nozzle1_y_axis_pg.CenterLine = True

#                 # # 8. Create 2D point at that location
#                 pt2d = tg.CreatePoint2d(0.0, 0.0)

#                 # 9. Add the sketch point
#                 skpt = first_jacket_nozzle_length_cut_sketch.SketchPoints.Add(pt2d, False)

#                 width = 5.0
#                 height = 15.0

#                 # Place rectangle starting at Y-axis (X = 0), going right
#                 pt1 = first_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(0.0, 0.0, 0.0))  # Bottom-left corner on Y-axis
#                 pt2 = first_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(width, height, 0.0))  # Top-right corner to the right

#                 # Add rectangle
#                 first_jacket_nozzle_length_cut_rectangle = first_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)
#                 fourth_line_end_pt = first_jacket_nozzle_length_cut_rectangle.Item(3).EndSketchPoint
#                 first_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddHorizontalAlign(fourth_line_end_pt, skpt)

#                 mid_x = (fourth_line_end_pt.Geometry.X + skpt.Geometry.X) / 2
#                 mid_y = (fourth_line_end_pt.Geometry.Y + skpt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 first_jacket_nozzle_length_cut_dim_constraints = first_jacket_nozzle_length_cut_sketch.DimensionConstraints
#                 aligned_dim = first_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_end_pt, skpt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '2 mm'
#                 first_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(skpt, jacket_shell_edge_pg)

#                 fourth_line_start_pt = first_jacket_nozzle_length_cut_rectangle.Item(3).StartSketchPoint
#                 mid_x = (fourth_line_start_pt.Geometry.X + fourth_line_end_pt.Geometry.X) / 2
#                 mid_y = (fourth_line_start_pt.Geometry.Y + fourth_line_end_pt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 aligned_dim = first_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_start_pt, fourth_line_end_pt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '150 mm'

#                 second_line_start_pt = first_jacket_nozzle_length_cut_rectangle.Item(2).StartSketchPoint
#                 second_line_end_pt = first_jacket_nozzle_length_cut_rectangle.Item(2).EndSketchPoint
#                 mid_x = (second_line_start_pt.Geometry.X + second_line_end_pt.Geometry.X) / 2
#                 mid_y = (second_line_start_pt.Geometry.Y + second_line_end_pt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)

#                 aligned_dim = first_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(second_line_start_pt, second_line_end_pt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '50 mm'

#                 forth_line = first_jacket_nozzle_length_cut_rectangle.Item(3)
#                 geo_const = first_jacket_nozzle_length_cut_sketch.GeometricConstraints
#                 geo_const.AddCollinear(shell_jacket_nozzle1_y_axis_pg, forth_line, True, True)

#                 first_jacket_nozzle_length_cut_sketch.Solve()
#                 first_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 first_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
#                 first_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 cut_sketch_profile = first_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

#                 part_def = inv_app.ActiveDocument.ComponentDefinition

#                 cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
#                 cut_sketch_revolve_feature = cut_sketch_revolve_feats.AddFull(cut_sketch_profile, shell_jacket_nozzle1_y_axis_pg, 20482)

#                 # Remove participants again
#                 cut_sketch_revolve_feature.RemoveParticipant(inner_shell)
#                 cut_sketch_revolve_feature.RemoveParticipant(glass_9100)

#                 print("First Jacket Nozzle at Top (Shell) Finish")
#                 # ------------------------------ First Jacket Nozzle at Top (Shell) Finish ------------------------------------------------------------


#                 # ------------------------------ Second Jacket Nozzle at Top (Shell) Start ------------------------------------------------------------
#                 # === NEW Nozzle at -208 Degrees ===
#                 # Set rotation angle for second nozzle
#                 print("Second Jacket Nozzle at Top (Shell) Start")
#                 shell_nozzle2_angle = -135
#                 shell_nozzle2_angle_rad = math.radians(shell_nozzle2_angle)
#                 x_axis_2 = tg.CreateUnitVector(math.cos(shell_nozzle2_angle_rad), 0.0, -math.sin(shell_nozzle2_angle_rad))
#                 y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)
#                 origin = tg.CreatePoint(0.0, 0.0, 0.0)

#                 # Create new plane for second nozzle
#                 shell_nozzle2_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis_2, y_axis)
#                 shell_nozzle2_angled_plane.Visible = True
#                 shell_nozzle2_angled_plane.Grounded = True
#                 shell_nozzle2_angled_plane.Name = "N15_Plane"

#                 # Add sketch on second plane
#                 shell_jacket_nozzle2_sketch = main_assy_def.Sketches.Add(shell_nozzle2_angled_plane)

#                 # Project Y-axis
#                 yaxis_pg_2 = shell_jacket_nozzle2_sketch.AddByProjectingEntity(main_y_axis)

#                 # Define rectangle dimensions
#                 width = 500.0
#                 height = 5.0

#                 # Place rectangle starting at Y-axis (X = 0), going right
#                 pt1 = shell_jacket_nozzle2_sketch.ModelToSketchSpace(tg.CreatePoint(0.0, 0.0, 0.0))  # Bottom-left corner on Y-axis
#                 pt2 = shell_jacket_nozzle2_sketch.ModelToSketchSpace(tg.CreatePoint(width, height, 0.0))  # Top-right corner to the right

#                 # Add rectangle
#                 second_rect_lines = shell_jacket_nozzle2_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)

#                 # Set centerline
#                 second_bottom_line = second_rect_lines.Item(1)
#                 second_bottom_line.Centerline = True

#                 # Get L_DN150 again
#                 xz_plane = L_nozzle_occ.Definition.WorkPlanes["XZ Plane"]
#                 xz_plane_proxy = L_nozzle_occ.CreateGeometryProxy(xz_plane)

#                 # Project and dimension
#                 proj_line_2 = shell_jacket_nozzle2_sketch.AddByProjectingEntity(xz_plane_proxy)

#                 # Dimension from proj_line to bottom_line
#                 second_bottom_line_start_pt1 = second_bottom_line.StartSketchPoint
#                 second_project_line_start_pt2 = proj_line_2.StartSketchPoint
#                 mid_x = (second_bottom_line_start_pt1.Geometry.X + second_project_line_start_pt2.Geometry.X) / 2
#                 mid_y = (second_bottom_line_start_pt1.Geometry.Y + second_project_line_start_pt2.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)

#                 second_dim_constraints = shell_jacket_nozzle2_sketch.DimensionConstraints
#                 vertical_dim = second_dim_constraints.AddTwoPointDistance(second_bottom_line_start_pt1, second_project_line_start_pt2, 19202, text_point, False)
#                 vertical_dim.Parameter.Expression = '2350 mm'


#                 # Height
#                 first_line = second_rect_lines.Item(1)
#                 third_line = second_rect_lines.Item(3)
#                 pt1 = first_line.StartSketchPoint
#                 pt2 = third_line.StartSketchPoint
#                 mid_x = (pt1.Geometry.X + pt2.Geometry.X) / 2
#                 mid_y = (pt1.Geometry.Y + pt2.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 vertical_dim2 = second_dim_constraints.AddTwoPointDistance(pt1, pt2, 19202, text_point, False)
#                 vertical_dim2.Parameter.Expression = "45 mm"

#                 # Solve and revolve
#                 shell_jacket_nozzle2_sketch.Solve()
#                 shell_jacket_nozzle2_sketch.UpdateProfiles()
#                 shell_jacket_nozzle2_sketch.Profiles.AddForSolid()
#                 shell_jacket_nozzle2_sketch.UpdateProfiles()
#                 profile_2 = shell_jacket_nozzle2_sketch.Profiles.Item(1)

#                 axis_line_2 = second_bottom_line
#                 revolve_feats = part_def.Features.RevolveFeatures
#                 revolve_feature_2 = revolve_feats.AddFull(profile_2, axis_line_2, 20482)

#                 # Remove participants again
#                 revolve_feature_2.RemoveParticipant(inner_shell)
#                 revolve_feature_2.RemoveParticipant(glass_9100)

#                 # Add second axis
#                 cylinder_2 = revolve_feature_2.Faces.Item(1).Geometry
#                 base_pt_2 = cylinder_2.BasePoint
#                 axis_vec_2 = cylinder_2.AxisVector
#                 axis_2 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
#                 axis_2.Name = "N15_Axis"
#                 axis_2.Grounded = True

#                 # Add second nozzle component
#                 shell_jacket_nozzle2 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 shell_jacket_nozzle2.Grounded = False

#                 # Set position
#                 transform_2 = tg.CreateMatrix()
#                 transform_2.SetTranslation(tg.CreateVector(base_pt_2.X, base_pt_2.Y, base_pt_2.Z))
#                 shell_jacket_nozzle2.Transformation = transform_2

#                 # Get proxies
#                 y_axis_2 = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2.Definition.WorkAxes["Y Axis"])
#                 xy_plane_2 = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2.Definition.WorkPlanes["XY Plane"])
#                 xz_plane_2 = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2.Definition.WorkPlanes["XZ Plane"])
#                 shell_face_proxy_2 = jacket_shell.CreateGeometryProxy(jacket_shell_face)

#                 # Add constraints
#                 flush_2 = main_assy_def.Constraints.AddFlushConstraint(shell_nozzle2_angled_plane, xy_plane_2, 0, None, None)
#                 mate_y_2 = main_assy_def.Constraints.AddMateConstraint2(axis_2, y_axis_2, 0, 24833, 24833, 115459, None, None)
#                 tangent_2 = main_assy_def.Constraints.AddTangentConstraint(xz_plane_2, shell_face_proxy_2, False, "140 mm")

#                 # Start cut revolve operation on first jacket nozzle:
#                 yz_plane = shell_jacket_nozzle2.Definition.WorkPlanes["YZ Plane"]
#                 yz_plane_proxy = shell_jacket_nozzle2.CreateGeometryProxy(yz_plane)
#                 second_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(yz_plane_proxy)

#                 # jacket_shell_edge = jacket_shell.Definition.SurfaceBodies[0].Edges.Item(7) # 
#                 # jacket_shell_edge_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_edge)
#                 jacket_shell_edge_pg = second_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(jacket_shell_edge_proxy)

#                 shell_jacket_nozzle2_y_axis = shell_jacket_nozzle2.Definition.WorkAxes["Y Axis"]
#                 shell_jacket_nozzle2_y_axis_proxy = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2_y_axis)
#                 shell_jacket_nozzle2_y_axis_pg = second_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(shell_jacket_nozzle2_y_axis_proxy)
#                 shell_jacket_nozzle2_y_axis_pg.CenterLine = True

#                 # # 8. Create 2D point at that location
#                 pt2d = tg.CreatePoint2d(0.0, 0.0)

#                 # 9. Add the sketch point
#                 skpt = second_jacket_nozzle_length_cut_sketch.SketchPoints.Add(pt2d, False)

#                 width = 5.0
#                 height = 15.0

#                 # Place rectangle starting at Y-axis (X = 0), going right
#                 pt1 = second_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(0.0, 0.0, 0.0))  # Bottom-left corner on Y-axis
#                 pt2 = second_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(width, height, 0.0))  # Top-right corner to the right

#                 # Add rectangle
#                 second_jacket_nozzle_length_cut_rectangle = second_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)
#                 fourth_line_end_pt = second_jacket_nozzle_length_cut_rectangle.Item(3).EndSketchPoint
#                 second_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddHorizontalAlign(fourth_line_end_pt, skpt)
                
#                 mid_x = (fourth_line_end_pt.Geometry.X + skpt.Geometry.X) / 2
#                 mid_y = (fourth_line_end_pt.Geometry.Y + skpt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 second_jacket_nozzle_length_cut_dim_constraints = second_jacket_nozzle_length_cut_sketch.DimensionConstraints
#                 aligned_dim = second_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_end_pt, skpt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '2 mm'
#                 second_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(skpt, jacket_shell_edge_pg)

#                 fourth_line_start_pt = second_jacket_nozzle_length_cut_rectangle.Item(3).StartSketchPoint
#                 mid_x = (fourth_line_start_pt.Geometry.X + fourth_line_end_pt.Geometry.X) / 2
#                 mid_y = (fourth_line_start_pt.Geometry.Y + fourth_line_end_pt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 aligned_dim = second_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_start_pt, fourth_line_end_pt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '150 mm'

#                 second_line_start_pt = second_jacket_nozzle_length_cut_rectangle.Item(2).StartSketchPoint
#                 second_line_end_pt = second_jacket_nozzle_length_cut_rectangle.Item(2).EndSketchPoint
#                 mid_x = (second_line_start_pt.Geometry.X + second_line_end_pt.Geometry.X) / 2
#                 mid_y = (second_line_start_pt.Geometry.Y + second_line_end_pt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)

#                 aligned_dim = second_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(second_line_start_pt, second_line_end_pt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '50 mm'

#                 forth_line = second_jacket_nozzle_length_cut_rectangle.Item(3)
#                 geo_const = second_jacket_nozzle_length_cut_sketch.GeometricConstraints
#                 geo_const.AddCollinear(shell_jacket_nozzle2_y_axis_pg, forth_line, True, True)

#                 second_jacket_nozzle_length_cut_sketch.Solve()
#                 second_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 second_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
#                 second_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 cut_sketch_profile = second_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

#                 part_def = inv_app.ActiveDocument.ComponentDefinition

#                 cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
#                 cut_sketch_revolve_feature = cut_sketch_revolve_feats.AddFull(cut_sketch_profile, shell_jacket_nozzle2_y_axis_pg, 20482)

#                 # Remove participants again
#                 cut_sketch_revolve_feature.RemoveParticipant(inner_shell)
#                 cut_sketch_revolve_feature.RemoveParticipant(glass_9100)


#                 print("Second Jacket Nozzle at Top (Shell) Finish")
#                 # ------------------------------ Second Jacket Nozzle at Top (Shell) Finish ------------------------------------------------------------

#             elif item["component"] == 'jacketnozzle_bottom':
#                 # ------------------------------ Third Jacket Nozzle at Bottom Start ------------------------------------------------------------
#                 print("Third Jacket Nozzle at Bottom Start")
#                 bottom_nozzle1_angle = -90
#                 angle_rad = math.radians(bottom_nozzle1_angle)
#                 origin = tg.CreatePoint(0.0, 0.0, 0.0)
#                 x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
#                 y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

#                 # Add Work Plane: N11_Plane
#                 bottom_nozzle1_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
#                 bottom_nozzle1_angled_plane.Visible = True
#                 bottom_nozzle1_angled_plane.Name = "N11_Plane"
#                 bottom_nozzle1_angled_plane.Grounded = True

#                 bottom_jacket_nozzle3_sketch = main_assy_def.Sketches.Add(main_assy_def.WorkPlanes["XZ Plane"])
#                 originPoint = main_assy_def.WorkPoints["Center Point"]  # Usually the origin work point
#                 projectedCenter = bottom_jacket_nozzle3_sketch.AddByProjectingEntity(originPoint)
#                 originSketchPoint  = bottom_jacket_nozzle3_sketch.SketchPoints.Item(1)
#                 startPt = tg.CreatePoint2d(0, 0)
#                 endPt = tg.CreatePoint2d(37, 0)  # 370 mm in cm (as Inventor usually uses cm internally)

#                 line1 = bottom_jacket_nozzle3_sketch.SketchLines.AddByTwoPoints(startPt, endPt)
#                 line1.Construction = True
#                 horizontal_line1 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddHorizontal(line1)
#                 coincident0 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(line1.StartSketchPoint, projectedCenter)


#                 dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
#                 line_1_dimension = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddTwoPointDistance(line1.StartSketchPoint, line1.EndSketchPoint, 19201, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '370 mm'

#                 endPt2 = tg.CreatePoint2d(0, -37)  # 370 mm along Y
#                 line2 = bottom_jacket_nozzle3_sketch.SketchLines.AddByTwoPoints(startPt, endPt2)
#                 line2.Construction = True

#                 circle_center_point = line2.EndSketchPoint
#                 center2d = circle_center_point.Geometry
#                 circle = bottom_jacket_nozzle3_sketch.SketchCircles.AddByCenterRadius(center2d, 4.6)

#                 dimTextPt2 = tg.CreatePoint2d(-10, 10)  # Text placement
#                 line_2_dimension = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddTwoPointDistance(line2.StartSketchPoint, line2.EndSketchPoint, 19203, dimTextPt2)
#                 line_2_dimension.Parameter.Expression = '370 mm'
#                 # vertical_constraint = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddVertical(line2)

#                 dimTextPoint = tg.CreatePoint2d(circle.CenterSketchPoint.Geometry.X + 50, circle.CenterSketchPoint.Geometry.Y)
#                 # Add diameter dimension (not driven by default, so it drives the size)
#                 diameter_dimension = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddDiameter(circle, dimTextPoint)
#                 # Optionally, set the diameter value explicitly, e.g. 92 mm
#                 diameter_dimension.Parameter.Expression = '92 mm'
                
#                 textPoint = tg.CreatePoint2d(10, -10)  # position of dimension text
#                 angleDim = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddTwoLineAngle(line1, line2, textPoint)
#                 angleDim.Parameter.Expression = "90.0 deg"
                
#                 circle_center = circle.CenterSketchPoint    # The SketchPoint at the center of the circle
#                 line_endpoint = line2.EndSketchPoint

#                 # coincident1 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(line2.StartSketchPoint, projectedCenter)
#                 line2.StartSketchPoint.Merge(projectedCenter)
#                 coincident_circle = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(circle_center, line_endpoint)
                
#                 bottom_jacket_nozzle3_sketch.Solve()
#                 bottom_jacket_nozzle3_sketch.UpdateProfiles()
#                 bottom_jacket_nozzle3_sketch.Profiles.AddForSolid()
#                 bottom_jacket_nozzle3_sketch.UpdateProfiles()

#                 extrude_features  = part_def.Features.ExtrudeFeatures
#                 extrude_def = extrude_features.CreateExtrudeDefinition(bottom_jacket_nozzle3_sketch.Profiles[0], 20482)
#                 extrude_def.SetDistanceExtent(150, 20994)
#                 extrude = extrude_features.Add(extrude_def)

#                 extrude_3_n11 = extrude.Faces.Item(1).Geometry
#                 base_pt_2 = extrude_3_n11.BasePoint
#                 axis_vec_2 = extrude_3_n11.AxisVector
#                 axis_3 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
#                 axis_3.Name = "N11_Axis"
#                 axis_3.Grounded = True

#                 # Add second nozzle component
#                 jacketnozzle_3 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 jacketnozzle_3.Grounded = False

#                 L_occ = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="L_DN150")
#                 xz_plane = L_occ.Definition.WorkPlanes["XZ Plane"]
#                 xz_plane_proxy = L_occ.CreateGeometryProxy(xz_plane)

#                 # Set position
#                 transform_3 = tg.CreateMatrix()
#                 transform_3.SetTranslation(tg.CreateVector(base_pt_2.X, base_pt_2.Y, base_pt_2.Z))
#                 jacketnozzle_3.Transformation = transform_3

#                 # Get proxies
#                 y_axis_3 = jacketnozzle_3.CreateGeometryProxy(jacketnozzle_3.Definition.WorkAxes["Y Axis"])
#                 xy_plane_3 = jacketnozzle_3.CreateGeometryProxy(jacketnozzle_3.Definition.WorkPlanes["XY Plane"])
#                 xz_plane_3 = jacketnozzle_3.CreateGeometryProxy(jacketnozzle_3.Definition.WorkPlanes["XZ Plane"])
#                 # xy_plane_main = main_assy_def.WorkPlanes['XY Plane']

#                 # Add constraints
#                 flush_3 = main_assy_def.Constraints.AddFlushConstraint(bottom_nozzle1_angled_plane, xy_plane_3, 0, None, None)
#                 mate_y_3 = main_assy_def.Constraints.AddMateConstraint2(axis_3, y_axis_3, 0, 24833, 24833, 115459, None, None)
#                 mate_xz_3 = main_assy_def.Constraints.AddMateConstraint2(xz_plane_3, xz_plane_proxy, "90 mm", 24833, 24833, 115460, None, None)

#                 # Start cut revolve operation on first jacket nozzle:

#                 # xz_plane_nozzle_3 = jacketnozzle_3.Definition.WorkPlanes["XY Plane"]
#                 # bottom_nozzle1_angled_plane_proxy = jacketnozzle_3.CreateGeometryProxy(bottom_nozzle1_angled_plane)
#                 third_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(bottom_nozzle1_angled_plane)
                
#                 bottom_jacket_nozzle3_y_axis = jacketnozzle_3.Definition.WorkAxes["Y Axis"]
#                 bottom_jacket_nozzle3_y_axis_proxy = jacketnozzle_3.CreateGeometryProxy(bottom_jacket_nozzle3_y_axis)
#                 bottom_jacket_nozzle3_y_axis_pg = third_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_jacket_nozzle3_y_axis_proxy)
#                 bottom_jacket_nozzle3_y_axis_pg.CenterLine = True
                
#                 bottom_swg_dish = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="BTM-1950")
#                 bottom_swg_dish_center_point = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkPoints["Center Point"])
#                 bottom_swg_dish_center_proj = third_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_center_point)

#                 bottom_swg_dish_y_axis = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkAxes["Y Axis"])
                

#                 bottom_swg_dish_y_axis_proj = third_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_y_axis)
#                 bottom_swg_dish_y_axis_proj_start_pt = bottom_swg_dish_y_axis_proj.StartSketchPoint
#                 # bottom_swg_dish_y_axis_proj.CenterLine = True

#                 # Draw Circle
#                 # center2d_point = tg.CreatePoint2d(0, 0)
#                 textPoint = tg.CreatePoint2d(10, 10)
#                 third_jacket_nozzle_circle = third_jacket_nozzle_length_cut_sketch.SketchCircles.AddByCenterRadius(bottom_swg_dish_y_axis_proj_start_pt.Geometry, 202.0)
#                 dim = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddRadius(third_jacket_nozzle_circle, textPoint)
#                 dim.Parameter.Expression = '2020 mm'
#                 third_jacket_nozzle_circle.Construction = True
                
#                 third_jacket_nozzle_circle_center_pt = third_jacket_nozzle_circle.CenterSketchPoint

#                 third_jacket_nozzle_circle_coincidence_2 = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_y_axis_proj, third_jacket_nozzle_circle_center_pt)
#                 third_jacket_nozzle_circle_coincidence_1 = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_center_proj, third_jacket_nozzle_circle)
                

#                 rect1_width = 10.0
#                 rect1_height = 5.0
#                 center_x = bottom_swg_dish_center_proj.Geometry.X
#                 center_y = bottom_swg_dish_center_proj.Geometry.Y

#                 rect1_bottom_left_pt = tg.CreatePoint2d(center_x - rect1_width / 2, center_y)
#                 rect1_top_right_pt = tg.CreatePoint2d(center_x + rect1_width / 2, center_y + rect1_height)
#                 # Create 2D corner points in sketch space
#                 # rect1_bottom_left_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_bottom_left_pt)  # Bottom-left
#                 # rect1_top_right_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_top_right_pt)  # Top-right

#                 # Add rectangle
#                 rect1_lines = third_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(rect1_bottom_left_pt, rect1_top_right_pt)

#                 fourth_line_of_rect1 = rect1_lines.Item(4)
#                 collinear1 = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCollinear(bottom_jacket_nozzle3_y_axis_pg, fourth_line_of_rect1)

#                 second_line_of_rect1 = rect1_lines.Item(2)

#                 first_line_of_rect1 = rect1_lines.Item(1)
#                 dimTextPt1 = tg.CreatePoint2d(-10, 10)  # Text placement
#                 line_1_dimension = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(first_line_of_rect1.StartSketchPoint, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '50 mm'

                
#                 dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
#                 line_1_dimension = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(second_line_of_rect1.StartSketchPoint, second_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '150 mm'

#                 new_pt = tg.CreatePoint2d(10, -10)
#                 new_sketch_pt = third_jacket_nozzle_length_cut_sketch.SketchPoints.Add(new_pt, False)
#                 coincidence1_new_pt = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, third_jacket_nozzle_circle)

#                 dimTextPt1 = tg.CreatePoint2d(10, 10)  # Text placement
#                 line_1_dimension = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(new_sketch_pt, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '9 mm'

#                 coincidence1_new_pt = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, second_line_of_rect1)

#                 third_jacket_nozzle_length_cut_sketch.Solve()
#                 third_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 third_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
#                 third_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 third_cut_sketch_profile = third_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

#                 part_def = inv_app.ActiveDocument.ComponentDefinition

#                 third_cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
#                 third_cut_sketch_revolve_feature = third_cut_sketch_revolve_feats.AddFull(third_cut_sketch_profile, bottom_jacket_nozzle3_y_axis_pg, 20482)

#                 # Remove participants again
#                 third_cut_sketch_revolve_feature.RemoveParticipant(bottom_swg_dish)
#                 third_cut_sketch_revolve_feature.RemoveParticipant(glass_9100)



#                 print("Third Jacket Nozzle at Bottom End")
#                 # ------------------------------ Third Jacket Nozzle at Bottom End ------------------------------------------------------------

#                 # ------------------------------ Forth Jacket Nozzle at Bottom Start ------------------------------------------------------------
#                 print("Forth Jacket Nozzle at Bottom Start")

#                 bottom_nozzle2_angle = -270
#                 angle_rad = math.radians(bottom_nozzle2_angle)
#                 origin = tg.CreatePoint(0.0, 0.0, 0.0)
#                 x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
#                 y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

#                 # Add Work Plane: N17_Plane
#                 bottom_nozzle2_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
#                 bottom_nozzle2_angled_plane.Visible = True
#                 bottom_nozzle2_angled_plane.Name = "N17_Plane"
#                 bottom_nozzle2_angled_plane.Grounded = True

#                 bottom_jacket_nozzle4_sketch = main_assy_def.Sketches.Add(main_assy_def.WorkPlanes["XZ Plane"])
#                 originPoint = main_assy_def.WorkPoints["Center Point"]  # Usually the origin work point
#                 projectedCenter = bottom_jacket_nozzle4_sketch.AddByProjectingEntity(originPoint)
#                 originSketchPoint  = bottom_jacket_nozzle4_sketch.SketchPoints.Item(1)
#                 startPt = tg.CreatePoint2d(0, 0)
#                 endPt = tg.CreatePoint2d(37, 0)  # 370 mm in cm (as Inventor usually uses cm internally)

#                 line1 = bottom_jacket_nozzle4_sketch.SketchLines.AddByTwoPoints(startPt, endPt)
#                 line1.Construction = True
#                 horizontal_line1 = bottom_jacket_nozzle4_sketch.GeometricConstraints.AddHorizontal(line1)
#                 coincident0 = bottom_jacket_nozzle4_sketch.GeometricConstraints.AddCoincident(line1.StartSketchPoint, projectedCenter)


#                 dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
#                 line_1_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddTwoPointDistance(line1.StartSketchPoint, line1.EndSketchPoint, 19201, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '370 mm'

#                 endPt2 = tg.CreatePoint2d(0, 37)  # 370 mm along Y
#                 line2 = bottom_jacket_nozzle4_sketch.SketchLines.AddByTwoPoints(startPt, endPt2)
#                 line2.Construction = True

#                 circle_center_point = line2.EndSketchPoint
#                 center2d = circle_center_point.Geometry
#                 circle = bottom_jacket_nozzle4_sketch.SketchCircles.AddByCenterRadius(center2d, 4.6)

#                 dimTextPt2 = tg.CreatePoint2d(-10, 10)  # Text placement
#                 line_2_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddTwoPointDistance(line2.StartSketchPoint, line2.EndSketchPoint, 19203, dimTextPt2)
#                 line_2_dimension.Parameter.Expression = '370 mm'
#                 # vertical_constraint = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddVertical(line2)

#                 dimTextPoint = tg.CreatePoint2d(circle.CenterSketchPoint.Geometry.X + 50, circle.CenterSketchPoint.Geometry.Y)
#                 # Add diameter dimension (not driven by default, so it drives the size)
#                 diameter_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddDiameter(circle, dimTextPoint)
#                 # Optionally, set the diameter value explicitly, e.g. 92 mm
#                 diameter_dimension.Parameter.Expression = '92 mm'
                
#                 textPoint = tg.CreatePoint2d(10, 10)  # position of dimension text
#                 angleDim = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddTwoLineAngle(line1, line2, textPoint)
#                 angleDim.Parameter.Expression = "90.0 deg"
                
#                 circle_center = circle.CenterSketchPoint    # The SketchPoint at the center of the circle
#                 line_endpoint = line2.EndSketchPoint

#                 # coincident1 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(line2.StartSketchPoint, projectedCenter)
#                 line2.StartSketchPoint.Merge(projectedCenter)
#                 coincident_circle = bottom_jacket_nozzle4_sketch.GeometricConstraints.AddCoincident(circle_center, line_endpoint)
                
                

#                 bottom_jacket_nozzle4_sketch.Solve()
#                 bottom_jacket_nozzle4_sketch.UpdateProfiles()
#                 bottom_jacket_nozzle4_sketch.Profiles.AddForSolid()
#                 bottom_jacket_nozzle4_sketch.UpdateProfiles()

#                 extrude_features  = part_def.Features.ExtrudeFeatures
#                 extrude_def = extrude_features.CreateExtrudeDefinition(bottom_jacket_nozzle4_sketch.Profiles[0], 20482)
#                 extrude_def.SetDistanceExtent(150, 20994)
#                 extrude = extrude_features.Add(extrude_def)

#                 extrude_4_n17 = extrude.Faces.Item(1).Geometry
#                 base_pt_2 = extrude_4_n17.BasePoint
#                 axis_vec_2 = extrude_4_n17.AxisVector
#                 axis_4 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
#                 axis_4.Name = "N17_Axis"
#                 axis_4.Grounded = True

#                 # Add second nozzle component
#                 jacketnozzle_4 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 jacketnozzle_4.Grounded = False

#                 L_occ = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="L_DN150")
#                 xz_plane = L_occ.Definition.WorkPlanes["XZ Plane"]
#                 xz_plane_proxy = L_occ.CreateGeometryProxy(xz_plane)

#                 # Set position
#                 transform_4 = tg.CreateMatrix()
#                 transform_4.SetTranslation(tg.CreateVector(base_pt_2.X, base_pt_2.Y, base_pt_2.Z))
#                 jacketnozzle_4.Transformation = transform_4

#                 # Get proxies
#                 y_axis_4 = jacketnozzle_4.CreateGeometryProxy(jacketnozzle_4.Definition.WorkAxes["Y Axis"])
#                 xy_plane_4 = jacketnozzle_4.CreateGeometryProxy(jacketnozzle_4.Definition.WorkPlanes["XY Plane"])
#                 xz_plane_4 = jacketnozzle_4.CreateGeometryProxy(jacketnozzle_4.Definition.WorkPlanes["XZ Plane"])
#                 # xy_plane_main = main_assy_def.WorkPlanes['XY Plane']

#                 # Add constraints
#                 flush_4 = main_assy_def.Constraints.AddFlushConstraint(bottom_nozzle2_angled_plane, xy_plane_4, 0, None, None)
#                 mate_y_4 = main_assy_def.Constraints.AddMateConstraint2(axis_4, y_axis_4, 0, 24833, 24833, 115459, None, None)
#                 mate_xz_4 = main_assy_def.Constraints.AddMateConstraint2(xz_plane_4, xz_plane_proxy, "90 mm", 24833, 24833, 115460, None, None)

#                 # Start cut revolve operation on first jacket nozzle:

#                 # xz_plane_nozzle_3 = jacketnozzle_3.Definition.WorkPlanes["XY Plane"]
#                 # bottom_nozzle1_angled_plane_proxy = jacketnozzle_3.CreateGeometryProxy(bottom_nozzle1_angled_plane)
#                 fourth_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(bottom_nozzle2_angled_plane)
                
#                 bottom_jacket_nozzle4_y_axis = jacketnozzle_4.Definition.WorkAxes["Y Axis"]
#                 bottom_jacket_nozzle4_y_axis_proxy = jacketnozzle_4.CreateGeometryProxy(bottom_jacket_nozzle4_y_axis)
#                 bottom_jacket_nozzle4_y_axis_pg = fourth_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_jacket_nozzle4_y_axis_proxy)
#                 bottom_jacket_nozzle4_y_axis_pg.CenterLine = True
                
#                 bottom_swg_dish = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="BTM-1950")
#                 bottom_swg_dish_center_point = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkPoints["Center Point"])
#                 bottom_swg_dish_center_proj = fourth_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_center_point)

#                 bottom_swg_dish_y_axis = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkAxes["Y Axis"])
                

#                 bottom_swg_dish_y_axis_proj = fourth_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_y_axis)
#                 bottom_swg_dish_y_axis_proj_start_pt = bottom_swg_dish_y_axis_proj.StartSketchPoint
#                 # bottom_swg_dish_y_axis_proj.CenterLine = True

#                 # Draw Circle
#                 # center2d_point = tg.CreatePoint2d(0, 0)
#                 textPoint = tg.CreatePoint2d(10, 10)
#                 fourth_jacket_nozzle_circle = fourth_jacket_nozzle_length_cut_sketch.SketchCircles.AddByCenterRadius(bottom_swg_dish_y_axis_proj_start_pt.Geometry, 202.0)
#                 dim = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddRadius(fourth_jacket_nozzle_circle, textPoint)
#                 dim.Parameter.Expression = '2020 mm'
#                 fourth_jacket_nozzle_circle.Construction = True
                
#                 fourth_jacket_nozzle_circle_center_pt = fourth_jacket_nozzle_circle.CenterSketchPoint

#                 fourth_jacket_nozzle_circle_coincidence_2 = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_y_axis_proj, fourth_jacket_nozzle_circle_center_pt)
#                 fourth_jacket_nozzle_circle_coincidence_1 = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_center_proj, fourth_jacket_nozzle_circle)
                

#                 rect1_width = 10.0
#                 rect1_height = 5.0
#                 center_x = bottom_swg_dish_center_proj.Geometry.X
#                 center_y = bottom_swg_dish_center_proj.Geometry.Y

#                 rect1_bottom_left_pt = tg.CreatePoint2d(center_x - rect1_width / 2, center_y)
#                 rect1_top_right_pt = tg.CreatePoint2d(center_x + rect1_width / 2, center_y + rect1_height)
#                 # Create 2D corner points in sketch space
#                 # rect1_bottom_left_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_bottom_left_pt)  # Bottom-left
#                 # rect1_top_right_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_top_right_pt)  # Top-right

#                 # Add rectangle
#                 rect1_lines = fourth_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(rect1_bottom_left_pt, rect1_top_right_pt)

#                 fourth_line_of_rect1 = rect1_lines.Item(4)
#                 collinear1 = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCollinear(bottom_jacket_nozzle4_y_axis_pg, fourth_line_of_rect1)

#                 second_line_of_rect1 = rect1_lines.Item(2)

#                 first_line_of_rect1 = rect1_lines.Item(1)
#                 dimTextPt1 = tg.CreatePoint2d(-10, 10)  # Text placement
#                 line_1_dimension = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(first_line_of_rect1.StartSketchPoint, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '50 mm'

                
#                 dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
#                 line_1_dimension = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(second_line_of_rect1.StartSketchPoint, second_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '150 mm'

#                 new_pt = tg.CreatePoint2d(10, -10)
#                 new_sketch_pt = fourth_jacket_nozzle_length_cut_sketch.SketchPoints.Add(new_pt, False)
#                 coincidence1_new_pt = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, fourth_jacket_nozzle_circle)

#                 dimTextPt1 = tg.CreatePoint2d(10, 10)  # Text placement
#                 line_1_dimension = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(new_sketch_pt, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '9 mm'

#                 coincidence1_new_pt = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, second_line_of_rect1)

#                 fourth_jacket_nozzle_length_cut_sketch.Solve()
#                 fourth_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 fourth_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
#                 fourth_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 fourth_cut_sketch_profile = fourth_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

#                 part_def = inv_app.ActiveDocument.ComponentDefinition

#                 fourth_cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
#                 fourth_cut_sketch_revolve_feature = fourth_cut_sketch_revolve_feats.AddFull(fourth_cut_sketch_profile, bottom_jacket_nozzle4_y_axis_pg, 20482)

#                 # Remove participants again
#                 fourth_cut_sketch_revolve_feature.RemoveParticipant(bottom_swg_dish)
#                 fourth_cut_sketch_revolve_feature.RemoveParticipant(glass_9100)

#                 print("Forth Jacket Nozzle at Bottom End")




# import math
# import win32com.client
# import win32gui
# import time
# import os
# from services.inventor_helper_service import FirstJacketNozzleBuilder


# class Inventor:
#     def __init__(self):
#         pass

#     def open(self, files):
#         part_path = files[0]
#         if not os.path.isfile(part_path):
#             raise FileNotFoundError(f"File not found: {part_path}")
        
#         invApp = win32com.client.Dispatch("Inventor.Application")
#         invApp.Visible = True

#         part_doc = invApp.Documents.Open(part_path)
#         print("Opened:", part_doc.DisplayName)
#         time.sleep(1)

#         window_title = invApp.Caption
#         hwnd = win32gui.FindWindow(None, window_title)

#         if hwnd:
#             win32gui.ShowWindow(hwnd, 5)  # SW_SHOW
#             win32gui.SetForegroundWindow(hwnd)
#             print("Inventor window brought to the front.")
#             return True
#         else:
#             print("Could not find the Inventor window.")
#             return False
        
#     def generate(self, components):
#         # Start Inventor
#         inv_app = win32com.client.Dispatch("Inventor.Application")
#         inv_app.Visible = True

#         # Get TransientGeometry
#         tg = inv_app.TransientGeometry

#         # Create a new Assembly document: Main Assembly
#         main_assy_doc = inv_app.Documents.Add("12291", inv_app.FileManager.GetTemplateFile("12291", "8963"), True)
#         main_assy_def = main_assy_doc.ComponentDefinition
#         monoblock = jacket = diapharm = sidebracket = jacketnozzle = None

#         for idx, item in enumerate(components):
#             if item["component"] == 'monoblock':
#                 monoblock = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 monoblock.Grounded = False

#                 # Main Assembly Work Axes and Work Planes
#                 main_y_axis = main_assy_def.WorkAxes["Y Axis"]
#                 main_xy_plane = main_assy_def.WorkPlanes["XY Plane"]
#                 main_xz_plane = main_assy_def.WorkPlanes["XZ Plane"]

#                 # Monoblock Work Axes and Work Planes
#                 monoblock_y_axis = monoblock.CreateGeometryProxy(monoblock.Definition.WorkAxes["Y Axis"]) # This is important !!
#                 monoblock_xy_plane = monoblock.CreateGeometryProxy(monoblock.Definition.WorkPlanes["XY Plane"])
#                 monoblock_xz_plane = monoblock.CreateGeometryProxy(monoblock.Definition.WorkPlanes["XZ Plane"])
                
#                 # Constraints for Monoblock        
#                 monoblock_mate_y = main_assy_def.Constraints.AddMateConstraint2(main_y_axis, monoblock_y_axis, 0, 24833, 24833, 115459, None, None)
#                 monoblock_flush_xy = main_assy_def.Constraints.AddFlushConstraint(main_xy_plane, monoblock_xy_plane, 0, None, None)
#                 monoblock_flush_xz = main_assy_def.Constraints.AddFlushConstraint(main_xz_plane, monoblock_xz_plane, 0, None, None)
            
#             elif item["component"] == 'jacket':
#                 print("Start jacket")
#                 jacket = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 jacket.Grounded = False

#                 # Monoblock Work Axes and Work Planes
#                 monoblock_y_axis = monoblock.CreateGeometryProxy(monoblock.Definition.WorkAxes["Y Axis"]) # This is important !!
#                 monoblock_xy_plane = monoblock.CreateGeometryProxy(monoblock.Definition.WorkPlanes["XY Plane"])
#                 monoblock_xz_plane = monoblock.CreateGeometryProxy(monoblock.Definition.WorkPlanes["XZ Plane"])

#                 # Jacket Work Axes and Work Planes
#                 jacket_y_axis = jacket.CreateGeometryProxy(jacket.Definition.WorkAxes["Y Axis"])
#                 jacket_xy_plane = jacket.CreateGeometryProxy(jacket.Definition.WorkPlanes["XY Plane"])
#                 jacket_xz_plane = jacket.CreateGeometryProxy(jacket.Definition.WorkPlanes["XZ Plane"])
                
#                 # Constraints for Jacket        
#                 jacket_mate_y = main_assy_def.Constraints.AddMateConstraint2(monoblock_y_axis, jacket_y_axis, 0, 24833, 24833, 115459, None, None)
#                 jacket_flush_xy = main_assy_def.Constraints.AddFlushConstraint(monoblock_xy_plane, jacket_xy_plane, 0, None, None)
#                 jacket_flush_xz = main_assy_def.Constraints.AddFlushConstraint(jacket_xz_plane, monoblock_xz_plane, "57 mm", None, None)

#                 print("End jacket")
            
#             elif item["component"] == 'diapharmring':
#                 print("Start diapharmring")
#                 diapharm = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 diapharm.Grounded = False

#                 btm_jcr = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="BTM JSR")

#                 # Bottom JSR Work Axes and Work Planes
#                 btm_jcr_y_axis = btm_jcr.CreateGeometryProxy(btm_jcr.Definition.WorkAxes["Y Axis"])
#                 btm_jcr_xy_plane = btm_jcr.CreateGeometryProxy(btm_jcr.Definition.WorkPlanes["XY Plane"])
#                 btm_jcr_xz_plane = btm_jcr.CreateGeometryProxy(btm_jcr.Definition.WorkPlanes["XZ Plane"])
                
#                 # Diapharm Ring Work Axes and Work Planes
#                 diapharm_y_axis = diapharm.CreateGeometryProxy(diapharm.Definition.WorkAxes["Y Axis"])
#                 diapharm_xy_plane = diapharm.CreateGeometryProxy(diapharm.Definition.WorkPlanes["XY Plane"])
#                 diapharm_xz_plane = diapharm.CreateGeometryProxy(diapharm.Definition.WorkPlanes["XZ Plane"])
                
#                 # Constraints for Diapharm Ring
#                 diapharm_mate_y = main_assy_def.Constraints.AddMateConstraint2(btm_jcr_y_axis, diapharm_y_axis, 0, 24833, 24833, 115459, None, None)
#                 diapharm_flush_xy = main_assy_def.Constraints.AddFlushConstraint(btm_jcr_xy_plane, diapharm_xy_plane, 0, None, None)
#                 diapharm_flush_xz = main_assy_def.Constraints.AddFlushConstraint(diapharm_xz_plane, btm_jcr_xz_plane, "40 mm", None, None)     

#                 print("End diapharmring")

#             elif item["component"] == 'sidebracket':
#                 print("Start sidebracket")
#                 sidebracket = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 sidebracket.Grounded = False

#                 # Jacket Work Axes and Work Planes
#                 jacket_y_axis = jacket.CreateGeometryProxy(jacket.Definition.WorkAxes["Y Axis"])
#                 jacket_xy_plane = jacket.CreateGeometryProxy(jacket.Definition.WorkPlanes["XY Plane"])

#                 initial = main_assy_def.Occurrences[0]
#                 ref_occ = initial.Definition.Occurrences[0]  # Inside monoblock
#                 # Get "REF LINE" from the ref_occ (this is still in its own context)
#                 ref_workplane_local = ref_occ.Definition.WorkPlanes["REF LINE"]
#                 # Step 2: Promote to monoblock-level assembly context
#                 ref_plane_proxy_lvl1 = ref_occ.CreateGeometryProxy(ref_workplane_local)
#                 # Step 3: Promote to main assembly context
#                 ref_plane_proxy_top = initial.CreateGeometryProxy(ref_plane_proxy_lvl1)


#                 # Side Bracket Work Axes and Work Planes
#                 sidebracket_y_axis = sidebracket.CreateGeometryProxy(sidebracket.Definition.WorkAxes["Y Axis"])
#                 sidebracket_xy_plane = sidebracket.CreateGeometryProxy(sidebracket.Definition.WorkPlanes["XY Plane"])
#                 sidebracket_xz_plane = sidebracket.CreateGeometryProxy(sidebracket.Definition.WorkPlanes["XZ Plane"])

#                 # Constraints for Side Bracket
#                 sidebracket_mate_y = main_assy_def.Constraints.AddMateConstraint2(jacket_y_axis, sidebracket_y_axis, 0, 24833, 24833, 115459, None, None)
#                 # sidebracket_flush_xy = main_assy_def.Constraints.AddFlushConstraint(jacket_xy_plane, sidebracket_xy_plane, 0, None, None)
#                 sidebracket_angle_xy = main_assy_def.Constraints.AddAngleConstraint(jacket_xy_plane, sidebracket_xy_plane, 0, 78593, None, None, None)
#                 sidebracket_flush_xz = main_assy_def.Constraints.AddFlushConstraint(sidebracket_xz_plane, ref_plane_proxy_top, "535 mm", None, None)

#                 # Adding 4 side bracket at 90.0 degree with corresponds to Y-axis
#                 transient_objs = inv_app.TransientObjects
#                 object_collection = transient_objs.CreateObjectCollection()
#                 object_collection.Add(sidebracket)
#                 pattern_axis = monoblock.CreateGeometryProxy(monoblock.Definition.WorkAxes["Y Axis"])
#                 main_assy_def.OccurrencePatterns.AddCircularPattern(object_collection, pattern_axis, True, "90 deg", 4)
                
#                 print("End sidebracket")

#             elif item["component"] == 'jacketnozzle_shell':
#                 # builder = FirstJacketNozzleBuilder(inv_app, tg, main_assy_def, monoblock, item)
#                 # builder.build_first_jacket_nozzle()
#                 # # ---------------------------------------------------- First Jacket Nozzle at Top (Shell) Start ------------------------------------------
#                 # Set rotation angle - New Plane
#                 print("First Jacket Nozzle at Top (Shell) Start")
#                 shell_nozzle1_angle = -28
#                 angle_rad = math.radians(shell_nozzle1_angle)
#                 origin = tg.CreatePoint(0.0, 0.0, 0.0)
#                 x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
#                 y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

#                 # Add Work Plane: N16_Plane
#                 shell_nozzle1_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
#                 shell_nozzle1_angled_plane.Visible = True
#                 shell_nozzle1_angled_plane.Name = "N16_Plane"
#                 shell_nozzle1_angled_plane.Grounded = True

#                 # Add Sketch
#                 shell_jacket_nozzle1_sketch = main_assy_def.Sketches.Add(shell_nozzle1_angled_plane)

#                 # Add Y-axis project geometry
#                 main_y_axis = main_assy_def.WorkAxes["Y Axis"]
#                 yaxis_pg = shell_jacket_nozzle1_sketch.AddByProjectingEntity(main_y_axis)

#                 L_nozzle_occ = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="L_DN150")

#                 width = 10.0
#                 height = 5.0
#                 # Create 2D corner points in sketch space
#                 bottom_left_pt = shell_jacket_nozzle1_sketch.ModelToSketchSpace(tg.CreatePoint(-width/2, 0, 0))  # Bottom-left
#                 top_right_pt = shell_jacket_nozzle1_sketch.ModelToSketchSpace(tg.CreatePoint(width/2, height, 0))  # Top-right

#                 # Add rectangle
#                 rect_lines = shell_jacket_nozzle1_sketch.SketchLines.AddAsTwoPointRectangle(bottom_left_pt, top_right_pt)

#                 # Get bottom line (first item)
#                 bottom_line = rect_lines.Item(1)
#                 bottom_line.Centerline = True
                                
#                 # Get the XZ plane of L_nozzle_occ
#                 L_nozzle_xz_plane = L_nozzle_occ.Definition.WorkPlanes["XZ Plane"]
#                 L_nozzle_xz_plane_proxy = L_nozzle_occ.CreateGeometryProxy(L_nozzle_xz_plane)

#                 # Project XZ plane into the sketch
#                 proj_line = shell_jacket_nozzle1_sketch.AddByProjectingEntity(L_nozzle_xz_plane_proxy)

#                 # Ensure the projected line is valid
#                 if not hasattr(proj_line, "StartSketchPoint"):
#                     raise Exception("Projected XZ plane did not return a SketchLine.")

#                 # Get points from bottom line and projected line
#                 bottom_line_start_pt1 = bottom_line.StartSketchPoint
#                 project_line_start_pt2 = proj_line.StartSketchPoint

#                 # Validate points
#                 if bottom_line_start_pt1 is None or project_line_start_pt2 is None:
#                     raise Exception("One or both SketchPoints are None.")

#                 # Create a text point for dimension label (optional but required by API)
#                 # Use midpoint between pt1 and pt2 as a reasonable label position
#                 mid_x = (bottom_line_start_pt1.Geometry.X + project_line_start_pt2.Geometry.X) / 2
#                 mid_y = (bottom_line_start_pt1.Geometry.Y + project_line_start_pt2.Geometry.Y) / 2
#                 text_point = inv_app.TransientGeometry.CreatePoint2d(mid_x, mid_y)

#                 # Add vertical dimension constraint
#                 dim_constraints = shell_jacket_nozzle1_sketch.DimensionConstraints
#                 dimension = dim_constraints.AddTwoPointDistance(bottom_line_start_pt1, project_line_start_pt2, 19202, text_point, False)

#                 # Set the distance value (assuming mm)
#                 dimension.Parameter.Expression = '2350 mm'

#                 second_line = rect_lines.Item(2)  

#                 # Add collinear constraint
#                 geo_constraints = shell_jacket_nozzle1_sketch.GeometricConstraints
#                 geo_constraints.AddCollinear(yaxis_pg, second_line)

#                 # Get second and fourth lines of the rectangle
#                 fourth_line = rect_lines.Item(4)  # Likely the right vertical edge

#                 # Get sketch points from each line
#                 second_line_start_pt1 = second_line.StartSketchPoint
#                 fourth_line_start_pt2 = fourth_line.StartSketchPoint

#                 # Validate points
#                 if second_line_start_pt1 is None or fourth_line_start_pt2 is None:
#                     raise Exception("One or both sketch points are None.")

#                 # Compute midpoint for dimension text placement
#                 mid_x = (second_line_start_pt1.Geometry.X + fourth_line_start_pt2.Geometry.X) / 2
#                 mid_y = (second_line_start_pt1.Geometry.Y + fourth_line_start_pt2.Geometry.Y) / 2
#                 text_point = inv_app.TransientGeometry.CreatePoint2d(mid_x, mid_y)

#                 # Add horizontal dimension constraint
#                 dim_constraints = shell_jacket_nozzle1_sketch.DimensionConstraints
#                 horizontal_dim = dim_constraints.AddTwoPointDistance(second_line_start_pt1, fourth_line_start_pt2, 19203, text_point, False)

#                 # Set the dimension to the actual rectangle width (10.0 mm)
#                 horizontal_dim.Parameter.Expression = "5000 mm"

#                 # Get first and third lines of the rectangle
#                 first_line = rect_lines.Item(1)   # Bottom edge
#                 third_line = rect_lines.Item(3)   # Top edge

#                 # Get sketch points (use start point for consistency)
#                 first_line_start_pt1 = first_line.StartSketchPoint
#                 third_line_start_pt2 = third_line.StartSketchPoint

#                 # Validate points
#                 if first_line_start_pt1 is None or third_line_start_pt2 is None:
#                     raise Exception("One or both sketch points are None.")

#                 # Compute midpoint for dimension text
#                 mid_x = (first_line_start_pt1.Geometry.X + third_line_start_pt2.Geometry.X) / 2
#                 mid_y = (first_line_start_pt1.Geometry.Y + third_line_start_pt2.Geometry.Y) / 2
#                 text_point = inv_app.TransientGeometry.CreatePoint2d(mid_x, mid_y)

#                 # Add vertical dimension
#                 vertical_dim = shell_jacket_nozzle1_sketch.DimensionConstraints.AddTwoPointDistance(first_line_start_pt1, third_line_start_pt2, 19202, text_point, False)

#                 # Set the value (height of the rectangle)
#                 vertical_dim.Parameter.Expression = "45 mm"

#                 # Solve the sketch: Needs to update profile after adding for solid.
#                 shell_jacket_nozzle1_sketch.Solve()
#                 shell_jacket_nozzle1_sketch.UpdateProfiles()
#                 shell_jacket_nozzle1_sketch.Profiles.AddForSolid()
#                 shell_jacket_nozzle1_sketch.UpdateProfiles()

#                 # === Step 1: Get the profile from the sketch ===
#                 profile = shell_jacket_nozzle1_sketch.Profiles.Item(1)  # Assumes rectangle forms a closed profile

#                 # === Step 2: Get the axis (centerline) ===
#                 axis_line = bottom_line  # Bottom line marked as Centerline earlier

#                 # === Step 3: Access the part definition (not assembly) ===
#                 # This must be run inside a part document, not an assembly
#                 # For example, if you're in jacketnozzle component part:
#                 part_def = inv_app.ActiveDocument.ComponentDefinition  # Must be a PartDocument

#                 # === Step 4: Revolve the sketch using AddFull ===
#                 revolve_features = part_def.Features.RevolveFeatures
#                 revolve_feature = revolve_features.AddFull(profile, axis_line, 20482)

#                 # Remove participants - components or occurrences
#                 # 1) Remove Inner shell
#                 inner_shell = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="INNER SHELL")
#                 revolve_feature.RemoveParticipant(inner_shell)
#                 # 2) Remove 9100 glass 
#                 glass_9100 = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="9100")
#                 revolve_feature.RemoveParticipant(glass_9100)

#                 # Adding Axis
#                 cylinder = revolve_feature.Faces.Item(1).Geometry  # Should be a cylinder
#                 base_pt = cylinder.BasePoint
#                 axis_vec = cylinder.AxisVector
#                 work_axis = main_assy_def.WorkAxes.AddFixed(base_pt, axis_vec, False)
#                 work_axis.Name = "N16_Axis"
#                 work_axis.Grounded = True

#                 shell_jacket_nozzle1 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 shell_jacket_nozzle1.Grounded = False

#                 # Create a transform matrix (identity to start)
#                 transform = tg.CreateMatrix()
#                 translation_vector = tg.CreateVector(base_pt.X, base_pt.Y, base_pt.Z)
#                 transform.SetTranslation(translation_vector)
#                 shell_jacket_nozzle1.Transformation = transform

#                 # Attach Jacket Nozzle with Jacket
#                 shell_jacket_nozzle1_y_axis = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkAxes["Y Axis"])
#                 shell_jacket_nozzle1_xy_plane = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkPlanes["XY Plane"])
#                 shell_jacket_jacket_nozzle1_xz_plane = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1.Definition.WorkPlanes["XZ Plane"])

#                 main_N16_Plane = main_assy_def.WorkPlanes['N16_Plane']
#                 main_N16_Axis = main_assy_def.WorkAxes["N16_Axis"]
#                 jacket_shell = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="10Tx2100x")
#                 jacket_shell_face = jacket_shell.Definition.SurfaceBodies[0].Faces[0]
#                 shell_face_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_face)

#                 # Adding Constraints

#                 jacket_nozzle_flush = main_assy_def.Constraints.AddFlushConstraint(main_N16_Plane, shell_jacket_nozzle1_xy_plane, 0, None, None)
#                 jacket_nozzle_mate_y = main_assy_def.Constraints.AddMateConstraint2(main_N16_Axis, shell_jacket_nozzle1_y_axis, 0, 24833, 24833, 115459, None, None)
#                 jacket_nozzle_tangent = main_assy_def.Constraints.AddTangentConstraint(shell_jacket_jacket_nozzle1_xz_plane, shell_face_proxy, False, "140 mm")


#                 # Start cut operation on first jacket nozzle:
#                 yz_plane = shell_jacket_nozzle1.Definition.WorkPlanes["YZ Plane"]
#                 yz_plane_proxy = shell_jacket_nozzle1.CreateGeometryProxy(yz_plane)
#                 first_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(yz_plane_proxy)

#                 jacket_shell_edge = jacket_shell.Definition.SurfaceBodies[0].Edges.Item(7) # 
#                 jacket_shell_edge_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_edge)
#                 jacket_shell_edge_pg = first_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(jacket_shell_edge_proxy)

#                 shell_jacket_nozzle1_y_axis = shell_jacket_nozzle1.Definition.WorkAxes["Y Axis"]
#                 shell_jacket_nozzle1_y_axis_proxy = shell_jacket_nozzle1.CreateGeometryProxy(shell_jacket_nozzle1_y_axis)
#                 shell_jacket_nozzle1_y_axis_pg = first_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(shell_jacket_nozzle1_y_axis_proxy)
#                 shell_jacket_nozzle1_y_axis_pg.CenterLine = True

#                 # # 8. Create 2D point at that location
#                 pt2d = tg.CreatePoint2d(0.0, 0.0)

#                 # 9. Add the sketch point
#                 skpt = first_jacket_nozzle_length_cut_sketch.SketchPoints.Add(pt2d, False)

#                 width = 5.0
#                 height = 15.0

#                 # Place rectangle starting at Y-axis (X = 0), going right
#                 pt1 = first_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(0.0, 0.0, 0.0))  # Bottom-left corner on Y-axis
#                 pt2 = first_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(width, height, 0.0))  # Top-right corner to the right

#                 # Add rectangle
#                 first_jacket_nozzle_length_cut_rectangle = first_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)
#                 fourth_line_end_pt = first_jacket_nozzle_length_cut_rectangle.Item(3).EndSketchPoint
#                 first_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddHorizontalAlign(fourth_line_end_pt, skpt)

#                 mid_x = (fourth_line_end_pt.Geometry.X + skpt.Geometry.X) / 2
#                 mid_y = (fourth_line_end_pt.Geometry.Y + skpt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 first_jacket_nozzle_length_cut_dim_constraints = first_jacket_nozzle_length_cut_sketch.DimensionConstraints
#                 aligned_dim = first_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_end_pt, skpt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '2 mm'
#                 first_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(skpt, jacket_shell_edge_pg)

#                 fourth_line_start_pt = first_jacket_nozzle_length_cut_rectangle.Item(3).StartSketchPoint
#                 mid_x = (fourth_line_start_pt.Geometry.X + fourth_line_end_pt.Geometry.X) / 2
#                 mid_y = (fourth_line_start_pt.Geometry.Y + fourth_line_end_pt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 aligned_dim = first_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_start_pt, fourth_line_end_pt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '150 mm'

#                 second_line_start_pt = first_jacket_nozzle_length_cut_rectangle.Item(2).StartSketchPoint
#                 second_line_end_pt = first_jacket_nozzle_length_cut_rectangle.Item(2).EndSketchPoint
#                 mid_x = (second_line_start_pt.Geometry.X + second_line_end_pt.Geometry.X) / 2
#                 mid_y = (second_line_start_pt.Geometry.Y + second_line_end_pt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)

#                 aligned_dim = first_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(second_line_start_pt, second_line_end_pt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '50 mm'

#                 forth_line = first_jacket_nozzle_length_cut_rectangle.Item(3)
#                 geo_const = first_jacket_nozzle_length_cut_sketch.GeometricConstraints
#                 geo_const.AddCollinear(shell_jacket_nozzle1_y_axis_pg, forth_line, True, True)

#                 first_jacket_nozzle_length_cut_sketch.Solve()
#                 first_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 first_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
#                 first_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 cut_sketch_profile = first_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

#                 part_def = inv_app.ActiveDocument.ComponentDefinition

#                 cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
#                 cut_sketch_revolve_feature = cut_sketch_revolve_feats.AddFull(cut_sketch_profile, shell_jacket_nozzle1_y_axis_pg, 20482)

#                 # Remove participants again
#                 cut_sketch_revolve_feature.RemoveParticipant(inner_shell)
#                 cut_sketch_revolve_feature.RemoveParticipant(glass_9100)

#                 print("First Jacket Nozzle at Top (Shell) Finish")
#                 # ------------------------------ First Jacket Nozzle at Top (Shell) Finish ------------------------------------------------------------


#                 # ------------------------------ Second Jacket Nozzle at Top (Shell) Start ------------------------------------------------------------
#                 # === NEW Nozzle at -208 Degrees ===
#                 # Set rotation angle for second nozzle
#                 print("Second Jacket Nozzle at Top (Shell) Start")
#                 shell_nozzle2_angle = -135
#                 shell_nozzle2_angle_rad = math.radians(shell_nozzle2_angle)
#                 x_axis_2 = tg.CreateUnitVector(math.cos(shell_nozzle2_angle_rad), 0.0, -math.sin(shell_nozzle2_angle_rad))
#                 y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)
#                 origin = tg.CreatePoint(0.0, 0.0, 0.0)

#                 # Create new plane for second nozzle
#                 shell_nozzle2_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis_2, y_axis)
#                 shell_nozzle2_angled_plane.Visible = True
#                 shell_nozzle2_angled_plane.Grounded = True
#                 shell_nozzle2_angled_plane.Name = "N15_Plane"

#                 # Add sketch on second plane
#                 shell_jacket_nozzle2_sketch = main_assy_def.Sketches.Add(shell_nozzle2_angled_plane)

#                 # Project Y-axis
#                 yaxis_pg_2 = shell_jacket_nozzle2_sketch.AddByProjectingEntity(main_y_axis)

#                 # Define rectangle dimensions
#                 width = 500.0
#                 height = 5.0

#                 # Place rectangle starting at Y-axis (X = 0), going right
#                 pt1 = shell_jacket_nozzle2_sketch.ModelToSketchSpace(tg.CreatePoint(0.0, 0.0, 0.0))  # Bottom-left corner on Y-axis
#                 pt2 = shell_jacket_nozzle2_sketch.ModelToSketchSpace(tg.CreatePoint(width, height, 0.0))  # Top-right corner to the right

#                 # Add rectangle
#                 second_rect_lines = shell_jacket_nozzle2_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)

#                 # Set centerline
#                 second_bottom_line = second_rect_lines.Item(1)
#                 second_bottom_line.Centerline = True

#                 # Get L_DN150 again
#                 xz_plane = L_nozzle_occ.Definition.WorkPlanes["XZ Plane"]
#                 xz_plane_proxy = L_nozzle_occ.CreateGeometryProxy(xz_plane)

#                 # Project and dimension
#                 proj_line_2 = shell_jacket_nozzle2_sketch.AddByProjectingEntity(xz_plane_proxy)

#                 # Dimension from proj_line to bottom_line
#                 second_bottom_line_start_pt1 = second_bottom_line.StartSketchPoint
#                 second_project_line_start_pt2 = proj_line_2.StartSketchPoint
#                 mid_x = (second_bottom_line_start_pt1.Geometry.X + second_project_line_start_pt2.Geometry.X) / 2
#                 mid_y = (second_bottom_line_start_pt1.Geometry.Y + second_project_line_start_pt2.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)

#                 second_dim_constraints = shell_jacket_nozzle2_sketch.DimensionConstraints
#                 vertical_dim = second_dim_constraints.AddTwoPointDistance(second_bottom_line_start_pt1, second_project_line_start_pt2, 19202, text_point, False)
#                 vertical_dim.Parameter.Expression = '2350 mm'


#                 # Height
#                 first_line = second_rect_lines.Item(1)
#                 third_line = second_rect_lines.Item(3)
#                 pt1 = first_line.StartSketchPoint
#                 pt2 = third_line.StartSketchPoint
#                 mid_x = (pt1.Geometry.X + pt2.Geometry.X) / 2
#                 mid_y = (pt1.Geometry.Y + pt2.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 vertical_dim2 = second_dim_constraints.AddTwoPointDistance(pt1, pt2, 19202, text_point, False)
#                 vertical_dim2.Parameter.Expression = "45 mm"

#                 # Solve and revolve
#                 shell_jacket_nozzle2_sketch.Solve()
#                 shell_jacket_nozzle2_sketch.UpdateProfiles()
#                 shell_jacket_nozzle2_sketch.Profiles.AddForSolid()
#                 shell_jacket_nozzle2_sketch.UpdateProfiles()
#                 profile_2 = shell_jacket_nozzle2_sketch.Profiles.Item(1)

#                 axis_line_2 = second_bottom_line
#                 revolve_feats = part_def.Features.RevolveFeatures
#                 revolve_feature_2 = revolve_feats.AddFull(profile_2, axis_line_2, 20482)

#                 # Remove participants again
#                 revolve_feature_2.RemoveParticipant(inner_shell)
#                 revolve_feature_2.RemoveParticipant(glass_9100)

#                 # Add second axis
#                 cylinder_2 = revolve_feature_2.Faces.Item(1).Geometry
#                 base_pt_2 = cylinder_2.BasePoint
#                 axis_vec_2 = cylinder_2.AxisVector
#                 axis_2 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
#                 axis_2.Name = "N15_Axis"
#                 axis_2.Grounded = True

#                 # Add second nozzle component
#                 shell_jacket_nozzle2 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 shell_jacket_nozzle2.Grounded = False

#                 # Set position
#                 transform_2 = tg.CreateMatrix()
#                 transform_2.SetTranslation(tg.CreateVector(base_pt_2.X, base_pt_2.Y, base_pt_2.Z))
#                 shell_jacket_nozzle2.Transformation = transform_2

#                 # Get proxies
#                 y_axis_2 = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2.Definition.WorkAxes["Y Axis"])
#                 xy_plane_2 = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2.Definition.WorkPlanes["XY Plane"])
#                 xz_plane_2 = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2.Definition.WorkPlanes["XZ Plane"])
#                 shell_face_proxy_2 = jacket_shell.CreateGeometryProxy(jacket_shell_face)

#                 # Add constraints
#                 flush_2 = main_assy_def.Constraints.AddFlushConstraint(shell_nozzle2_angled_plane, xy_plane_2, 0, None, None)
#                 mate_y_2 = main_assy_def.Constraints.AddMateConstraint2(axis_2, y_axis_2, 0, 24833, 24833, 115459, None, None)
#                 tangent_2 = main_assy_def.Constraints.AddTangentConstraint(xz_plane_2, shell_face_proxy_2, False, "140 mm")

#                 # Start cut revolve operation on first jacket nozzle:
#                 yz_plane = shell_jacket_nozzle2.Definition.WorkPlanes["YZ Plane"]
#                 yz_plane_proxy = shell_jacket_nozzle2.CreateGeometryProxy(yz_plane)
#                 second_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(yz_plane_proxy)

#                 # jacket_shell_edge = jacket_shell.Definition.SurfaceBodies[0].Edges.Item(7) # 
#                 # jacket_shell_edge_proxy = jacket_shell.CreateGeometryProxy(jacket_shell_edge)
#                 jacket_shell_edge_pg = second_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(jacket_shell_edge_proxy)

#                 shell_jacket_nozzle2_y_axis = shell_jacket_nozzle2.Definition.WorkAxes["Y Axis"]
#                 shell_jacket_nozzle2_y_axis_proxy = shell_jacket_nozzle2.CreateGeometryProxy(shell_jacket_nozzle2_y_axis)
#                 shell_jacket_nozzle2_y_axis_pg = second_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(shell_jacket_nozzle2_y_axis_proxy)
#                 shell_jacket_nozzle2_y_axis_pg.CenterLine = True

#                 # # 8. Create 2D point at that location
#                 pt2d = tg.CreatePoint2d(0.0, 0.0)

#                 # 9. Add the sketch point
#                 skpt = second_jacket_nozzle_length_cut_sketch.SketchPoints.Add(pt2d, False)

#                 width = 5.0
#                 height = 15.0

#                 # Place rectangle starting at Y-axis (X = 0), going right
#                 pt1 = second_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(0.0, 0.0, 0.0))  # Bottom-left corner on Y-axis
#                 pt2 = second_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(tg.CreatePoint(width, height, 0.0))  # Top-right corner to the right

#                 # Add rectangle
#                 second_jacket_nozzle_length_cut_rectangle = second_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(pt1, pt2)
#                 fourth_line_end_pt = second_jacket_nozzle_length_cut_rectangle.Item(3).EndSketchPoint
#                 second_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddHorizontalAlign(fourth_line_end_pt, skpt)
                
#                 mid_x = (fourth_line_end_pt.Geometry.X + skpt.Geometry.X) / 2
#                 mid_y = (fourth_line_end_pt.Geometry.Y + skpt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 second_jacket_nozzle_length_cut_dim_constraints = second_jacket_nozzle_length_cut_sketch.DimensionConstraints
#                 aligned_dim = second_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_end_pt, skpt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '2 mm'
#                 second_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(skpt, jacket_shell_edge_pg)

#                 fourth_line_start_pt = second_jacket_nozzle_length_cut_rectangle.Item(3).StartSketchPoint
#                 mid_x = (fourth_line_start_pt.Geometry.X + fourth_line_end_pt.Geometry.X) / 2
#                 mid_y = (fourth_line_start_pt.Geometry.Y + fourth_line_end_pt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)
#                 aligned_dim = second_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(fourth_line_start_pt, fourth_line_end_pt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '150 mm'

#                 second_line_start_pt = second_jacket_nozzle_length_cut_rectangle.Item(2).StartSketchPoint
#                 second_line_end_pt = second_jacket_nozzle_length_cut_rectangle.Item(2).EndSketchPoint
#                 mid_x = (second_line_start_pt.Geometry.X + second_line_end_pt.Geometry.X) / 2
#                 mid_y = (second_line_start_pt.Geometry.Y + second_line_end_pt.Geometry.Y) / 2
#                 text_point = tg.CreatePoint2d(mid_x, mid_y)

#                 aligned_dim = second_jacket_nozzle_length_cut_dim_constraints.AddTwoPointDistance(second_line_start_pt, second_line_end_pt, 19203, text_point, False)
#                 aligned_dim.Parameter.Expression = '50 mm'

#                 forth_line = second_jacket_nozzle_length_cut_rectangle.Item(3)
#                 geo_const = second_jacket_nozzle_length_cut_sketch.GeometricConstraints
#                 geo_const.AddCollinear(shell_jacket_nozzle2_y_axis_pg, forth_line, True, True)

#                 second_jacket_nozzle_length_cut_sketch.Solve()
#                 second_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 second_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
#                 second_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 cut_sketch_profile = second_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

#                 part_def = inv_app.ActiveDocument.ComponentDefinition

#                 cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
#                 cut_sketch_revolve_feature = cut_sketch_revolve_feats.AddFull(cut_sketch_profile, shell_jacket_nozzle2_y_axis_pg, 20482)

#                 # Remove participants again
#                 cut_sketch_revolve_feature.RemoveParticipant(inner_shell)
#                 cut_sketch_revolve_feature.RemoveParticipant(glass_9100)


#                 print("Second Jacket Nozzle at Top (Shell) Finish")
#                 # ------------------------------ Second Jacket Nozzle at Top (Shell) Finish ------------------------------------------------------------

#             elif item["component"] == 'jacketnozzle_bottom':
#                 # ------------------------------ Third Jacket Nozzle at Bottom Start ------------------------------------------------------------
#                 print("Third Jacket Nozzle at Bottom Start")
#                 bottom_nozzle1_angle = -90
#                 angle_rad = math.radians(bottom_nozzle1_angle)
#                 origin = tg.CreatePoint(0.0, 0.0, 0.0)
#                 x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
#                 y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

#                 # Add Work Plane: N11_Plane
#                 bottom_nozzle1_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
#                 bottom_nozzle1_angled_plane.Visible = True
#                 bottom_nozzle1_angled_plane.Name = "N11_Plane"
#                 bottom_nozzle1_angled_plane.Grounded = True

#                 bottom_jacket_nozzle3_sketch = main_assy_def.Sketches.Add(main_assy_def.WorkPlanes["XZ Plane"])
#                 originPoint = main_assy_def.WorkPoints["Center Point"]  # Usually the origin work point
#                 projectedCenter = bottom_jacket_nozzle3_sketch.AddByProjectingEntity(originPoint)
#                 originSketchPoint  = bottom_jacket_nozzle3_sketch.SketchPoints.Item(1)
#                 startPt = tg.CreatePoint2d(0, 0)
#                 endPt = tg.CreatePoint2d(37, 0)  # 370 mm in cm (as Inventor usually uses cm internally)

#                 line1 = bottom_jacket_nozzle3_sketch.SketchLines.AddByTwoPoints(startPt, endPt)
#                 line1.Construction = True
#                 horizontal_line1 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddHorizontal(line1)
#                 coincident0 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(line1.StartSketchPoint, projectedCenter)


#                 dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
#                 line_1_dimension = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddTwoPointDistance(line1.StartSketchPoint, line1.EndSketchPoint, 19201, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '370 mm'

#                 endPt2 = tg.CreatePoint2d(0, -37)  # 370 mm along Y
#                 line2 = bottom_jacket_nozzle3_sketch.SketchLines.AddByTwoPoints(startPt, endPt2)
#                 line2.Construction = True

#                 circle_center_point = line2.EndSketchPoint
#                 center2d = circle_center_point.Geometry
#                 circle = bottom_jacket_nozzle3_sketch.SketchCircles.AddByCenterRadius(center2d, 4.6)

#                 dimTextPt2 = tg.CreatePoint2d(-10, 10)  # Text placement
#                 line_2_dimension = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddTwoPointDistance(line2.StartSketchPoint, line2.EndSketchPoint, 19203, dimTextPt2)
#                 line_2_dimension.Parameter.Expression = '370 mm'
#                 # vertical_constraint = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddVertical(line2)

#                 dimTextPoint = tg.CreatePoint2d(circle.CenterSketchPoint.Geometry.X + 50, circle.CenterSketchPoint.Geometry.Y)
#                 # Add diameter dimension (not driven by default, so it drives the size)
#                 diameter_dimension = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddDiameter(circle, dimTextPoint)
#                 # Optionally, set the diameter value explicitly, e.g. 92 mm
#                 diameter_dimension.Parameter.Expression = '92 mm'
                
#                 textPoint = tg.CreatePoint2d(10, -10)  # position of dimension text
#                 angleDim = bottom_jacket_nozzle3_sketch.DimensionConstraints.AddTwoLineAngle(line1, line2, textPoint)
#                 angleDim.Parameter.Expression = "90.0 deg"
                
#                 circle_center = circle.CenterSketchPoint    # The SketchPoint at the center of the circle
#                 line_endpoint = line2.EndSketchPoint

#                 # coincident1 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(line2.StartSketchPoint, projectedCenter)
#                 line2.StartSketchPoint.Merge(projectedCenter)
#                 coincident_circle = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(circle_center, line_endpoint)
                
#                 bottom_jacket_nozzle3_sketch.Solve()
#                 bottom_jacket_nozzle3_sketch.UpdateProfiles()
#                 bottom_jacket_nozzle3_sketch.Profiles.AddForSolid()
#                 bottom_jacket_nozzle3_sketch.UpdateProfiles()

#                 extrude_features  = part_def.Features.ExtrudeFeatures
#                 extrude_def = extrude_features.CreateExtrudeDefinition(bottom_jacket_nozzle3_sketch.Profiles[0], 20482)
#                 extrude_def.SetDistanceExtent(150, 20994)
#                 extrude = extrude_features.Add(extrude_def)

#                 extrude_3_n11 = extrude.Faces.Item(1).Geometry
#                 base_pt_2 = extrude_3_n11.BasePoint
#                 axis_vec_2 = extrude_3_n11.AxisVector
#                 axis_3 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
#                 axis_3.Name = "N11_Axis"
#                 axis_3.Grounded = True

#                 # Add second nozzle component
#                 jacketnozzle_3 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 jacketnozzle_3.Grounded = False

#                 L_occ = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="L_DN150")
#                 xz_plane = L_occ.Definition.WorkPlanes["XZ Plane"]
#                 xz_plane_proxy = L_occ.CreateGeometryProxy(xz_plane)

#                 # Set position
#                 transform_3 = tg.CreateMatrix()
#                 transform_3.SetTranslation(tg.CreateVector(base_pt_2.X, base_pt_2.Y, base_pt_2.Z))
#                 jacketnozzle_3.Transformation = transform_3

#                 # Get proxies
#                 y_axis_3 = jacketnozzle_3.CreateGeometryProxy(jacketnozzle_3.Definition.WorkAxes["Y Axis"])
#                 xy_plane_3 = jacketnozzle_3.CreateGeometryProxy(jacketnozzle_3.Definition.WorkPlanes["XY Plane"])
#                 xz_plane_3 = jacketnozzle_3.CreateGeometryProxy(jacketnozzle_3.Definition.WorkPlanes["XZ Plane"])
#                 # xy_plane_main = main_assy_def.WorkPlanes['XY Plane']

#                 # Add constraints
#                 flush_3 = main_assy_def.Constraints.AddFlushConstraint(bottom_nozzle1_angled_plane, xy_plane_3, 0, None, None)
#                 mate_y_3 = main_assy_def.Constraints.AddMateConstraint2(axis_3, y_axis_3, 0, 24833, 24833, 115459, None, None)
#                 mate_xz_3 = main_assy_def.Constraints.AddMateConstraint2(xz_plane_3, xz_plane_proxy, "90 mm", 24833, 24833, 115460, None, None)

#                 # Start cut revolve operation on first jacket nozzle:

#                 # xz_plane_nozzle_3 = jacketnozzle_3.Definition.WorkPlanes["XY Plane"]
#                 # bottom_nozzle1_angled_plane_proxy = jacketnozzle_3.CreateGeometryProxy(bottom_nozzle1_angled_plane)
#                 third_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(bottom_nozzle1_angled_plane)
                
#                 bottom_jacket_nozzle3_y_axis = jacketnozzle_3.Definition.WorkAxes["Y Axis"]
#                 bottom_jacket_nozzle3_y_axis_proxy = jacketnozzle_3.CreateGeometryProxy(bottom_jacket_nozzle3_y_axis)
#                 bottom_jacket_nozzle3_y_axis_pg = third_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_jacket_nozzle3_y_axis_proxy)
#                 bottom_jacket_nozzle3_y_axis_pg.CenterLine = True
                
#                 bottom_swg_dish = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="BTM-1950")
#                 bottom_swg_dish_center_point = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkPoints["Center Point"])
#                 bottom_swg_dish_center_proj = third_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_center_point)

#                 bottom_swg_dish_y_axis = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkAxes["Y Axis"])
                

#                 bottom_swg_dish_y_axis_proj = third_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_y_axis)
#                 bottom_swg_dish_y_axis_proj_start_pt = bottom_swg_dish_y_axis_proj.StartSketchPoint
#                 # bottom_swg_dish_y_axis_proj.CenterLine = True

#                 # Draw Circle
#                 # center2d_point = tg.CreatePoint2d(0, 0)
#                 textPoint = tg.CreatePoint2d(10, 10)
#                 third_jacket_nozzle_circle = third_jacket_nozzle_length_cut_sketch.SketchCircles.AddByCenterRadius(bottom_swg_dish_y_axis_proj_start_pt.Geometry, 202.0)
#                 dim = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddRadius(third_jacket_nozzle_circle, textPoint)
#                 dim.Parameter.Expression = '2020 mm'
#                 third_jacket_nozzle_circle.Construction = True
                
#                 third_jacket_nozzle_circle_center_pt = third_jacket_nozzle_circle.CenterSketchPoint

#                 third_jacket_nozzle_circle_coincidence_2 = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_y_axis_proj, third_jacket_nozzle_circle_center_pt)
#                 third_jacket_nozzle_circle_coincidence_1 = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_center_proj, third_jacket_nozzle_circle)
                

#                 rect1_width = 10.0
#                 rect1_height = 5.0
#                 center_x = bottom_swg_dish_center_proj.Geometry.X
#                 center_y = bottom_swg_dish_center_proj.Geometry.Y

#                 rect1_bottom_left_pt = tg.CreatePoint2d(center_x - rect1_width / 2, center_y)
#                 rect1_top_right_pt = tg.CreatePoint2d(center_x + rect1_width / 2, center_y + rect1_height)
#                 # Create 2D corner points in sketch space
#                 # rect1_bottom_left_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_bottom_left_pt)  # Bottom-left
#                 # rect1_top_right_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_top_right_pt)  # Top-right

#                 # Add rectangle
#                 rect1_lines = third_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(rect1_bottom_left_pt, rect1_top_right_pt)

#                 fourth_line_of_rect1 = rect1_lines.Item(4)
#                 collinear1 = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCollinear(bottom_jacket_nozzle3_y_axis_pg, fourth_line_of_rect1)

#                 second_line_of_rect1 = rect1_lines.Item(2)

#                 first_line_of_rect1 = rect1_lines.Item(1)
#                 dimTextPt1 = tg.CreatePoint2d(-10, 10)  # Text placement
#                 line_1_dimension = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(first_line_of_rect1.StartSketchPoint, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '50 mm'

                
#                 dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
#                 line_1_dimension = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(second_line_of_rect1.StartSketchPoint, second_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '150 mm'

#                 new_pt = tg.CreatePoint2d(10, -10)
#                 new_sketch_pt = third_jacket_nozzle_length_cut_sketch.SketchPoints.Add(new_pt, False)
#                 coincidence1_new_pt = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, third_jacket_nozzle_circle)

#                 dimTextPt1 = tg.CreatePoint2d(10, 10)  # Text placement
#                 line_1_dimension = third_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(new_sketch_pt, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '9 mm'

#                 coincidence1_new_pt = third_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, second_line_of_rect1)

#                 third_jacket_nozzle_length_cut_sketch.Solve()
#                 third_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 third_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
#                 third_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 third_cut_sketch_profile = third_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

#                 part_def = inv_app.ActiveDocument.ComponentDefinition

#                 third_cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
#                 third_cut_sketch_revolve_feature = third_cut_sketch_revolve_feats.AddFull(third_cut_sketch_profile, bottom_jacket_nozzle3_y_axis_pg, 20482)

#                 # Remove participants again
#                 third_cut_sketch_revolve_feature.RemoveParticipant(bottom_swg_dish)
#                 third_cut_sketch_revolve_feature.RemoveParticipant(glass_9100)

#                 # first_line_of_rect1
#                 # New Sketch: For Nozzle inner cut (Extrude)
#                 nozzle_3_yz_plane = jacketnozzle_3.Definition.WorkPlanes["YZ Plane"]
#                 nozzle_3_yz_plane_proxy = jacketnozzle_3.CreateGeometryProxy(nozzle_3_yz_plane)
#                 nozzle_3_yz_plane_sketch = main_assy_def.Sketches.Add(nozzle_3_yz_plane_proxy)

#                 nozzle_3_y_axis = jacketnozzle_3.Definition.WorkAxes["Y Axis"]
#                 nozzle_3_y_axis_proxy = jacketnozzle_3.CreateGeometryProxy(nozzle_3_y_axis)
#                 nozzle_3_y_axis_pg = nozzle_3_yz_plane_sketch.AddByProjectingEntity(nozzle_3_y_axis_proxy)
#                 nozzle_3_y_axis_pg.CenterLine = True

#                 first_line_of_rect1_pg = nozzle_3_yz_plane_sketch.AddByProjectingEntity(first_line_of_rect1)

#                 # Add rectangle 1
#                 nozzle_3_sketch_rectangle = nozzle_3_yz_plane_sketch.SketchLines.AddAsTwoPointRectangle(tg.CreatePoint2d(0, -10), tg.CreatePoint2d(10, 0))
#                 nozzle_3_sketch_rectangle_line1 = nozzle_3_sketch_rectangle.Item(1)
#                 nozzle_3_sketch_rectangle_line2 = nozzle_3_sketch_rectangle.Item(2)
#                 nozzle_3_sketch_rectangle_line3 = nozzle_3_sketch_rectangle.Item(3)
#                 nozzle_3_sketch_rectangle_line4 = nozzle_3_sketch_rectangle.Item(4)

                
#                 # nozzle_3_sketch_lin3_yaxis_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle_line3.StartSketchPoint, nozzle_3_y_axis_pg.StartSketchPoint, 19203, dimTextPt)
#                 # nozzle_3_sketch_lin3_yaxis_dim.Parameter.Expression = '15 mm'

#                 dimTextPt = tg.CreatePoint2d(15, -5)
#                 nozzle_3_sketch_lin4_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle_line4.StartSketchPoint, nozzle_3_sketch_rectangle_line4.EndSketchPoint, 19203, dimTextPt)
#                 nozzle_3_sketch_lin4_dim.Parameter.Expression = '48 mm'

#                 dimTextPt = tg.CreatePoint2d(-10, 15)
#                 nozzle_3_sketch_lin1_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle_line1.StartSketchPoint, nozzle_3_sketch_rectangle_line1.EndSketchPoint, 19203, dimTextPt)
#                 nozzle_3_sketch_lin1_dim.Parameter.Expression = '38 mm'

#                 # dimTextPt = tg.CreatePoint2d(-15, -5)
#                 # nozzle_3_sketch_lin3_yaxis_dim_offset = nozzle_3_yz_plane_sketch.DimensionConstraints.AddOffset(nozzle_3_sketch_rectangle_line3, nozzle_3_y_axis_pg, dimTextPt, True)
#                 # nozzle_3_sketch_lin3_yaxis_dim_offset.Parameter.Expression = '15 mm'

#                 nozzle_3_sketch_fillet_arc = nozzle_3_yz_plane_sketch.SketchArcs.AddByFillet(
#                         nozzle_3_sketch_rectangle_line3,                  # Second sketch line (e.g. rectangle's 3rd line)
#                         nozzle_3_sketch_rectangle_line4,                  # First sketch line (e.g. rectangle's 2nd line)
#                         "15 mm",                 # Fillet radius (use string to specify mm)=
#                         nozzle_3_sketch_rectangle_line3.StartSketchPoint.Geometry,  # Point on second line
#                         nozzle_3_sketch_rectangle_line4.EndSketchPoint.Geometry,   # Point on first line
#                     )
                
#                 arc_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddArcLength(nozzle_3_sketch_fillet_arc, tg.CreatePoint2d(-5, 5))
#                 arc_dim.Parameter.Expression = '10 mm'
                
#                 nozzle_3_yz_plane_sketch_verticle_align =  nozzle_3_yz_plane_sketch.GeometricConstraints.AddVerticalAlign(first_line_of_rect1_pg, nozzle_3_sketch_rectangle_line2.EndSketchPoint)

#                 profile1 = nozzle_3_yz_plane_sketch.Profiles.AddForSolid()
#                 nozzle_3_yz_plane_sketch.UpdateProfiles()

#                 # extrude_def1 = part_def.Features.ExtrudeFeatures.CreateExtrudeDefinition(profile1, 20482)
#                 # extrude_def1.SetDistanceExtent("150 mm", 20995)
#                 # extrude = part_def.Features.ExtrudeFeatures.Add(extrude_def1)
                
#                 # Add rectangle 2 -------------------- Second Rectangle -----------------------
#                 nozzle_3_sketch_rectangle2 = nozzle_3_yz_plane_sketch.SketchLines.AddAsTwoPointRectangle(tg.CreatePoint2d(0, -10), tg.CreatePoint2d(10, 0))
#                 nozzle_3_sketch_rectangle2_line1 = nozzle_3_sketch_rectangle2.Item(1)
#                 nozzle_3_sketch_rectangle2_line2 = nozzle_3_sketch_rectangle2.Item(2)
#                 nozzle_3_sketch_rectangle2_line3 = nozzle_3_sketch_rectangle2.Item(3)
#                 nozzle_3_sketch_rectangle2_line4 = nozzle_3_sketch_rectangle2.Item(4)

#                 dimTextPt = tg.CreatePoint2d(15, -5)
#                 nozzle_3_sketch_lin4_dim2 = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle2_line4.StartSketchPoint, nozzle_3_sketch_rectangle2_line4.EndSketchPoint, 19203, dimTextPt)
#                 nozzle_3_sketch_lin4_dim2.Parameter.Expression = '48 mm'

#                 dimTextPt = tg.CreatePoint2d(-10, 15)
#                 nozzle_3_sketch_lin1_dim2 = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle2_line1.StartSketchPoint, nozzle_3_sketch_rectangle2_line1.EndSketchPoint, 19203, dimTextPt)
#                 nozzle_3_sketch_lin1_dim2.Parameter.Expression = '38 mm'

#                 # dimTextPt = tg.CreatePoint2d(-15, -5)
#                 # nozzle_3_sketch_lin3_yaxis_dim_offset2 = nozzle_3_yz_plane_sketch.DimensionConstraints.AddOffset(nozzle_3_sketch_rectangle2_line1, nozzle_3_y_axis_pg, dimTextPt, True)
#                 # nozzle_3_sketch_lin3_yaxis_dim_offset2.Parameter.Expression = '15 mm'

#                 nozzle_3_sketch_fillet_arc2 = nozzle_3_yz_plane_sketch.SketchArcs.AddByFillet(
#                         nozzle_3_sketch_rectangle2_line1,                  # Second sketch line (e.g. rectangle's 3rd line)
#                         nozzle_3_sketch_rectangle2_line4,                  # First sketch line (e.g. rectangle's 2nd line)
#                         "10 mm",                 # Fillet radius (use string to specify mm)=
#                         nozzle_3_sketch_rectangle2_line1.EndSketchPoint.Geometry,  # Point on second line
#                         nozzle_3_sketch_rectangle2_line4.StartSketchPoint.Geometry,   # Point on first line
#                     )
                
#                 arc_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddArcLength(nozzle_3_sketch_fillet_arc2, tg.CreatePoint2d(5, -5))
#                 arc_dim.Parameter.Expression = '10 mm'
                
#                 nozzle_3_yz_plane_sketch_verticle_align2 =  nozzle_3_yz_plane_sketch.GeometricConstraints.AddVerticalAlign(first_line_of_rect1_pg, nozzle_3_sketch_rectangle2_line2.StartSketchPoint)

#                 nozzle_3_yz_plane_sketch.GeometricConstraints.AddSymmetry( nozzle_3_sketch_rectangle2_line1, nozzle_3_sketch_rectangle_line3,nozzle_3_y_axis_pg)

#                 dimTextPt = tg.CreatePoint2d(-10, 15)
#                 nozzle_3_sketch_lin1_dim = nozzle_3_yz_plane_sketch.DimensionConstraints.AddTwoPointDistance(nozzle_3_sketch_rectangle2_line2.StartSketchPoint, nozzle_3_sketch_rectangle_line2.EndSketchPoint, 19203, dimTextPt)
#                 nozzle_3_sketch_lin1_dim.Parameter.Expression = '15 mm'

#                 nozzle_3_yz_plane_sketch.Solve()
#                 profile2 = nozzle_3_yz_plane_sketch.Profiles.AddForSolid()
#                 nozzle_3_yz_plane_sketch.UpdateProfiles()

#                 extrude_def2 = part_def.Features.ExtrudeFeatures.CreateExtrudeDefinition(profile2, 20482)
#                 extrude_def2.SetDistanceExtent("150 mm", 20995)
#                 extrude = part_def.Features.ExtrudeFeatures.Add(extrude_def2)

#                 JKT_occ = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="JKT-2100")
#                 extrude.RemoveParticipant(JKT_occ)

#                 print("Third Jacket Nozzle at Bottom End")
#                 # ------------------------------ Third Jacket Nozzle at Bottom End ------------------------------------------------------------

#                 # ------------------------------ Forth Jacket Nozzle at Bottom Start ------------------------------------------------------------
#                 print("Forth Jacket Nozzle at Bottom Start")

#                 bottom_nozzle2_angle = -270
#                 angle_rad = math.radians(bottom_nozzle2_angle)
#                 origin = tg.CreatePoint(0.0, 0.0, 0.0)
#                 x_axis = tg.CreateUnitVector(math.cos(angle_rad), 0.0, -math.sin(angle_rad))
#                 y_axis = tg.CreateUnitVector(0.0, 1.0, 0.0)

#                 # Add Work Plane: N17_Plane
#                 bottom_nozzle2_angled_plane = main_assy_def.WorkPlanes.AddFixed(origin, x_axis, y_axis)
#                 bottom_nozzle2_angled_plane.Visible = True
#                 bottom_nozzle2_angled_plane.Name = "N17_Plane"
#                 bottom_nozzle2_angled_plane.Grounded = True

#                 bottom_jacket_nozzle4_sketch = main_assy_def.Sketches.Add(main_assy_def.WorkPlanes["XZ Plane"])
#                 originPoint = main_assy_def.WorkPoints["Center Point"]  # Usually the origin work point
#                 projectedCenter = bottom_jacket_nozzle4_sketch.AddByProjectingEntity(originPoint)
#                 originSketchPoint  = bottom_jacket_nozzle4_sketch.SketchPoints.Item(1)
#                 startPt = tg.CreatePoint2d(0, 0)
#                 endPt = tg.CreatePoint2d(37, 0)  # 370 mm in cm (as Inventor usually uses cm internally)

#                 line1 = bottom_jacket_nozzle4_sketch.SketchLines.AddByTwoPoints(startPt, endPt)
#                 line1.Construction = True
#                 horizontal_line1 = bottom_jacket_nozzle4_sketch.GeometricConstraints.AddHorizontal(line1)
#                 coincident0 = bottom_jacket_nozzle4_sketch.GeometricConstraints.AddCoincident(line1.StartSketchPoint, projectedCenter)


#                 dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
#                 line_1_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddTwoPointDistance(line1.StartSketchPoint, line1.EndSketchPoint, 19201, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '370 mm'

#                 endPt2 = tg.CreatePoint2d(0, 37)  # 370 mm along Y
#                 line2 = bottom_jacket_nozzle4_sketch.SketchLines.AddByTwoPoints(startPt, endPt2)
#                 line2.Construction = True

#                 circle_center_point = line2.EndSketchPoint
#                 center2d = circle_center_point.Geometry
#                 circle = bottom_jacket_nozzle4_sketch.SketchCircles.AddByCenterRadius(center2d, 4.6)

#                 dimTextPt2 = tg.CreatePoint2d(-10, 10)  # Text placement
#                 line_2_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddTwoPointDistance(line2.StartSketchPoint, line2.EndSketchPoint, 19203, dimTextPt2)
#                 line_2_dimension.Parameter.Expression = '370 mm'
#                 # vertical_constraint = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddVertical(line2)

#                 dimTextPoint = tg.CreatePoint2d(circle.CenterSketchPoint.Geometry.X + 50, circle.CenterSketchPoint.Geometry.Y)
#                 # Add diameter dimension (not driven by default, so it drives the size)
#                 diameter_dimension = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddDiameter(circle, dimTextPoint)
#                 # Optionally, set the diameter value explicitly, e.g. 92 mm
#                 diameter_dimension.Parameter.Expression = '92 mm'
                
#                 textPoint = tg.CreatePoint2d(10, 10)  # position of dimension text
#                 angleDim = bottom_jacket_nozzle4_sketch.DimensionConstraints.AddTwoLineAngle(line1, line2, textPoint)
#                 angleDim.Parameter.Expression = "90.0 deg"
                
#                 circle_center = circle.CenterSketchPoint    # The SketchPoint at the center of the circle
#                 line_endpoint = line2.EndSketchPoint

#                 # coincident1 = bottom_jacket_nozzle3_sketch.GeometricConstraints.AddCoincident(line2.StartSketchPoint, projectedCenter)
#                 line2.StartSketchPoint.Merge(projectedCenter)
#                 coincident_circle = bottom_jacket_nozzle4_sketch.GeometricConstraints.AddCoincident(circle_center, line_endpoint)
                
                

#                 bottom_jacket_nozzle4_sketch.Solve()
#                 bottom_jacket_nozzle4_sketch.UpdateProfiles()
#                 bottom_jacket_nozzle4_sketch.Profiles.AddForSolid()
#                 bottom_jacket_nozzle4_sketch.UpdateProfiles()

#                 extrude_features  = part_def.Features.ExtrudeFeatures
#                 extrude_def = extrude_features.CreateExtrudeDefinition(bottom_jacket_nozzle4_sketch.Profiles[0], 20482)
#                 extrude_def.SetDistanceExtent(150, 20994)
#                 extrude = extrude_features.Add(extrude_def)

#                 extrude_4_n17 = extrude.Faces.Item(1).Geometry
#                 base_pt_2 = extrude_4_n17.BasePoint
#                 axis_vec_2 = extrude_4_n17.AxisVector
#                 axis_4 = main_assy_def.WorkAxes.AddFixed(base_pt_2, axis_vec_2, False)
#                 axis_4.Name = "N17_Axis"
#                 axis_4.Grounded = True

#                 # Add second nozzle component
#                 jacketnozzle_4 = main_assy_def.Occurrences.Add(item["filepath"], tg.CreateMatrix())
#                 jacketnozzle_4.Grounded = False

#                 L_occ = self.find_occurrence_recursive(occurrences=monoblock.SubOccurrences, target_name="L_DN150")
#                 xz_plane = L_occ.Definition.WorkPlanes["XZ Plane"]
#                 xz_plane_proxy = L_occ.CreateGeometryProxy(xz_plane)

#                 # Set position
#                 transform_4 = tg.CreateMatrix()
#                 transform_4.SetTranslation(tg.CreateVector(base_pt_2.X, base_pt_2.Y, base_pt_2.Z))
#                 jacketnozzle_4.Transformation = transform_4

#                 # Get proxies
#                 y_axis_4 = jacketnozzle_4.CreateGeometryProxy(jacketnozzle_4.Definition.WorkAxes["Y Axis"])
#                 xy_plane_4 = jacketnozzle_4.CreateGeometryProxy(jacketnozzle_4.Definition.WorkPlanes["XY Plane"])
#                 xz_plane_4 = jacketnozzle_4.CreateGeometryProxy(jacketnozzle_4.Definition.WorkPlanes["XZ Plane"])
#                 # xy_plane_main = main_assy_def.WorkPlanes['XY Plane']

#                 # Add constraints
#                 flush_4 = main_assy_def.Constraints.AddFlushConstraint(bottom_nozzle2_angled_plane, xy_plane_4, 0, None, None)
#                 mate_y_4 = main_assy_def.Constraints.AddMateConstraint2(axis_4, y_axis_4, 0, 24833, 24833, 115459, None, None)
#                 mate_xz_4 = main_assy_def.Constraints.AddMateConstraint2(xz_plane_4, xz_plane_proxy, "90 mm", 24833, 24833, 115460, None, None)

#                 # Start cut revolve operation on first jacket nozzle:

#                 # xz_plane_nozzle_3 = jacketnozzle_3.Definition.WorkPlanes["XY Plane"]
#                 # bottom_nozzle1_angled_plane_proxy = jacketnozzle_3.CreateGeometryProxy(bottom_nozzle1_angled_plane)
#                 fourth_jacket_nozzle_length_cut_sketch = main_assy_def.Sketches.Add(bottom_nozzle2_angled_plane)
                
#                 bottom_jacket_nozzle4_y_axis = jacketnozzle_4.Definition.WorkAxes["Y Axis"]
#                 bottom_jacket_nozzle4_y_axis_proxy = jacketnozzle_4.CreateGeometryProxy(bottom_jacket_nozzle4_y_axis)
#                 bottom_jacket_nozzle4_y_axis_pg = fourth_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_jacket_nozzle4_y_axis_proxy)
#                 bottom_jacket_nozzle4_y_axis_pg.CenterLine = True
                
#                 bottom_swg_dish = self.find_occurrence_recursive(occurrences=main_assy_def.Occurrences, target_name="BTM-1950")
#                 bottom_swg_dish_center_point = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkPoints["Center Point"])
#                 bottom_swg_dish_center_proj = fourth_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_center_point)

#                 bottom_swg_dish_y_axis = bottom_swg_dish.CreateGeometryProxy(bottom_swg_dish.Definition.WorkAxes["Y Axis"])
                

#                 bottom_swg_dish_y_axis_proj = fourth_jacket_nozzle_length_cut_sketch.AddByProjectingEntity(bottom_swg_dish_y_axis)
#                 bottom_swg_dish_y_axis_proj_start_pt = bottom_swg_dish_y_axis_proj.StartSketchPoint
#                 # bottom_swg_dish_y_axis_proj.CenterLine = True

#                 # Draw Circle
#                 # center2d_point = tg.CreatePoint2d(0, 0)
#                 textPoint = tg.CreatePoint2d(10, 10)
#                 fourth_jacket_nozzle_circle = fourth_jacket_nozzle_length_cut_sketch.SketchCircles.AddByCenterRadius(bottom_swg_dish_y_axis_proj_start_pt.Geometry, 202.0)
#                 dim = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddRadius(fourth_jacket_nozzle_circle, textPoint)
#                 dim.Parameter.Expression = '2020 mm'
#                 fourth_jacket_nozzle_circle.Construction = True
                
#                 fourth_jacket_nozzle_circle_center_pt = fourth_jacket_nozzle_circle.CenterSketchPoint

#                 fourth_jacket_nozzle_circle_coincidence_2 = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_y_axis_proj, fourth_jacket_nozzle_circle_center_pt)
#                 fourth_jacket_nozzle_circle_coincidence_1 = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(bottom_swg_dish_center_proj, fourth_jacket_nozzle_circle)
                

#                 rect1_width = 10.0
#                 rect1_height = 5.0
#                 center_x = bottom_swg_dish_center_proj.Geometry.X
#                 center_y = bottom_swg_dish_center_proj.Geometry.Y

#                 rect1_bottom_left_pt = tg.CreatePoint2d(center_x - rect1_width / 2, center_y)
#                 rect1_top_right_pt = tg.CreatePoint2d(center_x + rect1_width / 2, center_y + rect1_height)
#                 # Create 2D corner points in sketch space
#                 # rect1_bottom_left_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_bottom_left_pt)  # Bottom-left
#                 # rect1_top_right_pt = third_jacket_nozzle_length_cut_sketch.ModelToSketchSpace(rect1_top_right_pt)  # Top-right

#                 # Add rectangle
#                 rect1_lines = fourth_jacket_nozzle_length_cut_sketch.SketchLines.AddAsTwoPointRectangle(rect1_bottom_left_pt, rect1_top_right_pt)

#                 fourth_line_of_rect1 = rect1_lines.Item(4)
#                 collinear1 = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCollinear(bottom_jacket_nozzle4_y_axis_pg, fourth_line_of_rect1)

#                 second_line_of_rect1 = rect1_lines.Item(2)

#                 first_line_of_rect1 = rect1_lines.Item(1)
#                 dimTextPt1 = tg.CreatePoint2d(-10, 10)  # Text placement
#                 line_1_dimension = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(first_line_of_rect1.StartSketchPoint, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '50 mm'

                
#                 dimTextPt1 = tg.CreatePoint2d(10, -10)  # Text placement
#                 line_1_dimension = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(second_line_of_rect1.StartSketchPoint, second_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '150 mm'

#                 new_pt = tg.CreatePoint2d(10, -10)
#                 new_sketch_pt = fourth_jacket_nozzle_length_cut_sketch.SketchPoints.Add(new_pt, False)
#                 coincidence1_new_pt = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, fourth_jacket_nozzle_circle)

#                 dimTextPt1 = tg.CreatePoint2d(10, 10)  # Text placement
#                 line_1_dimension = fourth_jacket_nozzle_length_cut_sketch.DimensionConstraints.AddTwoPointDistance(new_sketch_pt, first_line_of_rect1.EndSketchPoint, 19203, dimTextPt1)
#                 line_1_dimension.Parameter.Expression = '9 mm'

#                 coincidence1_new_pt = fourth_jacket_nozzle_length_cut_sketch.GeometricConstraints.AddCoincident(new_sketch_pt, second_line_of_rect1)

#                 fourth_jacket_nozzle_length_cut_sketch.Solve()
#                 fourth_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 fourth_jacket_nozzle_length_cut_sketch.Profiles.AddForSolid()
#                 fourth_jacket_nozzle_length_cut_sketch.UpdateProfiles()
#                 fourth_cut_sketch_profile = fourth_jacket_nozzle_length_cut_sketch.Profiles.Item(1)

#                 part_def = inv_app.ActiveDocument.ComponentDefinition

#                 fourth_cut_sketch_revolve_feats = part_def.Features.RevolveFeatures
#                 fourth_cut_sketch_revolve_feature = fourth_cut_sketch_revolve_feats.AddFull(fourth_cut_sketch_profile, bottom_jacket_nozzle4_y_axis_pg, 20482)

#                 # Remove participants again
#                 fourth_cut_sketch_revolve_feature.RemoveParticipant(bottom_swg_dish)
#                 fourth_cut_sketch_revolve_feature.RemoveParticipant(glass_9100)

#                 print("Forth Jacket Nozzle at Bottom End")

#         return True
    
#     def find_occurrence_recursive(self, occurrences, target_name):
#         target_lower = target_name.lower()  # Case-insensitive comparison
#         for occ in occurrences:
#             name = occ.Name.lower()
#             display_name = occ.Definition.Document.DisplayName.lower()
#             if target_lower in name or target_lower in display_name:
#                 return occ
#             if hasattr(occ, "SubOccurrences") and occ.SubOccurrences.Count > 0:
#                 found = self.find_occurrence_recursive(occ.SubOccurrences, target_name)
#                 if found:
#                     return found
#         return None

#     def find_named_workplane_in_occurrence(self, occurrence, target_name):
#         try:
#             wp = occurrence.Definition.WorkPlanes.Item(target_name)
#             if wp is not None:
#                 return occurrence.CreateGeometryProxy(wp)
#             # for wp in occurrence.Definition.WorkPlanes:
#             #     if wp.Name == target_name:
#             #         # return occurrence.CreateGeometryProxy(wp)
#             #         return wp, occurrence
#         except:
#             pass  # Not a part or not accessible

#         # Recurse into nested sub-occurrences if it's an assembly
#         if hasattr(occurrence.Definition, "Occurrences"):
#             for sub_occ in occurrence.Definition.Occurrences:
#                 result = self.find_named_workplane_in_occurrence(sub_occ, target_name)
#                 if result:
#                     return result
#         return None
