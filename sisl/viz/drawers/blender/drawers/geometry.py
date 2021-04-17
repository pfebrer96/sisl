import bpy

from ....plots import GeometryPlot
from ..drawer import BlenderDrawer


class BlenderGeometryDrawer(BlenderDrawer):

    def draw_1D(self, drawer_info, **kwargs):
        raise NotImplementedError("A way of drawing 1D geometry representations is not implemented for blender")

    def draw_1D(self, drawer_info, **kwargs):
        raise NotImplementedError("A way of drawing 2D geometry representations is not implemented for blender")

    def draw_3D(self, drawer_info, **kwargs):

        # For now, draw only the atoms
        for atom_props in drawer_info["atoms_props"]:
            self._plot_3D_atom(**atom_props)

    def _plot_3D_atom(self, xyz, r, color="gray", name=None, vertices=15, **kwargs):

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=vertices, ring_count=vertices,
            align='WORLD', enter_editmode=False,
            location=xyz, radius=size
        )

        atom = bpy.context.selected_objects[0]

        color = self._to_rgb_color(color)

        if color is not None:
            mat = bpy.data.materials.new("material")
            mat.use_nodes = True

            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*color, 1)

            atom.active_material = mat

        bpy.ops.object.shade_smooth()

GeometryPlot._drawers.register("blender", BlenderGeometryDrawer)
