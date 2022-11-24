from subprocess import check_output
import numpy as np
import json
import os
from operator import attrgetter

def _convert_np_float(val):
    if isinstance(val, np.floating) or isinstance(val, np.integer):
        return val.item()
    return val


def polygons_to_json(id, polygons, types, room_polygons, room_types):
    """
    Transform polygons to JSON
    """

    dictionary = {
      "id": id,
      "polygons": polygons.tolist(),
      "types": types,
      "room_polygons": list(map(lambda p : p.__geo_interface__, room_polygons)),
      "room_types": room_types
    }

    str = json.dumps(dictionary, separators=(',', ':'), default=_convert_np_float)
    return str


def generate_3d(path, id, polygons, types, room_polygons, room_types):
    polygon_dict_str = polygons_to_json(id, polygons, types, room_polygons, room_types)

    check_output(
      [
        os.environ["BLENDER_PATH"],
        "-noaudio",
        "--background",
        "--python",
        "./blender_generate_3d.py",
        polygon_dict_str,
        path
      ]
    )