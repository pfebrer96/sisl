import inspect

class EntryPoints:
    """The entry points manager for a plot class"""

    def __init__(self, plot_cls):
        self._entry_points = {}

        self._cls = plot_cls
        self._output_validator = None
    
    def help(self):
        """ Generates a helpful message about the entry points of the plot class """
        string = ""

        if self._output_validator is not None:
            string += f"Here is some information about what an entry point for {self._cls.__name__} needs to implement:\n"
            string += self._output_validator.__doc__
            string += "\n\n"

        string += "REGISTERED ENTRY POINTS:\n\n"

        for name, entry_point in self._entry_points.items():

            string += f"{name}\n------------\n\n"
            string += (entry_point["func"].__doc__ or "").lstrip()

            string += "\nSettings used:\n\t- "
            string += '\n\t- '.join(entry_point["settings"])
            string += "\n\n"

        return string

    def register(self, name, entry_point):
        """Register a new entry point to the available entry points.

        Parameters
        -----------
        name: str
            The name of the entry_point being registered. Users will need to pass this value
            in order to choose this entry_point.
        entry_point: function
            The entry point to be registered
        """
        # Update the options of the entry point setting
        entry_point_param = self._cls.get_class_param("entry_point")
        entry_point_param.options = [*entry_point_param.get_options(raw=True), {"label": name, "value": name}]
        entry_point_param.default = [*entry_point_param.default, name]

        entry_point._entry_point_name = name
        self._entry_points[name] = {
            "func": entry_point,
            "settings": tuple(inspect.signature(entry_point).parameters)[1:]
        }

    def register_output_validator(self, output_validator):
        self._output_validator = output_validator

    def use(self, entry_point_name, plot):
        func = self._entry_points[entry_point_name]["func"]
        settings = self.entry_point_settings(entry_point_name)

        ret = func(plot, **{key: plot.get_setting(key) for key in settings})

        if self._output_validator is not None:
            self._output_validator(ret)

        return ret

    def entry_point_settings(self, entry_point_name):
        return self._entry_points[entry_point_name]["settings"]
    
    @property
    def options(self):
        return list(self._entry_points)

    def __getitem__(self, i):
        return lambda func: 3