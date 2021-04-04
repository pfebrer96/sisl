import plotly.graph_objects as go

from ....plots import GridPlot
from ..drawer import PlotlyDrawer


class PlotlyGridDrawer(PlotlyDrawer):

    def draw_1D(self, drawer_info, **kwargs):

        self.add_trace({
            'type': 'scatter',
            'mode': 'lines',
            'y': drawer_info["values"],
            'x': drawer_info["ax_range"],
            'name': drawer_info["name"],
            **kwargs
        })

        axes_titles = {'xaxis_title': f'{("X","Y", "Z")[drawer_info["ax"]]} axis [Ang]', 'yaxis_title': 'Values'}

        self.update_layout(**axes_titles)

    def draw_2D(self, drawer_info, **kwargs):

        # Draw the heatmap
        self.add_trace({
            'type': 'heatmap',
            'name': drawer_info["name"],
            'z': drawer_info["values"],
            'x': drawer_info["x"],
            'y': drawer_info["y"],
            'zsmooth': drawer_info["zsmooth"],
            'zmin': drawer_info["cmin"],
            'zmax': drawer_info["cmax"],
            'zmid': drawer_info["cmid"],
            'colorscale': drawer_info["colorscale"],
            **kwargs
        })

        # Draw the isocontours
        for contour in drawer_info["contours"]:
            self.add_scatter(
                x=contour["x"], y=contour["y"],
                marker_color=contour["color"], line_color=contour["color"],
                opacity=contour["opacity"],
                name=contour["name"]
            )

        axes_titles = {f'{ax}_title': f'{("X","Y", "Z")[drawer_info[ax]]} axis [Ang]' for ax in ("xaxis", "yaxis")}

        self.update_layout(**axes_titles)

        self.figure.layout.yaxis.scaleanchor = "x"
        self.figure.layout.yaxis.scaleratio = 1

    def draw_3D(self, drawer_info, **kwargs):

        for isosurf in drawer_info["isosurfaces"]:

            x, y, z = isosurf["vertices"].T
            I, J, K = isosurf["faces"].T

            self.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=I, j=J, k=K,
                color=isosurf["color"],
                opacity=isosurf["opacity"],
                name=isosurf["name"],
                **kwargs
            ))

        self.layout.scene = {'aspectmode': 'data'}

    def _after_get_figure(self):
        self.update_layout(legend_orientation='h')

GridPlot._drawers.register("plotly", PlotlyGridDrawer)

# def _plot_2D_carpet(self, grid, values, xaxis, yaxis):
#     """
#     CURRENTLY NOT USED, but kept here just in case it is needed in the future

#     It was supposed to display skewed grids in 2D, but it has some limitations
#     (see https://github.com/zerothi/sisl/pull/268#issuecomment-702758586). In these cases,
#     the grid is first transformed to cartesian coordinates and then plotted in a regular map
#     instead of using the Carpet trace.
#     """

#     minval, maxval = values.min(), values.max()

#     values = values.T

#     x, y = np.mgrid[:values.shape[0], :values.shape[1]]
#     x, y = x * grid.dcell[xaxis, xaxis] + y * grid.dcell[yaxis, xaxis], x * grid.dcell[xaxis, yaxis] + y * grid.dcell[yaxis, yaxis]

#     self.figure.add_trace(go.Contourcarpet(
#         z = values,
#         contours = dict(
#             start = minval,
#             end = maxval,
#             size = (maxval - minval) / 40,
#             showlines=False
#         ),
#     ))

#     self.figure.add_trace(go.Carpet(
#         a = np.arange(values.shape[1]),
#         b = np.arange(values.shape[0]),
#         x = x,
#         y = y,
#         aaxis = dict(
#             showgrid=False,
#             showline=False,
#             showticklabels="none"
#         ),
#         baxis = dict(
#             showgrid=False,
#             showline=False,
#             showticklabels="none"
#         ),
#     ))
