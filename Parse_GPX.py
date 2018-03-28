from API_call_for_GPX import project_name, project_directory
import gpxpy
import csv
import os
import re

# create csv file called merged.csv to working directory and give column names x, y & t
with open(project_name + '.csv', 'a') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar=' ', lineterminator='\n')
    writer.writerow('yxt')

# create a folder for your files manually
source_dir = project_directory + '/data/'
try:
    for file in os.listdir(source_dir):
        print(file)
        # Sometimes there are hidden or other files in the directory, we need to ignore them
        if not file.endswith(".gpx"):
            continue
        # Sometimes an empty GPX file gets included and crashes the program.
        if os.stat(source_dir + file).st_size == 0:
            print('File size zero!')
            continue
        filePath = source_dir + file
        gpx_file = open(filePath, 'r')
        gpx = gpxpy.parse(gpx_file)
        count = 0

        # iterate through rows and append each gpx row to merged csv
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    fields = ['{0},{1},{2}'.format(point.latitude, point.longitude, point.time)]
                    # Here double whitespace is removed so QGIS accepts the time format
                    re.sub(' +', ' ', fields[0])
                    # Graphhopper creates quite a lot of GPX points and for this purpose every second is enough.
                    count += 1
                    if count % 2 == 0:
                        with open(project_directory + '/GPX_merged_' + project_name + '.csv', 'a') as f:
                            writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar=' ', lineterminator='\n')
                            writer.writerow(fields)
except Exception as e:
    print(e)

