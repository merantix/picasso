import re


class BaseVisualization:
    """Interface encapsulating a NN visualization.

    This interface defines how a visualization is computed for a given NN
    model.

    """
    # (:obj:`str`): Short description of the visualization.
    DESCRIPTION = None

    # (:obj:`str`): Optional link to the paper specifying the visualization.
    REFERENCE_LINK = None

    # (:obj:`dict`): Optional visualization settings that the user can select,
    # as a dict mapping setting names to lists of their allowed values.
    ALLOWED_SETTINGS = None

    def __init__(self, model):
        """Create a new instance of this visualization.

        `BaseVisualization` is an interface and should only be instantiated via
        a subclass.

        Args:
            model (:obj:`.models.model.BaseModel`): NN model to be
                visualized.

        """
        self._model = model

        # give default settings
        if self.ALLOWED_SETTINGS:
            self.update_settings({setting: self.ALLOWED_SETTINGS[setting][0]
                                  for setting in self.ALLOWED_SETTINGS})

    @property
    def model(self):
        """NN model to be visualized.

        (:obj:`.models.model.BaseModel`)

        """
        return self._model

    def update_settings(self, settings):
        """Update the settings

        If a derived class has an ALLOWED_SETTINGS dict, we check here that
        incoming settings from the web app are allowed, and set the child
        properties as appropriate.

        """

        def error_string(setting, setting_val):
            return ('{val} is not an acceptable value for '
                    'parameter {param} for visualization'
                    '{vis}.').format(val=setting_val,
                                     param=setting,
                                     vis=self.__class__.__name__)

        for setting in settings:
            if settings[setting] in self.ALLOWED_SETTINGS[setting]:
                # if the setting is allowed, set the attribute but remove
                # invalid variable characters
                #
                # see:
                #
                # https://stackoverflow.com/questions/3303312/how-do-i-convert-a-string-to-a-valid-variable-name-in-python
                setattr(self, '_' + re.sub('\W|^(?=\d)', '_', setting).lower(),
                        settings[setting])
            else:
                raise ValueError(error_string(settings[setting], setting))

    def make_visualization(self, inputs, output_dir, settings=None):
        """Generate the visualization.

        All visualizations must implement this method.

        Args:
            inputs (iterable of :class:`PIL.Image`): Batch of input images to
                make visualizations for, as PIL :obj:`Image` objects.
            output_dir (:obj:`str`): A directory to write outputs (e.g.,
                plots) to.
            settings (:obj:`str`): Dictionary of settings that the user
                selected, as a dict mapping setting names to values.  This
                should only be provided if this class's `ALLOWED_SETTINGS`
                attribute is non-null.

        Returns:
            Object used to render the visualization, passed directly to the
            visualization class's associated HTML template.  Since this HTML
            template is custom for each visualization class, the return type
            is arbitrary.

        """
        raise NotImplementedError
