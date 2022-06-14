class Interaction:
    "A class that describes a type of interaction between objects."

    def __init__(self, objects):
        self.objects = objects

    def test(self, obj):
        """Test object to see if its properties warrant this interaction (mass ->
        gravity, for instance).
        """

        raise NotImplementedError

    def interact(self):
        "Use and change the physical properties of interacting objects."

        raise NotImplementedError
