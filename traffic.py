from geojson import Polygon
import json
from secrets import *
from urllib.request import urlopen

locations = {}  # This is a key:value dictionary, key is place-name, value is coordinates
durations = [15, 30, 45]  # In minutes
travelModes = ["car"]
timestamp = "now"

appcode = here_app_code
appID = here_app_id
timestamp = "2017-12-03T16:00:00"
# coordinates = "52.471868,-1.897253"


for location in locations:
    for minute in durations:
        for mode in travelModes:
            seconds = (minute * 60)
            coords = locations[location]
            filename = (location + str(minute) + 'min' + mode + '.json')
            url = "https://isoline.route.cit.api.here.com/routing/7.2/calculateisoline.json?app_id=" + \
                  appID + "&app_code=" + \
                  appcode + "&mode=shortest;" + \
                  mode + ";traffic:enabled&start=geo!" + \
                  coords + "&maxpoints=999&departure=" + \
                  timestamp + "&range=" + \
                  str(seconds) + "&rangetype=time&jsonAttributes=41"
            response = urlopen(url)
            data = json.load(response)
            for polygon in reversed(data['response']['isoline']):
                    innerPolygon = []
                    for ind in range(0, len(polygon['component'][0]['shape'])):
                        if ind%2 == 1:
                            innerPolygon.append((polygon['component'][0]['shape'][ind], polygon['component'][0]['shape'][ind-1]))

            outerPolygon = []
            outerPolygon.append(innerPolygon)
            my_geoJSON = Polygon(outerPolygon)
            with open(filename, 'w') as f:
                f.write(str(my_geoJSON))

