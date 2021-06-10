"""
======================================================================
Fury Markers
======================================================================

This it's a example which shows how to use the marker actor.
"""
import numpy as np
import vtk
import vtk.util.numpy_support as vtknp
from fury import actor, window, colormap as cmap
n = 10000

"""
The are nine types 2d markers: circle, square, diamond,
triangle, pentagon, hexagon, heptagon, cross and plus.
"""
marker_symbols = ['o', 's', 'd', '^', 'p', 'h', 's6', 'x', '+']
markers = [
    np.random.choice(marker_symbols)
    for i in range(n)]

centers = np.random.normal(size=(n, 3), scale=10)

colors = np.random.uniform(size=(n, 3))
# In addition, as similar to networkx,  you can control the
# edge color and edge width for each marker
nodes_actor = actor.markers(
    centers,
    marker=markers,
    edge_width=.1,
    edge_color=[255, 255, 0],
    colors=colors,
    scales=.5,
)
# In addtion, the 3d impostor sphere it's also a valid type of marker
nodes_3d_actor = actor.markers(
    centers+np.ones_like(centers)*25,
    marker='3d',
    colors=colors,
    scales=.5,
)

scene = window.Scene()

scene.add(nodes_actor)
scene.add(nodes_3d_actor)

interactive = True

if interactive:
    window.show(scene, size=(600, 600))
