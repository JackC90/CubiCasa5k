import bpy
import numpy as np
import json
import sys
import math
import os.path
from operator import itemgetter
from shapely import geometry

room_classes = ["Background", "Outdoor", "Wall", "Kitchen", "Living Room" ,"Bed Room", "Bath", "Entry", "Railing", "Storage", "Garage", "Undefined"]
icon_classes = ["No Icon", "Window", "Door", "Closet", "Electrical Applience" ,"Toilet", "Sink", "Sauna Bench", "Fire Place", "Bathtub", "Chimney"]
    

# adapted from https://gist.github.com/flashlib/e8261539915426866ae910d55a3f9959
def order_clockwise_bbox(pts):
    xSorted = pts[np.argsort(pts[:, 0]), :]
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost
    rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
    (tr, br) = rightMost
    return np.array([tl, tr, br, bl], dtype="float32")

def categorize_walls_icons(polygons, types):
    polygon_walls = []
    type_walls = []
    polygon_icons = []
    type_icons = []
    
    for idx, t in enumerate(types):
        # polygon corresponding to type
        p = polygons[idx]
        if t["type"] == 'wall':
            type_walls.append(t)
            polygon_walls.append(p)
        elif t["type"] == 'icon':
            type_icons.append(t)
            polygon_icons.append(t)
    return polygon_walls, type_walls, polygon_icons, type_icons


def wall_2d_to_3d(polygons, types, wall_height = 1., scale = 1.):
    l_polygons = len(polygons)

    wall_horizontal_verts = np.empty(shape=(l_polygons * 2, 4, 3), dtype="float32")
    wall_horizontal_faces = np.empty(shape=(l_polygons * 2, 1, 4), dtype="int32")
    wall_vertical_verts = np.empty(shape=(l_polygons, 4, 4, 3), dtype="float32")
    wall_vertical_faces = np.array([np.arange(0, 4, 1)], dtype="int32" )

    np_polygon = np.divide(np.array(polygons), scale)
    
    i = 0
    i_v = 0
    for shape in np_polygon:
        l = len(shape)
        h_t = np.empty(shape=(l, 3), dtype="float32")
        h_b = np.empty(shape=(l, 3), dtype="float32")

        sorted_shape = order_clockwise_bbox(shape)

        j = 0
        for point in sorted_shape:
            t_new = np.array([point[0], point[1], wall_height])
            b_new = np.array([point[0], point[1], 0])

            # Horizontal
            h_t[j] = t_new
            h_b[j] = b_new

            j += 1

        # Horizontal
        h_faces = np.array([np.arange(0, l, 1)])

        # Top
        wall_horizontal_verts[i] = h_t
        wall_horizontal_faces[i] = h_faces

        # Bottom
        i += 1
        wall_horizontal_verts[i] = h_b
        wall_horizontal_faces[i] = h_faces
        i += 1

         # Vertical
        t_tl, t_tr, t_br, t_bl = h_t
        b_tl, b_tr, b_br, b_bl = h_b

        v_l = [t_tl, t_bl, b_bl, b_tl]
        v_t = [t_tr, t_tl, b_tl, b_tr]
        v_r = [t_br, t_tr, b_tr, b_br]
        v_b = [t_bl, t_br, b_br, b_bl]

        sides = np.array([v_l, v_t, v_r, v_b])
        wall_vertical_verts[i_v] = sides
        i_v += 1
    return wall_horizontal_verts, wall_horizontal_faces, wall_vertical_verts, wall_vertical_faces

def icon_2d_to_3d(polygons, types, wall_height = 1., scale = 1.):
    np_polygons = np.divide(np.array(polygons), scale)
    len_polygons = len(np_polygons)

    icons = []

    for i in range(len_polygons):
        shape = np_polygons[i]
        sorted_shape = order_clockwise_bbox(shape)
        icon_type_class = types[i]["class"]
        icon_label = icon_classes["icon_type_class"]
        icons.append({
            "class": icon_type_class,
            "label": icon_label,
            "verts": sorted_shape
        })
    return icons

