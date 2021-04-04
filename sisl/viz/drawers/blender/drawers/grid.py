import bpy

from ....plots import GridPlot
from ..drawer import BlenderDrawer


class BlenderGridDrawer(BlenderDrawer):

    def draw_1D(self, drawer_info, **kwargs):
        raise NotImplementedError("A way of drawing 1D grid representations is not implemented for blender")

    def draw_1D(self, drawer_info, **kwargs):
        raise NotImplementedError("A way of drawing 2D grid representations is not implemented for blender")

    def draw_3D(self, drawer_info, **kwargs):

        for isosurf in drawer_info["isosurfaces"]:

            x, y, z = isosurf["vertices"].T
            I, J, K = isosurf["faces"].T

            mesh = bpy.data.meshes.new(isosurf["name"])

            obj = bpy.data.objects.new(mesh.name, mesh)

            col = bpy.data.collections.get("Grids")

            if col is None:
                col = bpy.data.collections.new("Grids")
                bpy.context.scene.collection.children.link(col)

            col.objects.link(obj)
            bpy.context.view_layer.objects.active = obj

            edges = []
            mesh.from_pydata(isosurf["vertices"], edges, isosurf["faces"].tolist())

            mat = bpy.data.materials.new("material")
            mat.use_nodes = True

            color = isosurf["color"]
            if color is not None:
                mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*isosurf["color"], 1)

            mat.node_tree.nodes["Principled BSDF"].inputs[19].default_value = isosurf["opacity"]

            mesh.materials.append(mat)

GridPlot._drawers.register("blender", BlenderGridDrawer)
