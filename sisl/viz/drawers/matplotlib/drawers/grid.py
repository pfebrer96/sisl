import matplotlib.pyplot as plt
import numpy as np

from ....plots import GridPlot
from ..drawer import MatplotlibDrawer


class MatplotlibGridDrawer(MatplotlibDrawer):

    def draw_1D(self, drawer_info, **kwargs):

        self.ax.plot(drawer_info["ax_range"], drawer_info["values"], label=drawer_info["name"], **kwargs)

        self.ax.set_xlabel(f'{("X","Y", "Z")[drawer_info["ax"]]} axis [Ang]')
        self.ax.set_ylabel('Values')

    def draw_2D(self, drawer_info, **kwargs):

        # Define the axes values
        x = drawer_info["x"]
        y = drawer_info["y"]

        extent = [x[0], x[-1], y[0], y[-1]]

        # Draw the values of the grid
        self.ax.imshow(
            drawer_info["values"], vmin=drawer_info["cmin"], vmax=drawer_info["cmax"],
            label=drawer_info["name"], cmap=drawer_info["colorscale"], extent=extent,
            origin="lower"
        )

        # Draw the isocontours
        for contour in drawer_info["contours"]:
            self.ax.plot(
                contour["x"], contour["y"],
                color=contour["color"],
                alpha=contour["opacity"],
                label=contour["name"]
            )

        self.ax.set_xlabel(f'{("X","Y", "Z")[drawer_info["xaxis"]]} axis [Ang]')
        self.ax.set_ylabel(f'{("X","Y", "Z")[drawer_info["yaxis"]]} axis [Ang]')

    def draw_3D(self, drawer_info, **kwargs):

        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(projection="3d")

        for isosurf in drawer_info["isosurfaces"]:

            x, y, z = isosurf["vertices"].T
            I, J, K = isosurf["faces"].T

            self.ax.plot_trisurf(x, y, z, linewidth=0, antialiased=True)

GridPlot._drawers.register("matplotlib", MatplotlibGridDrawer)
