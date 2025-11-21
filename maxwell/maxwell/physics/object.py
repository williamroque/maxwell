class Object:
    "A class for physical objects."

    def __init__(self, properties, figure_properties):
        self.properties = properties
        self.figure = self.build_figure(figure_properties)

    def build_figure(self, figure_properties):
        "Create a Shape to represent the object."

        raise NotImplementedError

    def create_interactions(self, other):
        "Find all possible interactions with other object."

        raise NotImplementedError

    def apply_properties(self):
        "Apply physical properties to figure."

        raise NotImplementedError
