import csv

control = "/Users/patrickmcgranaghan1/Documents/Python/python_work/SurveyApplications/control.csv"
setpoints = "/Users/patrickmcgranaghan1/Documents/Python/python_work/SurveyApplications/setPoints.csv"
max_hypotenuse = 200  # Integer in feet

# Note in the State Plane Coordinate System the coordinates are written Northing(Y), Easting(X)
#   This is the opposite of the normal (X, Y) coordinate system.

with open(setpoints, 'r') as setpts:
    setreader = csv.reader(setpts)
    for setcoord in setreader:
        templist = []
        with open(control, 'r') as ctrl:
            ctrlreader = csv.reader(ctrl)
            for ctrlcoord in ctrlreader:
                xDelta = int(setcoord[2]) - int(ctrlcoord[2])
                yDelta = int(setcoord[1]) - int(ctrlcoord[1])
                hypotenuse = ((xDelta ** 2) + (yDelta ** 2)) ** (0.5)
                if hypotenuse <= max_hypotenuse:
                    tup = (ctrlcoord[0], hypotenuse)
                    templist.append(tup)
        closest_base = (min(templist, key=lambda t: t[1]))

        # Below write code to insert the closest control points into the spreadsheet in a selected column
        print(setcoord[0] + " is closest to " + (closest_base[0]) + ". A distance of " + str(closest_base[1]))
