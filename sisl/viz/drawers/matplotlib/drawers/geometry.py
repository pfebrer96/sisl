from collections.abc import Iterable
import numpy as np
from itertools import repeat

from ....plots import GeometryPlot
from ..drawer import MatplotlibDrawer


class MatplotlibGeometryDrawer(MatplotlibDrawer):

    def draw_1D(self, drawer_info, **kwargs):

        geometry = drawer_info["geometry"]
        xaxis = drawer_info["xaxis"]
        yaxis = drawer_info["yaxis"]

        # Add the atoms trace
        self._plot_atoms_2D(**drawer_info["atoms_props"])

        self.ax.set_xlabel(f'{("X","Y","Z")[xaxis]} axis [Ang]')
        self.ax.set_ylabel(yaxis)

    def draw_2D(self, drawer_info, **kwargs):
        geometry = drawer_info["geometry"]
        xaxis = drawer_info["xaxis"]
        yaxis = drawer_info["yaxis"]
        bonds_props = drawer_info["bonds_props"]

        # If there are bonds to draw, draw them
        if len(bonds_props) > 0:
            bonds_kwargs = {}
            for k in bonds_props[0]:
                if k == "xys":
                    new_k = k
                else:
                    new_k = f"bonds_{k}"
                bonds_kwargs[new_k] = [x[k] for x in bonds_props]

            self._plot_bonds_2D(**bonds_kwargs, points_per_bond=drawer_info["points_per_bond"])

        # Add the atoms trace
        self._plot_atoms_2D(**drawer_info["atoms_props"])

        # And finally draw the unit cell
        show_cell = drawer_info["show_cell"]
        cell = geometry.cell
        if show_cell == "axes":
            self._plot_cell_axes_2D(geometry=geometry, cell=cell, xaxis=xaxis, yaxis=yaxis)
        elif show_cell == "box":
            self._plot_cell_box_2D(
                geometry=geometry, cell=cell,
                xaxis=xaxis, yaxis=yaxis
            )

        self.ax.set_xlabel(f'{("X","Y", "Z")[drawer_info["xaxis"]]} axis [Ang]')
        self.ax.set_ylabel(f'{("X","Y", "Z")[drawer_info["yaxis"]]} axis [Ang]')
        self.ax.axis("equal")

    def _plot_atoms_2D(self, xy, xaxis="x", yaxis="y", color="gray", size=10, name='atoms', text=None, group=None, showlegend=True, **kwargs):
        self.ax.scatter(xy[0], xy[1], s=size, color=color, label=name)

    def _plot_bonds_2D(self, xys, points_per_bond=5, force_bonds_as_points=False,
        bonds_color='gray', bonds_size=3, bonds_text=None,
        coloraxis="coloraxis", name='bonds', group=None, showlegend=True, **kwargs):
        """
        Cheaper than _bond_trace2D because it draws all bonds in a single trace.

        It is also more flexible, since it allows providing bond colors as floats that all
        relate to the same colorscale.

        However, the bonds are represented as dots between the two atoms (if you use enough
        points per bond it almost looks like a line).
        """
        # Check if we need to build the markers_properties from atoms_* arguments
        if isinstance(bonds_color, Iterable) and not isinstance(bonds_color, str):
            bonds_color = np.repeat(bonds_color, points_per_bond)
            single_color = False
        else:
            single_color = True

        if isinstance(bonds_size, Iterable):
            bonds_size = np.repeat(bonds_size, points_per_bond)
            single_size = False
        else:
            single_size = True

        x = []
        y = []
        text = []
        if single_color and single_size and not force_bonds_as_points:
            # Then we can display this trace as lines! :)
            for i, ((x1, y1), (x2, y2)) in enumerate(xys):

                x = [*x, x1, x2, None]
                y = [*y, y1, y2, None]

                if bonds_text:
                    text = np.repeat(bonds_text, 3)

            fmt = '.-'

        else:
            # Otherwise we will need to draw points in between atoms
            # representing the bonds
            for i, ((x1, y1), (x2, y2)) in enumerate(xys):

                x = [*x, *np.linspace(x1, x2, points_per_bond)]
                y = [*y, *np.linspace(y1, y2, points_per_bond)]

            fmt = 'o'
            if bonds_text:
                text = np.repeat(bonds_text, points_per_bond)

        self.ax.plot(x, y, fmt, label=name, color=bonds_color, markersize=bonds_size, linewidth=bonds_size)

    def _plot_cell_axes_2D(self, geometry, cell, xaxis="x", yaxis="y"):
        cell_xy = GeometryPlot._projected_2Dcoords(geometry, xyz=cell, xaxis=xaxis, yaxis=yaxis).T

        for i, vec in enumerate(cell_xy):
            self.ax.plot([0, vec[0]], [0, vec[1]], 'o-', label=f'Axis {i}')

    def _plot_cell_box_2D(self, cell, geometry, xaxis="x", yaxis="y", color=None, filled=False, **kwargs):
        cell_corners = GeometryPlot._get_cell_corners(cell)
        x, y = GeometryPlot._projected_2Dcoords(geometry, xyz=cell_corners, xaxis=xaxis, yaxis=yaxis)

        self.ax.plot(x, y, color=color, label="Unit cell")

    def draw_3D(self, drawer_info):
        return NotImplementedError(f"3D geometry plots are not implemented by {self.__class__.__name__}")

GeometryPlot._drawers.register("matplotlib", MatplotlibGeometryDrawer)
