from ....plots import PdosPlot
from ..drawer import MatplotlibDrawer

class MatplotlibPDOSDrawer(MatplotlibDrawer):

    _ax_defaults = {
        'xlabel': 'Density of states [1/eV]',
        'ylabel': 'Energy [eV]'
    }

    def draw_PDOS_lines(self, drawer_info):
        
        lines = drawer_info["PDOS_values"]
        Es = drawer_info["Es"]
        min_PDOS = 0
        max_PDOS = 0

        for name, values in lines.items():
            self.draw_PDOS_line(values, Es, drawer_info["request_metadata"][name], name)
            
            min_PDOS = min(min_PDOS, min(values))
            max_PDOS = max(max_PDOS, max(values))

        self.ax.set_xlim(min_PDOS, max_PDOS)
        self.ax.set_ylim(min(Es), max(Es))
 
    def draw_PDOS_line(self, Es, values, request_metadata, name):

        line_style = request_metadata["style"]["line"]

        self.ax.plot(
            Es, values, color=line_style["color"], linewidth=line_style["width"], label=name
        )

PdosPlot._drawers.register("matplotlib", MatplotlibPDOSDrawer)
    