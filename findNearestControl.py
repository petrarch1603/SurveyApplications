import csv

control = "/Users/patrickmcgranaghan1/Documents/Python/python_work/SurveyApplications/source_data/control.csv"
set_points = "/Users/patrickmcgranaghan1/Documents/Python/python_work/SurveyApplications/source_data/setPoints.csv"
max_hypotenuse = 200  # Integer in feet

# Note in the State Plane Coordinate System the coordinates are written Northing(Y), Easting(X)
#   This is the opposite of the normal (X, Y) coordinate system.

with open(set_points, 'r') as set_pts:
    set_reader = csv.reader(set_pts)
    for set_coord in set_reader:
        temp_list = []
        with open(control, 'r') as ctrl:
            ctrl_reader = csv.reader(ctrl)
            for ctrl_coord in ctrl_reader:
                xDelta = int(set_coord[2]) - int(ctrl_coord[2])
                yDelta = int(set_coord[1]) - int(ctrl_coord[1])
                hypotenuse = ((xDelta ** 2) + (yDelta ** 2)) ** 0.5
                if hypotenuse <= max_hypotenuse:
                    tup = (ctrl_coord[0], hypotenuse)
                    temp_list.append(tup)
        closest_base = (min(temp_list, key=lambda t: t[1]))

        # Below write code to insert the closest control points into the spreadsheet in a selected column
        print(set_coord[0] + " is closest to " + (closest_base[0]) + ". A distance of " + str(closest_base[1]))
