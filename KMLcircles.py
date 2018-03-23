import math
import simplekml


radius = 2

def make_circle(initial, raw_radius, sides):
    new_coords = []
    angle = 0
    angle_increment = (math.tau / sides)
    lat_radians = math.radians(lat)
    length_of_equator_degree = 69.172
    constant = math.cos(lat_radians)
    mile = (1 / (constant * length_of_equator_degree))
    radius = (raw_radius * mile)
    for i in range(sides+1):
        x = initial[0] + radius * math.cos(angle)
        y = initial[1] - constant * radius * math.sin(angle)
        coords = (str(x), str(y))
        coords = tuple(coords)
        new_coords.append(coords)
        angle += angle_increment
    return new_coords

my_coords = [-79.395373, 43.743782]
long = my_coords[0]
lat = my_coords[1]
new_long = (long) * math.cos(lat)

kml = simplekml.Kml()
my_circle = make_circle(initial=my_coords, raw_radius=2, sides=20)
earth_circle = kml.newlinestring(name="Toronto Circle",
                          coords=my_circle)
kml.save("circle.kml")