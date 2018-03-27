import os
import pandas as pd
import urllib.request

# path to your csv file with the endpoint coordinates
project_name = 'colorado'  # String with no spaces or irregular characters. Will be used in naming files and a directory
coordinates = pd.read_csv('source_data/grid_colorado.csv')

# graphhopper API call building blocks. Check Graphhopper documentation how to modify these.
urlStart = 'http://localhost:8989/route?'
point = 'point='
urlEnd = '&type=gpx&instructions=false&vehicle=car'
separator = '%2C'

# The starting point for each query (lat, lon). Use e.g. QGIS to change these.
startY = '39.549405'
startX = '-104.867832'

# Make the API calls for each row in you CSV file and save the results to individual .gpx files.
for index, row in coordinates.iterrows():
    req = urlStart + point + startY + separator + startX + '&' + point + str(row['Y']) + separator + str(row['X']) + urlEnd
    try:
        resp = urllib.request.urlopen(str(req))
        gpxData = str(resp.read(),'utf-8')
        current_dir = os.getcwd()
        os.makedirs(project_name)
        fileName = current_dir + '/' + project_name + '/' + str(index) + '.gpx'
        saveFile = open(str(fileName), 'w')
        print('Processed index ' + str(index))
        saveFile.write(gpxData)
        saveFile.close()
    except Exception as e:
        print('ERROR: ' + str(e) + '.\nBad request on index ' + str(index))
        pass

#resp = urllib.request.urlopen('http://localhost:8989/route?point=39.549405%2C-104.867832&point=41.0008582686798%2C-109.046670266878&type=gpx&instructions=false&vehicle=car')
