class Frame():
    def __init__(self):
        self.scene = None

    def set_scene(self, scene):
        self.scene = scene

    def props(self, shape_id):
        return self.scene.shapes[shape_id].properties

    def apply_frame(self, properties):
        pass
