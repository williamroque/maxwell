from maxwell.int import *

clear()

line = None

def add_point(point):
    global line
    if line is None:
        line = LineSet([point])
    else:
        line.properties.points.append(point)
        line.render()
    
track_clicks(add_point)
