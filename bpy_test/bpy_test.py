import bpy
import numpy as np
import json
import sys
import math
import os.path
from operator import itemgetter


def init_object(name):
    # Create new blender object and return references to mesh and object
    mymesh = bpy.data.meshes.new(name)
    myobject = bpy.data.objects.new(name, mymesh)
    bpy.context.collection.objects.link(myobject)
    return myobject, mymesh

# Create mesh and object
myobject, mymesh = init_object("Example")


verts = [[7.26, 5.37, 1], [8.74, 5.71, 1], [7.26, 5.71, 1], [8.74, 5.37, 1]]
faces = [[0, 1, 2, 3]]

# Generate mesh data
mymesh.from_pydata(verts, [], faces)