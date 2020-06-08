
# Nick
# Here you should not expose PRESETS? Or should you?
#
# Currently you are exposing PRESETS, add_presets, get_preset
# But probably you only want add_presets, get_preset
# You should try and add __all__ for all modules for clarity
# This ensures that you only expose what you want
# Note that __all__ does not omit the possibility of
# fetching non-exposes methods. ;)

PRESETS = {

    "dark": {
        "layout": {"template": "sisl_dark"},
        "bands_color": "#ccc",
        "bands_width": 2
    },

}

def add_presets(**presets):
    '''
    Registers new presets

    Parameters
    ----------
    **presets:
        as many as you want. Each preset is a dict.
    '''

    global PRESETS
    # Nick
    # why not just
    #   PRESETS.update(presets) ?

    PRESETS = {**PRESETS, **presets}

def get_preset(name):
    '''
    Gets the asked preset.

    Parameters
    -----------
    name: str
        the name of the preset that you are looking for
    '''
    global PRESETS
    return PRESETS.get(name, None)
