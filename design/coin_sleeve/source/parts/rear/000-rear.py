import math
s=part("middle")
rear_hole_diameter=param("rear_hole_diameter",25.0)
inner_shoulder_radius=param("rear_inner_shoulder_radius",4.0)
assert rear_hole_diameter<s.disc_diameter
outline=s.upper_outline()
rear=extrude(outline,amount=s.face_thickness)
edges=[e for e in rear.edges() if abs(e.bounding_box().min.Z)<1e-7 and abs(e.bounding_box().max.Z)<1e-7]
rear=fillet(edges,radius=s.outer_edge_radius)
pad_width=s.neck_panel_width
pad_top=s.rear_tab_top_y-(s.stitch_edge_inset+s.stitch_width/2+s.stitch_panel_gap)
pad_height=pad_top-s.rear_tab_root_y
pad_radius=min(s.rear_tab_corner_radius-1.6,pad_width/2-0.1)
panel_outline=Circle(s.surface_pad_radius)+Pos(0,(pad_top+s.rear_tab_root_y)/2)*RectangleRounded(pad_width,pad_height,pad_radius)
pad_join_y=math.sqrt(s.surface_pad_radius**2-(pad_width/2)**2)
pad_shoulders=[v for v in panel_outline.vertices() if abs(abs(v.X)-pad_width/2)<0.001 and abs(v.Y-pad_join_y)<0.001]
assert len(pad_shoulders)==2
# The two marked inner shoulders have their own R4 driving dimension.
panel_outline=fillet(pad_shoulders,radius=inner_shoulder_radius)
panel=Pos(0,0,-s.surface_relief)*extrude(panel_outline,amount=s.surface_relief+0.15)
panel=fillet(panel.edges().filter_by(Axis.Z,reverse=True),radius=0.14)
welt_path=offset(outline,amount=-0.65).faces()[0].outer_wire()
welt_profile=Plane(origin=welt_path.position_at(0),z_dir=welt_path.tangent_at(0))*Circle(s.surface_relief+0.05)
piping=Pos(0,0,0.05)*sweep(welt_profile,path=welt_path)
rear=rear.fuse(panel,piping)
rear-=Pos(0,0,-1)*Cylinder(rear_hole_diameter/2,s.face_thickness+2,align=(Align.CENTER,Align.CENTER,Align.MIN))
slot=s.cord_slot(s.face_thickness)
rear-=slot
stitch_path=offset(outline,amount=-s.stitch_edge_inset).faces()[0].outer_wire()
count=max(12,round(stitch_path.length/s.stitch_pitch))
capsule=Pos(0,0,-s.stitch_relief)*extrude(SlotOverall(s.stitch_length,s.stitch_width),amount=s.stitch_relief+0.18)
stitches=[]
for i in range(count):
    u=(i+0.5)/count
    p=stitch_path.position_at(u)
    t=stitch_path.tangent_at(u)
    angle=math.degrees(math.atan2(t.Y,t.X))-12
    if abs(p.X)<s.rear_slot_width/2+0.5 and abs(p.Y-s.rear_slot_center_y)<s.rear_slot_height/2+0.5:
        continue
    stitches.append(Pos(p.X,p.Y,0)*Rot(0,0,angle)*capsule)
rear=rear.fuse(*stitches)
rear-=slot
rear.color=srgb("#A65F3D")
assert rear.is_valid
assert len(rear.solids())==1
assert abs(rear.bounding_box().max.Z-s.face_thickness)<1e-6
print("upper faceplate thickness",s.face_thickness+s.stitch_relief,"hole",rear_hole_diameter)
publish("rear_shell",rear,"上纹理面盖",material="tpu")