# Takes Shapely polygons and converts each 2D point into 3D vertex
def room_2d_to_3d(room_polygons, room_types, wall_height = 1., scale = 1.):
    l_rooms = len(room_polygons)
    
    floors = list(range(l_rooms))
    ceilings = list(range(l_rooms))
    
    for i in range(l_rooms):
        shape = room_polygons[i]
        room_type = room_types[i]
        coords = np.divide(np.array(shape["coordinates"]), scale)
        pol_type = shape["type"]
        Poly = geometry.LinearRing
        pol = (Poly(coords[0])) if coords.any() else None
        
        # Clock-wise        
        pol = (Poly(list(pol.coords)[::-1])) if not pol.is_ccw else pol
        
        pol_len = len(pol.coords) - 1
        
        bottom_vert_points = list(range(pol_len))
        top_vert_points = list(range(pol_len))
        
        for j in range(pol_len):
            point = pol.coords[j]
            x = point[0]
            y = point[1]
            # Floor
            bottom_vert_points[j] = [x, y, 0.]
            # Ceiling
            top_vert_points[pol_len - 1 - j] = [x, y, wall_height]
        
        room_class = room_type["class"]
        room_label = room_classes[room_class]

        # Floors
        floors[i] = {
            "verts": bottom_vert_points,
            "faces": [list(range(0, pol_len, 1))],
            "class": room_class,
            "label": room_label
        }
        
        # Ceilings
        ceilings[i] = {
            "verts":  top_vert_points,
            "faces": [list(range(0, pol_len, 1))],
            "class": room_class,
            "label": room_label
        }
    
    return floors, ceilings
        

def init_object(name):
    # Create new blender object and return references to mesh and object
    mymesh = bpy.data.meshes.new(name)
    myobject = bpy.data.objects.new(name, mymesh)
    bpy.context.collection.objects.link(myobject)
    return myobject, mymesh

def create_mat(rgb_color):
    mat = bpy.data.materials.new(name="MaterialName")  # set new material to variable
    mat.diffuse_color = rgb_color if rgb_color else (255,255,255, 1)
    mat.shadow_method = 'OPAQUE'
    return mat

def average(lst):
    return sum(lst) / len(lst)

def get_mesh_center(verts):
    # Calculate center location of a mesh from verts
    x = []
    y = []
    z = []
    
    for vert in verts:
        x.append(vert[0])
        y.append(vert[1])
        z.append(vert[2])
    return [average(x), average(y), average(z)]
        
        
def subtract_center_verts(verts1, verts2):
    # Remove verts1 from all verts in verts2, return result, verts1 & verts2 must have same shape!
    for i in range(0, len(verts2)):
        verts2[i][0] -= verts1[0]
        verts2[i][1] -= verts1[1]
        verts2[i][2] -= verts1[2]
    return verts2                                                                                                                                                                                                                         

def create_custom_mesh(objname, verts, faces, mat=None, cen=None):
    """
    @Param objname, name of new mesh
    @Param pos, object position [x, y, z]
    @Param vertex, corners
    @Param faces, buildorder
    """
    # Create mesh and object
    myobject, mymesh = init_object(objname)

    # Rearrange verts to put pivot point in center of mesh
    # Find center of verts
    center = get_mesh_center(verts)
    # Subtract center from verts before creation
    proper_verts = subtract_center_verts(center, verts)
    # Generate mesh data
    mymesh.from_pydata(proper_verts, [], faces)
    # Calculate the edges
    mymesh.update(calc_edges=True)

    parent_center = [0, 0, 0]
    if cen is not None:
        parent_center = [int(cen[0] / 2), int(cen[1] / 2), int(cen[2])]

    # Move object to input verts location
    myobject.location.x = center[0] - parent_center[0]
    myobject.location.y = center[1] - parent_center[1]
    myobject.location.z = center[2] - parent_center[2]

    # add material
    if mat is None:  # add random color
        myobject.data.materials.append(
            create_mat(1)
        )  # add the material to the object
    else:
        myobject.data.materials.append(mat)  # add the material to the object
    return myobject



def create_floorplan():
    """
    Get transform data
    """
    # read from file
