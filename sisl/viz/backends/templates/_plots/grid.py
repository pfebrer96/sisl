from ..backend import Backend

from ....plots.grid import GridPlot

class GridBackend(Backend):

    def draw(self, backend_info):
        # Choose which function we need to use to plot
        drawing_func = getattr(self, f"draw_{backend_info['ndim']}D")

        drawing_func(backend_info)
    
    def draw_1D(self, backend_info, **kwargs):
        """Draws the grid in 1D"""
        self.draw_line(backend_info["ax_range"], backend_info["values"], name=backend_info["name"], **kwargs)

    def draw_2D(self, backend_info, **kwargs):
        """Should draw the grid in 2D, and draw contours if requested."""
        raise NotImplementedError(f"{self.__class__.__name__} does not implement displaying grids in 2D")

    def draw_3D(self, backend_info, **kwargs):
        """Should draw all the isosurfaces of the grid in 3D"""
        raise NotImplementedError(f"{self.__class__.__name__} does not implement displaying grids in 3D")

GridPlot._backends.register_template(GridBackend)