import math
# Shared envelope and decoration layout for integrated lower body and upper lid.
disc_diameter = param("disc_diameter", 28.9)
disc_thickness = param("disc_thickness", 5.1)
body_diameter = param("body_diameter", 39.6)
diametral_clearance = param("cavity_diametral_clearance", 0.4)  # nominal before radial inset
cavity_radial_inset = param("cavity_radial_inset", 0.06)
axial_clearance = param("cavity_axial_clearance", 0.3)  # nominal clearance before user-requested reduction
middle_height_reduction = param("middle_height_reduction", 0.12)
front_hole_diameter = param("front_hole_diameter", 25.0)
face_thickness = param("face_thickness", 1.3)
rear_tab_width = param("rear_tab_width", 16.0)
rear_tab_top_y = param("rear_tab_top_y", 28.0)
rear_tab_root_y = param("rear_tab_root_y", 10.0)
rear_tab_corner_radius = param("rear_tab_corner_radius", 4.0)
rear_shoulder_radius = param("rear_shoulder_radius", 3.0)
rear_slot_height = param("rear_slot_height", 3.0)
rear_slot_corner_radius = param("rear_slot_corner_radius", 1.2)
rear_slot_center_y = param("rear_slot_center_y", 24.0)
outer_edge_radius = param("outer_edge_radius", 0.45)
surface_pad_radius = param("surface_pad_radius", 16.4)
surface_relief = param("surface_relief", 0.2)
stitch_edge_inset = param("stitch_edge_inset", 1.65)
stitch_length = param("stitch_length", 1.9)
stitch_width = param("stitch_width", 0.6)
stitch_relief = param("stitch_relief", 0.2)
stitch_pitch = param("stitch_pitch", 2.7)
stitch_panel_gap = param("stitch_panel_gap", 0.8)
welt_radius = param("welt_radius", 0.18)
body_radius = body_diameter/2
cavity_radius = (disc_diameter+diametral_clearance)/2-cavity_radial_inset
assert 2*cavity_radius>disc_diameter
neck_panel_width = rear_tab_width-2*(stitch_edge_inset+stitch_width/2+stitch_panel_gap)
rear_slot_width = neck_panel_width  # slot and lower inner decoration share both X edges
nominal_core_height = disc_thickness+axial_clearance
core_height = nominal_core_height-middle_height_reduction
assert core_height >= disc_thickness
stitch_radius = body_radius-stitch_edge_inset
cavity_floor_z = face_thickness
upper_cut_z = face_thickness+core_height
upper_mount_z = 2*face_thickness+core_height
tab_height = rear_tab_top_y-rear_tab_root_y
tab_center = (rear_tab_top_y+rear_tab_root_y)/2
def upper_outline():
    shape = Circle(body_radius)+Pos(0,tab_center)*RectangleRounded(rear_tab_width,tab_height,rear_tab_corner_radius)
    join_y = math.sqrt(body_radius**2-(rear_tab_width/2)**2)
    shoulders=[v for v in shape.vertices() if abs(abs(v.X)-rear_tab_width/2)<0.001 and abs(v.Y-join_y)<0.001]
    assert len(shoulders)==2
    return fillet(shoulders,radius=rear_shoulder_radius)
def cord_slot(height):
    return Pos(0,rear_slot_center_y,-1)*extrude(RectangleRounded(rear_slot_width,rear_slot_height,rear_slot_corner_radius),amount=height+2)
# The former lower faceplate and middle ring are one manufactured solid.
lower_body = Cylinder(body_radius,upper_cut_z,align=(Align.CENTER,Align.CENTER,Align.MIN))
exterior_edges=[e for e in lower_body.edges() if abs(e.bounding_box().min.Z)<1e-7 and abs(e.bounding_box().max.Z)<1e-7]
lower_body=fillet(exterior_edges,radius=outer_edge_radius)
# Keep the original underside of the upper-side ear at Z=4.0.
ear_underside_z=face_thickness+nominal_core_height/2
ear_height=upper_cut_z-ear_underside_z
assert ear_height>0
# Round the ear's complete lower perimeter before joining it to the cylinder;
# the cylinder naturally buries the circular portion of this edge treatment.
ear_body=Pos(0,0,ear_underside_z)*extrude(upper_outline(),amount=ear_height)
ear_outer_edges=[e for e in ear_body.edges()
    if abs(e.bounding_box().min.Z-ear_underside_z)<1e-7
    and abs(e.bounding_box().max.Z-ear_underside_z)<1e-7]
