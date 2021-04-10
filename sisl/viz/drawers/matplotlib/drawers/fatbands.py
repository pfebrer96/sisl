from ....plots import FatbandsPlot
from .bands import MatplotlibBandsDrawer


class MatplotlibFatbandsDrawer(MatplotlibBandsDrawer):

    def draw(self, drawer_info):

        groups_weights = drawer_info["groups_weights"]
        groups_metadata = drawer_info["groups_metadata"]
        existing_bands = drawer_info["draw_bands"][0]

        for group_name in groups_weights:
            self.draw_group_weights(
                weights=groups_weights[group_name], metadata=groups_metadata[group_name],
                name=group_name, bands=existing_bands
            )

        self.draw_bands(*drawer_info["draw_bands"])

    def draw_group_weights(self, weights, metadata, name, bands):

        for ispin, spin_weights in enumerate(weights):
            for i, band_weights in enumerate(spin_weights):

                band_values = bands.sel(band=band_weights.band, spin=band_weights.spin)

                self.ax.fill_between(
                    band_values.k.values, band_values + band_weights, band_values - band_weights,
                    color=metadata["style"]["line"]["color"], label=name
                )

FatbandsPlot._drawers.register("matplotlib", MatplotlibFatbandsDrawer)