#    transform = read_from_file(path_to_transform_file)
    
    params = json.loads("{\"id\":\"example\",\"polygons\":[[[771,326],[777,326],[777,371],[771,371]],[[901,327],[903,327],[903,389],[901,389]],[[973,367],[1066,367],[1066,373],[973,373]],[[540,236],[546,236],[546,304],[540,304]],[[216,296],[546,296],[546,304],[216,304]],[[1050,373],[1062,373],[1062,567],[1050,567]],[[241,541],[1062,541],[1062,567],[241,567]],[[771,371],[903,371],[903,389],[771,389]],[[86,254],[94,254],[94,550],[86,550]],[[86,550],[238,550],[238,558],[86,558]],[[86,254],[244,254],[244,262],[86,262]],[[235,71],[552,71],[552,97],[235,97]],[[217,80],[243,80],[243,262],[217,262]],[[862,94],[880,94],[880,225],[862,225]],[[659,74],[880,74],[880,94],[659,94]],[[1046,243],[1066,243],[1066,373],[1046,373]],[[862,225],[1066,225],[1066,243],[862,243]],[[659,94],[667,94],[667,237],[659,237]],[[557,74],[667,74],[667,94],[557,94]],[[534,77],[557,77],[557,91],[534,91]],[[534,97],[552,97],[552,236],[534,236]],[[216,262],[244,262],[244,296],[216,296]],[[659,237],[868,237],[868,245],[659,245]],[[534,236],[667,236],[667,246],[534,246]],[[222,296],[238,296],[238,549],[222,549]],[[222,549],[241,549],[241,559],[222,559]],[[858,328],[899,328],[899,366],[858,366]],[[499,256],[538,256],[538,296],[499,296]],[[853,501],[891,501],[891,539],[853,539]],[[779,96],[815,96],[815,123],[779,123]],[[1008,434],[1047,434],[1047,475],[1008,475]],[[858,387],[899,387],[899,426],[858,426]],[[777,327],[859,327],[859,366],[777,366]],[[731,96],[755,96],[755,138],[731,138]],[[1006,373],[1045,373],[1045,415],[1006,415]],[[892,500],[945,500],[945,538],[892,538]],[[818,386],[858,386],[858,426],[818,426]],[[499,94],[538,94],[538,256],[499,256]],[[821,152],[860,152],[860,193],[821,193]],[[973,341],[1046,341],[1046,367],[973,367]],[[434,296],[490,296],[490,304],[434,304]],[[668,541],[729,541],[729,567],[668,567]],[[304,541],[426,541],[426,567],[304,567]],[[485,541],[547,541],[547,567],[485,567]],[[871,541],[974,541],[974,567],[871,567]],[[257,71],[318,71],[318,97],[257,97]],[[217,168],[243,168],[243,229],[217,229]],[[1046,254],[1066,254],[1066,316],[1046,316]],[[757,237],[803,237],[803,245],[757,245]],[[573,236],[627,236],[627,246],[573,246]],[[222,313],[238,313],[238,373],[222,373]],[[222,398],[238,398],[238,459],[222,459]],[[222,460],[238,460],[238,520],[222,520]]],\"types\":[{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":8},{\"type\":\"wall\",\"class\":8},{\"type\":\"wall\",\"class\":8},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"wall\",\"class\":2},{\"type\":\"icon\",\"class\":3,\"prob\":0.9905971385089056},{\"type\":\"icon\",\"class\":3,\"prob\":0.9440514197716346},{\"type\":\"icon\",\"class\":4,\"prob\":0.9415205429795707},{\"type\":\"icon\",\"class\":6,\"prob\":0.997063907576196},{\"type\":\"icon\",\"class\":4,\"prob\":0.8775597358212164},{\"type\":\"icon\",\"class\":4,\"prob\":0.6754742038481082},{\"type\":\"icon\",\"class\":3,\"prob\":0.9572829484492261},{\"type\":\"icon\",\"class\":5,\"prob\":0.7095157683841766},{\"type\":\"icon\",\"class\":4,\"prob\":0.7037261105864622},{\"type\":\"icon\",\"class\":6,\"prob\":0.7949014491334099},{\"type\":\"icon\",\"class\":4,\"prob\":0.625892562866211},{\"type\":\"icon\",\"class\":3,\"prob\":0.6725881781220323},{\"type\":\"icon\",\"class\":3,\"prob\":0.4944140044803393},{\"type\":\"icon\",\"class\":3,\"prob\":0.8342650466774236},{\"type\":\"icon\",\"class\":2,\"prob\":0.7151030131748745},{\"type\":\"icon\",\"class\":1,\"prob\":0.9868075549978326},{\"type\":\"icon\",\"class\":1,\"prob\":0.8934914202888556},{\"type\":\"icon\",\"class\":1,\"prob\":0.9783558431393455},{\"type\":\"icon\",\"class\":1,\"prob\":0.8211293409260643},{\"type\":\"icon\",\"class\":1,\"prob\":0.8975295154624449},{\"type\":\"icon\",\"class\":1,\"prob\":0.8792983219873108},{\"type\":\"icon\",\"class\":2,\"prob\":0.5756427395728326},{\"type\":\"icon\",\"class\":2,\"prob\":0.5491943774016007},{\"type\":\"icon\",\"class\":2,\"prob\":0.6267389368127894},{\"type\":\"icon\",\"class\":2,\"prob\":0.838589604695638},{\"type\":\"icon\",\"class\":1,\"prob\":0.9044731640424885},{\"type\":\"icon\",\"class\":1,\"prob\":0.957708994547526}],\"room_polygons\":[{\"type\":\"Polygon\",\"coordinates\":[[[90.0,258.0],[90.0,300.0],[90.0,326.0],[90.0,327.0],[90.0,370.0],[90.0,380.0],[90.0,554.0],[230.0,554.0],[230.0,380.0],[230.0,370.0],[230.0,327.0],[230.0,326.0],[230.0,300.0],[230.0,258.0],[90.0,258.0]]]},{\"type\":\"Polygon\",\"coordinates\":[[[1056.0,370.0],[973.0,370.0],[902.0,370.0],[871.0,370.0],[868.0,370.0],[868.0,380.0],[774.0,380.0],[663.0,380.0],[663.0,554.0],[774.0,554.0],[868.0,554.0],[871.0,554.0],[902.0,554.0],[973.0,554.0],[1056.0,554.0],[1056.0,380.0],[1056.0,370.0]]]},{\"type\":\"Polygon\",\"coordinates\":[[[235.0,326.0],[230.0,326.0],[230.0,327.0],[230.0,370.0],[230.0,380.0],[230.0,554.0],[235.0,554.0],[241.0,554.0],[543.0,554.0],[543.0,380.0],[543.0,370.0],[241.0,370.0],[241.0,327.0],[241.0,326.0],[241.0,300.0],[235.0,300.0],[235.0,326.0]]]},{\"type\":\"Polygon\",\"coordinates\":[[[774.0,258.0],[774.0,241.0],[663.0,241.0],[557.0,241.0],[557.0,258.0],[663.0,258.0],[774.0,258.0]]]},{\"type\":\"Polygon\",\"coordinates\":[[[241.0,84.0],[241.0,234.0],[241.0,241.0],[241.0,258.0],[241.0,300.0],[543.0,300.0],[543.0,258.0],[543.0,241.0],[543.0,234.0],[543.0,84.0],[241.0,84.0]]]},{\"type\":\"Polygon\",\"coordinates\":[[[663.0,234.0],[663.0,241.0],[774.0,241.0],[868.0,241.0],[868.0,234.0],[868.0,84.0],[774.0,84.0],[663.0,84.0],[663.0,234.0]]]},{\"type\":\"Polygon\",\"coordinates\":[[[871.0,241.0],[868.0,241.0],[774.0,241.0],[774.0,258.0],[774.0,300.0],[774.0,326.0],[774.0,327.0],[774.0,370.0],[868.0,370.0],[871.0,370.0],[902.0,370.0],[973.0,370.0],[1056.0,370.0],[1056.0,327.0],[1056.0,326.0],[1056.0,300.0],[1056.0,258.0],[1056.0,241.0],[1056.0,234.0],[973.0,234.0],[902.0,234.0],[871.0,234.0],[871.0,241.0]]]},{\"type\":\"Polygon\",\"coordinates\":[[[543.0,258.0],[543.0,300.0],[241.0,300.0],[241.0,326.0],[241.0,327.0],[241.0,370.0],[543.0,370.0],[543.0,380.0],[543.0,554.0],[557.0,554.0],[663.0,554.0],[663.0,380.0],[774.0,380.0],[868.0,380.0],[868.0,370.0],[774.0,370.0],[774.0,327.0],[774.0,326.0],[774.0,300.0],[774.0,258.0],[663.0,258.0],[557.0,258.0],[557.0,241.0],[663.0,241.0],[663.0,234.0],[663.0,84.0],[557.0,84.0],[543.0,84.0],[543.0,234.0],[543.0,241.0],[543.0,258.0]]]},{\"type\":\"Polygon\",\"coordinates\":[[[230.0,326.0],[235.0,326.0],[235.0,300.0],[230.0,300.0],[230.0,326.0]]]},{\"type\":\"Polygon\",\"coordinates\":[[[868.0,241.0],[871.0,241.0],[871.0,234.0],[868.0,234.0],[868.0,241.0]]]}],\"room_types\":[{\"type\":\"room\",\"class\":1},{\"type\":\"room\",\"class\":3},{\"type\":\"room\",\"class\":4},{\"type\":\"room\",\"class\":4},{\"type\":\"room\",\"class\":5},{\"type\":\"room\",\"class\":6},{\"type\":\"room\",\"class\":7},{\"type\":\"room\",\"class\":11},{\"type\":\"room\",\"class\":11},{\"type\":\"room\",\"class\":11}]}")
    
    id, polygons, types, room_polygons, room_types = itemgetter('id', 'polygons', 'types', 'room_polygons', 'room_types')(params)
    
    parent, _ = init_object("Floorplan_" + str(id))
    # Set Cursor start
    bpy.context.scene.cursor.location = (0, 0, 0)
    
    # Parsed
    pixel_scale_factor = 100.
    wall_height = 2.5

    polygon_walls, type_walls, polygon_icons, type_icons = categorize_walls_icons(polygons, types)

    wall_horizontal_verts, wall_horizontal_faces, wall_vertical_verts, wall_vertical_faces = wall_2d_to_3d(polygon_walls, type_walls, wall_height, pixel_scale_factor)
    
    floors, ceilings = room_2d_to_3d(room_polygons, room_types, wall_height, pixel_scale_factor)
    