ear_body=fillet(ear_outer_edges,radius=outer_edge_radius)
lower_body=lower_body.fuse(ear_body)
print("ear underside outer perimeter radius",outer_edge_radius)
lower_body-=Pos(0,0,face_thickness)*Cylinder(cavity_radius,core_height+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
panel=Pos(0,0,-surface_relief)*Cylinder(surface_pad_radius,surface_relief+0.15,align=(Align.CENTER,Align.CENTER,Align.MIN))
panel=fillet(panel.edges(),radius=0.14)
piping=Pos(0,0,0.05)*Torus(body_radius-0.65,surface_relief+0.05)
lower_body=lower_body.fuse(panel,piping)
lower_body-=Pos(0,0,-1)*Cylinder(front_hole_diameter/2,upper_cut_z+2,align=(Align.CENTER,Align.CENTER,Align.MIN))
lower_body-=cord_slot(upper_cut_z)
lower_body-=Pos(0,0,-0.04)*Torus(stitch_radius,welt_radius)
capsule=Pos(0,0,-stitch_relief)*extrude(SlotOverall(stitch_length,stitch_width),amount=stitch_relief+0.18)
count=max(12,round(2*math.pi*stitch_radius/stitch_pitch))
stitches=[]
for i in range(count):
    angle=360*i/count
    a=math.radians(angle)
    stitches.append(Pos(stitch_radius*math.cos(a),stitch_radius*math.sin(a),0)*Rot(0,0,angle+78)*capsule)
# Use the opposite face's stitch path and phase on the exposed ear underside.
ear_stitch_path=offset(upper_outline(),amount=-stitch_edge_inset).faces()[0].outer_wire()
ear_count=max(12,round(ear_stitch_path.length/stitch_pitch))
ear_stitches=[]
# Clip the regular-length stitches exactly at the circular body boundary.
ear_stitch_clip=Pos(0,0,ear_underside_z-stitch_relief-0.1)*Cylinder(body_radius,stitch_relief+0.38,align=(Align.CENTER,Align.CENTER,Align.MIN))
for i in range(ear_count):
    u=(i+0.5)/ear_count
    p=ear_stitch_path.position_at(u)
    t=ear_stitch_path.tangent_at(u)
    # The circular body covers the root portion of this path at Z=4.
    if math.hypot(p.X,p.Y)<body_radius-stitch_length/2:
        continue
    if abs(p.X)<rear_slot_width/2+0.5 and abs(p.Y-rear_slot_center_y)<rear_slot_height/2+0.5:
        continue
    angle=math.degrees(math.atan2(t.Y,t.X))-12
    ear_stitch=(Pos(p.X,p.Y,ear_underside_z)*Rot(0,0,angle)*capsule)-ear_stitch_clip
    if len(ear_stitch.solids())>0:
        ear_stitches.append(ear_stitch)
assert len(ear_stitches)>=9
lower_body=lower_body.fuse(*stitches,*ear_stitches)
lower_body-=cord_slot(upper_cut_z)
print("ear underside raised stitches",len(ear_stitches),"relief",stitch_relief,"length",stitch_length,"width",stitch_width)
lower_body.color=srgb("#A65F3D")
assert lower_body.is_valid
assert len(lower_body.solids())==1
assert abs(lower_body.bounding_box().max.Z-upper_cut_z)<1e-6
assert body_radius-cavity_radius>=2.0
assert front_hole_diameter<disc_diameter
print("middle height reduction",middle_height_reduction,"from",nominal_core_height,"to",core_height)
print("cavity axial clearance",core_height-disc_thickness,"lid mating Z",upper_cut_z,"lid mount Z",upper_mount_z)
print("lower body overall height",upper_cut_z+stitch_relief,"ear thickness",ear_height)
print("cavity diameter",2*cavity_radius,"radial inset",cavity_radial_inset)
print("slot width",rear_slot_width,"inner neck decoration width",neck_panel_width,"stitch height",stitch_relief)
publish("middle_ring",lower_body,"一体下壳",material="tpu")
