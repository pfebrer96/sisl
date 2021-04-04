import bpy

from .._plot_drawers import Drawer
from ...plot import SubPlots, MultiplePlot, Animation


class BlenderDrawer(Drawer):

    def clear(self):
        """ Clears the blender scene so that data can be reset

        Parameters
        --------
        """
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False, confirm=False)

        return self


class BlenderMultiplePlotDrawer(BlenderDrawer):

    def draw(self, drawer_info, childs):
        # Start assigning each plot to a position of the layout
        for child in childs:
            self._draw_child_in_scene(child)

    def _draw_child_in_ax(self, child):
        child.get_figure(clear_fig=False)

MultiplePlot._drawers.register("blender", BlenderMultiplePlotDrawer)