#    print(top_verts, top_faces, bottom_verts, bottom_faces)

    """
    Create Walls
    """

    # Wall settings
    cen = None
    wall_mat = create_mat((0.96, 0.96, 0.96, 1)) 
    wall_mat_trans = create_mat((0.96, 0.96, 0.96, 0))    
    
    # Vertical faces
    boxcount = 0
    wallcount = 0
    
    wall_parent, _ = init_object("Walls")
    
    faces = wall_vertical_faces
    verts = wall_vertical_verts
    
    for walls in verts:
        boxname = "Box_" + str(boxcount)
        for wall in walls:
            wallname = "Wall_Ver_" + str(wallcount)

            obj = create_custom_mesh(
                boxname + "_" + wallname,
                wall,
                faces,
                cen=cen,
                mat=wall_mat
            )
            obj.parent = wall_parent

            wallcount += 1
        boxcount += 1


    # Horizontal faces
    faces = wall_horizontal_faces
    verts = wall_horizontal_verts

    # Create mesh from data
    boxcount = 0
    wallcount = 0

    for i in range(0, len(verts)):
        roomname = "Walls_Hor_" + str(i)
        obj = create_custom_mesh(
            roomname,
            verts[i],
            faces[i],
            cen=cen,
            mat=wall_mat
        )
        obj.parent = wall_parent

    wall_parent.parent = parent
    
    # Rooms
    room_parent, _ = init_object("Rooms")
    
    for i in range(len(floors)):
        floor = floors[i]
        ceiling = ceilings[i]
        label = floor["label"]
        
        roomname = "Room_" + str(i) + "_" + label
        obj = create_custom_mesh(
            roomname,
            floor["verts"],
            floor["faces"],
            cen=cen,
            mat=wall_mat
        )
        obj.parent = room_parent
        
        roomname = "RoomCeiling_" + str(i) + "_" + label
        obj2 = create_custom_mesh(
            roomname,
            ceiling["verts"],
            ceiling["faces"],
            cen=cen,
            mat=wall_mat
        )
        obj2.parent = room_parent

    room_parent.parent = parent


def main(argv):

    # Remove starting object cube
    objs = bpy.data.objects
    
    if "Cube" in objs:
        objs.remove(objs["Cube"], do_unlink=True)
    
    """
    Instantiate
    Each argument after 7 will be a floorplan path
    """
    params = create_floorplan()
    
#    bpy.ops.wm.save_as_mainfile(filepath="%s/%s.blend" %("C:/Users/JackChua/Projects/Floorplan/CubiCasa5k/data/output/example/", params["id"]))    
    

main(['0'])