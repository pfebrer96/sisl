'''
This file defines all the siles that are plotable.

It does so by patching the classes accordingly

In the future, sisl objects will probably be 'plotable' too
'''
from functools import partial
from types import MethodType

import numpy as np

import sisl.io.siesta as siesta
from sisl.io.sile import get_siles, BaseSile

import sisl
from .plots import *
from .plot import Plot


# -----------------------------------------------------
#   Let's define the functions that will help us here
# -----------------------------------------------------

def _get_plotting_func(PlotClass, setting_key):

    def _plot(self, *args, **kwargs):
        return PlotClass(*args, **{setting_key: self, **kwargs})
    
    _plot.__doc__ = f'''Builds a {PlotClass.__name__} by setting the value of "{setting_key}" to the current object.
    
    It accepts the same arguments as {PlotClass.__name__}. 
    
    Documentation for {PlotClass.__name__}
    -------------
    
    {PlotClass.__doc__}
    '''
    
    return _plot

def _plot_default(self, *args, plot_suffix=None,**kwargs):
    '''
    Plots the default representation for the object.

    However, a different representation can be obtained (see the plot_suffix parameter).

    Parameters
    ----------
    plot_suffix: str, optional
        the suffix of the plotting function that you want to plot.

        E.g.: obj.plot(suffix="nicely") is equivalent to obj.plot_nicely()
    '''

    suffix = plot_suffix or self._plot_default_suffix

    return getattr(self, f"plot_{suffix}")(*args, **kwargs)

def register_plotable(plotable, PlotClass=None, setting_key=None, plotting_func=None,
    suffix=None, default=None, all_instances=False):
    '''
    Makes the sisl.viz module aware of which sisl objects can be plotted and how to do it.

    Parameters
    ------------
    plotable: any
        any class or object that you want to make plotable. Note that, if it's an object, the plotting
        capabilities will be attributed ONLY to that object, not the whole class. You can change this
        behavior by setting the `all_instances` parameter to True.
    PlotClass: child of sisl.Plot, optional
        The class of the Plot that we want this object to use.
    setting_key: str, optional
        The key of the setting where the object must go. This works together with
        the PlotClass parameter.
    suffix: str, optional
        suffix that will be used to identify the particular plot function that is being registered.

        E.g.: If suffix is "nicely", the plotting function will be registered under "obj.plot_nicely()"

        IF THE PLOT CLASS YOU ARE USING IS NOT ALREADY REGISTERED FOR THE PLOTABLE, PLEASE LET THE SUFFIX
        BE HANDLED AUTOMATICALLY UNLESS YOU HAVE A GOOD REASON NOT TO DO SO. This will help keeping consistency
        across the different objects as the suffix is determined by the plot class that is being used.
    plotting_func: function, optional
        if the PlotClass - setting_key pair does not satisfy your needs, you can pass a more complex function here
        instead.
        It should accept (self, *args, **kwargs) and return a plot object.
    default: boolean, optional 
        whether this way of plotting the class should be the default one.
        If not provided, it will be set to True if it's the first register and False otherwise.
    all_instances: boolean, optional
        if you are passing an object, this determines whether the plotability is given to all the instances
        of the class or just to the particular object.
    '''

    is_instance = False
    if not isinstance(plotable, type):
        if all_instances:
            plotable = plotable.__class__
        else:
            is_instance = True

    # If it's the first time that the class is being registered,
    # let's initialize it's "plotability"
    is_first_register = not hasattr(plotable, "_plot_funcs")
    if is_first_register:
        plotable._plot_funcs = {}

        # If the object already has a plot attribute, we will call this one
        # plot_sisl to avoid overwriting (I don't know if this will ever happen)
        if hasattr(plotable, "plot"):
            plotattr_name = "plot_sisl"
        else:
            plotattr_name = "plot"

        if is_instance:
            plot_default = MethodType(_plot_default, plotable)
        else:
            plot_default = _plot_default

        setattr(plotable, plotattr_name, plot_default)
    
    # If no plotting function is provided, we will try to create one by using the PlotClass
    # and the setting_key that have been provided
    if plotting_func is None:
        plotting_func = _get_plotting_func(PlotClass, setting_key)
    if is_instance:
        plotting_func = MethodType(plotting_func, plotable)

    if suffix is None:
        # We will take the name of the plot class as the suffix
        suffix = PlotClass.suffix()

    if default or (default is None and is_first_register):
        plotable._plot_default_suffix = suffix

    # Register the plotting method
    setattr(plotable, f'plot{"_"+suffix if suffix else ""}', plotting_func)

# -----------------------------------------------------
#               Register plotable siles
# -----------------------------------------------------

register_plotable(siesta.bandsSileSiesta, BandsPlot, 'bands_file')

register_plotable(siesta.pdosSileSiesta, PdosPlot, 'pdos_file')

for GridSile in get_siles(attrs=["read_grid"]):
    register_plotable(GridSile, GridPlot, 'grid_file')

