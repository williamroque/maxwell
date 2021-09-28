class Frame():
    def __init__(self, apply_callback=None, setup_callback=None):
        self.apply_callback = apply_callback
        self.setup_callback = setup_callback

        self.scene = None
        self.is_first = False


    def set_scene(self, scene):
        self.scene = scene


    def props(self, shape_id):
        return self.scene.shapes[shape_id].properties


    def apply_frame(self):
        props = self.scene.properties

        if props.i == 0:
            self.is_first = True

        if 'easing_function' in props.keys()\
           and props.i < len(props.easing_function):
            props.easing_ratio = props.easing_function[props.i]

        if props.i == 0 and self.setup_callback is not None:
            self.setup_callback(self, props)

        if self.apply_callback is not None:
            self.apply_callback(self, props)

        props.i += 1
