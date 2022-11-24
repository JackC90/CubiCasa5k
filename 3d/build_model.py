from pygltflib import GLTF2, Scene

def create_3d_floor(polygons, types, room_polygons, room_types):
    gltf = GLTF2()
    scene = Scene()