for GeomSile in get_siles(attrs=["read_geometry"]):
    register_plotable(GeomSile, GeometryPlot, 'geom_file', default=True)
    register_plotable(GeomSile, BondLengthMap, 'geom_file')

# -----------------------------------------------------
#           Register plotable sisl objects
# -----------------------------------------------------

register_plotable(sisl.Geometry, GeometryPlot, 'geom')
register_plotable(sisl.Geometry, BondLengthMap, 'geom')

register_plotable(sisl.Grid, GridPlot, 'grid')

def plot_wf(eigenstate, geometry, i=0, grid_prec=0.2, plot_geom=False, geom_kwargs={}, **kwargs):
    '''
    Plots a wavefunction from an eigenstate using the basis orbitals of a geometry.

    Parameters
    -----------
    geometry: sisl.Geometry
        Necessary to generate the grid and to plot the wavefunctions, since the basis orbitals are needed.
    i: int, optional
        the index of the wavefunction.
    grid_prec: float, optional
        the precision (in Ang) of the grid where the WF will be projected. If you are
        plotting a 3D representation, take into account that a very fine and big grid could result in
        your computer crashing on render. If it's the first time you are using this function,
        assess the capabilities of your computer by first using a low-precision grid and increase
        it gradually.
    plot_geom: boolean, optional
        whether the geometry should also be plotted. If true, a geometry plot and a grid plot
        are merged to create the final plot.
    geom_kwargs: dict, optional
        dictionary with the keyword arguments that should be passed to `geom.plot()` if `plot_geom`
        is set to True.
    **kwargs:
        they go directly to the initialization of GridPlot, so you can check the documentation
        of grid plot to see what you have available.
    '''

    grid = sisl.Grid(grid_prec, geometry=geometry)
    eigenstate[i].wavefunction(grid)

    grid_plot_kwargs = {**{'axes': [0, 1, 2],
                           'trace_name': f'WF {int(i)}'}, **kwargs}

    plot = grid.plot(**grid_plot_kwargs)

    if plot_geom:
        geom_plot = geometry.plot(
            **{**{'axes': grid_plot_kwargs["axes"]}, **geom_kwargs})
        plot = plot.merge(geom_plot)

        plot.layout = geom_plot.layout

    plot.update_layout(legend_orientation='h')

    return plot

def plot_wf_H(H, i, from_valence=False, k=(0,0,0), grid_prec=0.2, geometry=None, plot_geom=False, geom_kwargs={}, **kwargs):
    '''
    Plots a wavefunction calculated from the hamiltonian and the basis orbitals in a geometry.

    Parameters
    -----------
    i: int
        the index of the wavefunction,
    from_valence: boolean, optional
        whether the indexing reference should be the valence state (or HOMO) instead
        of the first state.

        If set to True, i=0 means the valence state (HOMO), i=1 is the conduction state (LUMO),
        i=-1 is the level just below the valence state, etc...

        Right now, it ASSUMES THAT THE VALENCE INDEX IS JUST HALF THE NUMBER OF ORBITALS (or the number of
        orbitals if there is spin polarization) so it may not be correct in some cases (e.g. electron doping).
    k: array-like of shape (3,), optional
        the k point where the wavefunction needs to be calculated
    grid_prec: float, optional
        the precision (in Ang) of the grid where the WF will be projected. If you are
        plotting a 3D representation, take into account that a very fine and big grid could result in
        your computer crashing on render. If it's the first time you are using this function,
        assess the capabilities of your computer by first using a low-precision grid and increase
        it gradually.
    geometry: sisl.Geometry, optional
        Necessary to generate the grid and to plot the wavefunctions, since the basis orbitals are needed.
        If not provided, it will be taken from the Hamiltonian. 
    plot_geom: boolean, optional
        whether the geometry should also be plotted. If true, a geometry plot and a grid plot
        are merged to create the final plot.
    geom_kwargs: dict, optional
        dictionary with the keyword arguments that should be passed to `geom.plot()` if `plot_geom`
        is set to True.
    **kwargs:
        they go directly to the initialization of GridPlot, so you can check the documentation
        of grid plot to see what you have available.
    '''

    geom = geometry if geometry is not None else H.geom

    if from_valence:
        i += geom.no/(1 if H.spin.is_polarized else 2)

    eig = H.eigenstate(k)

    return eig.plot_wf(geometry=geom, i=i, grid_prec=grid_prec, plot_geom=plot_geom, geom_kwargs=geom_kwargs, **kwargs)

register_plotable(sisl.EigenstateElectron, GridPlot, plotting_func=plot_wf, suffix='wf')
register_plotable(sisl.Hamiltonian, GridPlot, plotting_func=plot_wf_H, suffix='wf')

register_plotable(sisl.Hamiltonian, BandsPlot, "H")
register_plotable(sisl.BandStructure, BandsPlot, "band_structure")

register_plotable(sisl.Hamiltonian, FatbandsPlot, "H")
register_plotable(sisl.BandStructure, FatbandsPlot, "band_structure")
    
