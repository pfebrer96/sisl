from collections.abc import Iterable
import numpy as np
from itertools import repeat

from ....plots import GeometryPlot
from ..drawer import PlotlyDrawer


class PlotlyGeometryDrawer(PlotlyDrawer):

    def draw_1D(self, drawer_info, **kwargs):

        geometry = drawer_info["geometry"]
        xaxis = drawer_info["xaxis"]
        yaxis = drawer_info["yaxis"]

        # Add the atoms trace
        self.add_traces(self._atoms_2D_scatter(**drawer_info["atoms_props"]))

        self.update_layout(xaxis_title=f'{("X","Y","Z")[xaxis]} axis [Ang]', yaxis_title=yaxis)

    def draw_2D(self, drawer_info, **kwargs):
        geometry = drawer_info["geometry"]
        xaxis = drawer_info["xaxis"]
        yaxis = drawer_info["yaxis"]
        bonds_props = drawer_info["bonds_props"]

        traces = []

        # If there are bonds to draw, draw them
        if len(bonds_props) > 0:
            bonds_kwargs = {}
            for k in bonds_props[0]:
                if k == "xys":
                    new_k = k
                else:
                    new_k = f"bonds_{k}"
                bonds_kwargs[new_k] = [x[k] for x in bonds_props]

            traces.append(self._bonds_2D_scatter(**bonds_kwargs, points_per_bond=drawer_info["points_per_bond"]))

        # Add the atoms trace
        traces.append(self._atoms_2D_scatter(**drawer_info["atoms_props"]))

        # And finally draw the unit cell
        show_cell = drawer_info["show_cell"]
        cell = geometry.cell
        if show_cell == "axes":
            traces.extend(
                self._cell_2D_axes_traces(geometry=geometry, cell=cell, xaxis=xaxis, yaxis=yaxis)
            )
        elif show_cell == "box":
            traces.append(
                self._cell_2D_box_trace(
                    geometry=geometry, cell=cell,
                    xaxis=xaxis, yaxis=yaxis
                    )
            )

        self.add_traces(traces)

        axes_titles = {f'{ax}_title': f'{("X","Y","Z")[drawer_info[ax]]} axis [Ang]' for ax in ("xaxis", "yaxis")}

        self.update_layout(**axes_titles)

        self.layout.yaxis.scaleanchor = "x"
        self.layout.yaxis.scaleratio = 1

    def _atoms_2D_scatter(self, xy, xaxis="x", yaxis="y", color="gray", size=10, name='atoms', text=None, group=None, showlegend=True, **kwargs):
        trace = {
            "type": "scatter",
            'mode': 'markers',
            'name': name,
            'x': xy[0],
            'y': xy[1],
            'marker': {'size': size, 'color': color},
            'text': text,
            'legendgroup': group,
            'showlegend': showlegend,
            **kwargs
        }

        return trace

    def _bonds_2D_scatter(self, xys, points_per_bond=5, force_bonds_as_points=False,
        bonds_color='#ccc', bonds_size=3, bonds_text=None,
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

            mode = 'markers+lines'

        else:
            # Otherwise we will need to draw points in between atoms
            # representing the bonds
            for i, ((x1, y1), (x2, y2)) in enumerate(xys):

                x = [*x, *np.linspace(x1, x2, points_per_bond)]
                y = [*y, *np.linspace(y1, y2, points_per_bond)]

            mode = 'markers'
            if bonds_text:
                text = np.repeat(bonds_text, points_per_bond)

        trace = {
            'type': 'scatter',
            'mode': mode,
            'name': name,
            'x': x, 'y': y,
            'marker': {'color': bonds_color, 'size': bonds_size, 'coloraxis': coloraxis},
            'text': text if len(text) != 0 else None,
            'hoverinfo': 'text',
            'legendgroup': group,
            'showlegend': showlegend,
            **kwargs
        }

        return trace

    def _bond_2D_trace(self, xys, width=2, color="#ccc", name=None, group=None, showlegend=False, **kwargs):
        """
        Returns a bond trace in 2d.
        """
        x, y = np.array(xys).T

        trace = {
            "type": "scatter",
            'mode': 'lines',
            'name': name,
            'x': x,
            'y': y,
            'line': {'width': width, 'color': color},
            'legendgroup': group,
            'showlegend': showlegend,
            **kwargs
        }

        return trace

    def _cell_2D_axes_traces(self, geometry, cell, xaxis="x", yaxis="y"):
        cell_xy = GeometryPlot._projected_2Dcoords(geometry, xyz=cell, xaxis=xaxis, yaxis=yaxis).T

        return [{
            'type': 'scatter',
            'mode': 'markers+lines',
            'x': [0, vec[0]],
            'y': [0, vec[1]],
            'name': f'Axis {i}'
        } for i, vec in enumerate(cell_xy)]

    def _cell_2D_box_trace(self, cell, geometry, xaxis="x", yaxis="y", color=None, filled=False, **kwargs):

        cell_corners = GeometryPlot._get_cell_corners(cell)
        x, y = GeometryPlot._projected_2Dcoords(geometry, xyz=cell_corners, xaxis=xaxis, yaxis=yaxis)

        return {
            'type': 'scatter',
            'mode': 'lines',
            'name': 'Unit cell',
            'x': x,
            'y': y,
            'line': {'color': color},
            'fill': 'toself' if filled else None,
            **kwargs
        }

    def draw_3D(self, drawer_info):

        geometry = drawer_info["geometry"]
        bonds_props = drawer_info["bonds_props"]

        # If there are bonds to draw, draw them
        if len(bonds_props) > 0:
            # Unless we have different bond sizes, we want to plot all bonds in the same trace
            different_bond_sizes = False
            if "size" in bonds_props[0]:
                first_size = bonds_props[0].get("size")
                for bond_prop in bonds_props:
                    if bond_prop.get("size") != first_size:
                        different_bond_sizes = True
                        break

            if different_bond_sizes:
                for bond_props in drawer_info["bonds_props"]:
                    self.add_trace(
                        self._bond_3D_trace(**bond_props)
                    )
            else:
                bonds_kwargs = {}
                for k in bonds_props[0]:
                    if k == "r":
                        v = bonds_props[0][k]
                    else:
                        v = [x[k] for x in bonds_props]
                    bonds_kwargs[f"bonds_{k}"] = v

                self._bonds_3D_scatter(drawer_info["bonds"], **bonds_kwargs)

        # Now draw the atoms
        for atom_props in drawer_info["atoms_props"]:
            self.add_trace(self._atom_3D_trace(**atom_props))

        # And finally draw the unit cell
        show_cell = drawer_info["show_cell"]
        cell = geometry.cell
        if show_cell == "axes":
            self.add_traces(self._cell_3D_axes_traces(cell=cell))
        elif show_cell == "box":
            self.add_trace(self._cell_3D_box_trace(cell=cell))

        self.layout.scene.aspectmode = 'data'

    def _bonds_3D_scatter(self, bonds, bonds_xyz1, bonds_xyz2, bonds_r=10, bonds_color='gray', bonds_labels=None,
        atoms=False, atoms_color="blue", atoms_size=None, name=None, coloraxis='coloraxis', legendgroup=None, **kwargs):
        """
        This method is capable of plotting all the geometry in one 3d trace.

        Parameters
        ----------

        Returns
        ----------
        tuple.
            If bonds_labels are provided, it returns (trace, labels_trace).
            Otherwise, just (trace,)
        """
        # If only bonds are in this trace, we will name it "bonds".
        if not name:
            name = 'Bonds and atoms' if atoms else 'Bonds'

        # Check if we need to build the markers_properties from atoms_* arguments
        if atoms and isinstance(atoms_color, Iterable) and not isinstance(atoms_color, str):
            build_marker_color = True
            atoms_color = np.array(atoms_color)
            marker_color = []
        else:
            build_marker_color = False
            marker_color = atoms_color

        if atoms and isinstance(atoms_size, Iterable):
            build_marker_size = True
            atoms_size = np.array(atoms_size)
            marker_size = []
        else:
            build_marker_size = False
            marker_size = atoms_size

        # Bond color
        if isinstance(bonds_color, Iterable) and not isinstance(bonds_color, str):
            build_line_color = True
            bonds_color = np.array(bonds_color)
            line_color = []
        else:
            build_line_color = False
            line_color = bonds_color

        x = []; y = []; z = []

        for i, bond in enumerate(bonds):

            x = [*x, bonds_xyz1[i][0], bonds_xyz2[i][0], None]
            y = [*y, bonds_xyz1[i][1], bonds_xyz2[i][1], None]
            z = [*z, bonds_xyz1[i][2], bonds_xyz2[i][2], None]

            if build_marker_color:
                marker_color = [*marker_color, *atoms_color[bond], "white"]
            if build_marker_size:
                marker_size = [*marker_size, *atoms_size[bond], 0]
            if build_line_color:
                line_color = [*line_color, bonds_color[i], bonds_color[i], 0]

        if bonds_labels:

            x_labels, y_labels, z_labels = np.array([geom_xyz[bond].mean(axis=0) for bond in bonds]).T
            labels_trace = {
                'type': 'scatter3d', 'mode': 'markers',
                'x': x_labels, 'y': y_labels, 'z': z_labels,
                'text': bonds_labels, 'hoverinfo': 'text',
                'marker': {'size': bonds_r*3, "color": "rgba(255,255,255,0)"},
                "showlegend": False
            }

        trace = {
            'type': 'scatter3d',
            'mode': f'lines{"+markers" if atoms else ""}',
            'name': name,
            'x': x,
            'y': y,
            'z': z,
            'line': {'width': bonds_r, 'color': line_color, 'coloraxis': coloraxis},
            'marker': {'size': marker_size, 'color': marker_color},
            'legendgroup': legendgroup,
            'showlegend': True,
            **kwargs
        }

        self.add_traces((trace, labels_trace) if bonds_labels else (trace,))

    def _atom_3D_trace(self, xyz, size, color="gray", name=None, group=None, showlegend=False, vertices=15, **kwargs):

        trace = {
            'type': 'mesh3d',
            **{key: np.ravel(val) for key, val in GeometryPlot._sphere(xyz, size, vertices=vertices).items()},
            'showlegend': showlegend,
            'alphahull': 0,
            'color': color,
            'showscale': False,
            'legendgroup': group,
            'name': name,
            'meta': ['({:.2f}, {:.2f}, {:.2f})'.format(*xyz)],
            'hovertemplate': '%{meta[0]}',
            **kwargs
        }

        return trace

    def _bond_3D_trace(self, xyz1, xyz2, size=0.3, color="#ccc", name=None, group=None, showlegend=False, line_kwargs={}, **kwargs):

        # Drawing cylinders instead of lines would be better, but rendering would be slower
        # We need to give the possibility.
        # Also, the fastest way to draw bonds would be a single scatter trace with just markers
        # (bonds would be drawn as sequences of points, but rendering would be much faster)

        x, y, z = np.array([xyz1, xyz2]).T

        trace = {
            'type': 'scatter3d',
            'mode': 'lines',
            'name': name,
            'x': x,
            'y': y,
            'z': z,
            'line': {'width': size, 'color': color, **line_kwargs},
            'legendgroup': group,
            'showlegend': showlegend,
            **kwargs
        }

        return trace

    def _cell_3D_axes_traces(self, cell):

        return [{
            'type': 'scatter3d',
            'x': [0, vec[0]],
            'y': [0, vec[1]],
            'z': [0, vec[2]],
            'name': f'Axis {i}'
        } for i, vec in enumerate(cell)]

    def _cell_3D_box_trace(self, cell, color=None, width=2, **kwargs):

        x, y, z = GeometryPlot._get_cell_corners(cell).T

        return {
            'type': 'scatter3d',
            'mode': 'lines',
            'name': 'Unit cell',
            'x': x,
            'y': y,
            'z': z,
            'line': {'color': color, 'width': width},
            **kwargs
        }

GeometryPlot._drawers.register("plotly", PlotlyGeometryDrawer)
