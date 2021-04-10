from ....plots import FatbandsPlot
from .bands import PlotlyBandsDrawer


class PlotlyFatbandsDrawer(PlotlyBandsDrawer):

    def draw(self, drawer_info):

        groups_weights = drawer_info["groups_weights"]
        groups_metadata = drawer_info["groups_metadata"]
        existing_bands = drawer_info["draw_bands"][0]

        # We are going to need a trace that goes forward and then back so that
        # it is self-fillable
        xs = existing_bands.k.values
        area_xs = [*xs, *reversed(xs)]

        for group_name in groups_weights:
            self.draw_group_weights(
                weights=groups_weights[group_name], metadata=groups_metadata[group_name],
                name=group_name, bands=existing_bands, area_xs=area_xs
            )

        # Avoid bands being displayed in the legend individually (it would be a mess)
        drawer_info["draw_bands"][-1] = lambda band, plot: {'showlegend': False}

        self.draw_bands(*drawer_info["draw_bands"])

    def draw_group_weights(self, weights, metadata, name, bands, area_xs):

        fatband_traces = []
        for ispin, spin_weights in enumerate(weights):
            for i, band_weights in enumerate(spin_weights):

                band_values = bands.sel(band=band_weights.band, spin=band_weights.spin)

                fatband_traces.append({
                    "type": "scatter",
                    "mode": "lines",
                    "x": area_xs,
                    "y": [*(band_values + band_weights), *reversed(band_values - band_weights)],
                    "line": {"width": 0, "color": metadata["style"]["line"]["color"]},
                    "showlegend": i == 0,
                    "name": name,
                    "legendgroup": name,
                    "fill": "toself"
                })

        self.add_traces(fatband_traces)

FatbandsPlot._drawers.register("plotly", PlotlyFatbandsDrawer)
