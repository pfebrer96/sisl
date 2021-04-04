import numpy as np

from ....plots import PdosPlot
from ..drawer import PlotlyDrawer


class PlotlyPDOSDrawer(PlotlyDrawer):

    _layout_defaults = {
        'xaxis_title': 'Density of states [1/eV]',
        'xaxis_mirror': True,
        'yaxis_mirror': True,
        'yaxis_title': 'Energy [eV]',
        'showlegend': True
    }

    def draw_PDOS_lines(self, drawer_info):

        lines = drawer_info["PDOS_values"]
        Es = drawer_info["Es"]

        for name, values in lines.items():
            self.draw_PDOS_line(Es, values, drawer_info["request_metadata"][name], name)

        self.update_layout(yaxis_range=[min(Es), max(Es)])

    def draw_PDOS_line(self, Es, values, request_metadata, name):

        line_style = request_metadata["style"]["line"]

        self.add_trace({
            'type': 'scatter',
            'x': values,
            'y': Es,
            'mode': 'lines',
            'name': name,
            'line': line_style,
            "hoverinfo": "name",
        })


PdosPlot._drawers.register("plotly", PlotlyPDOSDrawer)
