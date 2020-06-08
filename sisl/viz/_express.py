'''

This file implements a smooth interface between sisl and plotly express,
to make visualization of sisl objects even easier.

This goes hand by hand with the implementation of dataframe extraction in sisl
objects, which is not already implemented (https://github.com/zerothi/sisl/issues/220)

'''

from functools import wraps

import plotly.express as px
from sisl._dispatcher import AbstractDispatch, ClassDispatcher

__all__ = ['sx']

class WithSislManagement(AbstractDispatch):

    def __init__(self, px):

        self._obj = px

    def dispatch(self, method):

        @wraps(method)
        def with_sisl_support(*args, **kwargs):

            # Nick:
            # Hmm, isn't the first two checks equivalent?
            # I.e. len(args) > 0 == bool(args)
            # Also, no need to cast args to list
            # You could just do (and NO args=list(args))
            #   if args:
            #       ...
            if args:
                # Try to generate the dataframe for this object.
                # Nick:
                # I think we should rename this to 
                if hasattr(args[0], 'to_df'):
                    parent_obj = args[0].to_df()
                else:
                    parent_obj = args[0]

                # Otherwise, we are just going to interpret it as if the user wants to get the attributes
                # of the object. We will support deep attribute getting here using points as separators.
                # (I don't know if this makes sense because there's probably hardly any attributes that are
                # ready to be plotted, i.e. they are 1d arrays)
                for key, val in kwargs.items():
                    if isinstance(val, str):
                        obj = parent_obj

                        # recursively dig out the attribute
                        for attr in val.split('.'):
                            newval = getattr(obj, attr, None)
                            if newval is None:
                                break
                            obj = newval

                        else:
                            # If we've gotten to the end of the loop, it is because we've found the attribute.
                            val = obj

                        # Replace the provided string by the actual value of the attribute
                        kwargs[key] = val
                            
            ret = method(*args, **kwargs)

            return ret

        return with_sisl_support

sx = WithSislManagement(px)
