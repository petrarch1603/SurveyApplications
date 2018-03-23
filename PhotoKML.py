import PIL.Image, PIL.ExifTags
import sys
import xml.dom.minidom

file = "photos/IMG_0707.JPG"

# exif_data = img._getexif()



def get_exif_data(file):
    img = PIL.Image.open(file)
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
    }
    return exif

def get_raw_gps_data(file):
    raw_exif = get_exif_data(file)
    rawgpsdata = {}
    for key in raw_exif['GPSInfo'].keys():
        decode = PIL.ExifTags.GPSTAGS.get(key, key)
        rawgpsdata[decode] = raw_exif['GPSInfo'][key]
    return rawgpsdata

def convert_to_degrees(value):
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def get_gps_data(file):
    rawgpsdata = get_raw_gps_data(file)
    rawLat = convert_to_degrees(value=rawgpsdata['GPSLatitude'])
    rawLong = convert_to_degrees(value=rawgpsdata['GPSLongitude'])
    try:
        altitude = rawgpsdata['GPSAltitude'][0] / rawgpsdata['GPSAltitude'][1]
    except KeyError:
        altitude = 0

    if rawgpsdata['GPSLatitudeRef'] == 'S':
        Lat = (-(rawLat))
    else:
        Lat = rawLat
    if rawgpsdata['GPSLongitudeRef'] == 'W':
        Long = (-(rawLong))
    else:
        Long = rawLong
    direction = (rawgpsdata['GPSImgDirection'][0] / rawgpsdata['GPSImgDirection'][1])
    clean_gps = {
        "Longitude": Long,
        "Latitude": Lat,
        "Altitude": altitude,
        "Direction": direction
    }
    return clean_gps

def create_kml_doc():
    kml_doc = xml.dom.minidom.Document()
    kml_element = kml_doc.createElementNS('http://www.opengis.net/kml/2.2', 'kml')
    kml_element.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
    kml_element = kml_doc.appendChild(kml_element)
    document = kml_doc.createElement('Document')
    kml_element.appendChild(document)
    return kml_doc


def photo_overlay(kml_doc, clean_gps, image_name):
    po = kml_doc.createElement('PhotoOverlay')
    name = kml_doc.createElement('name')
    name.appendChild(kml_doc.createTextNode(image_name))
    description = kml_doc.createElement('description')
    description.appendChild(kml_doc.createCDATASection('<a href="#%s">'
                                                       'Click here to fly into '
                                                       'photo</a>' % image_name))
    po.appendChild(name)
    po.appendChild(description)
    icon = kml_doc.createElement('Icon')
    href = kml_doc.createElement('href')
    href.appendChild(kml_doc.createTextNode(image_name))
    camera = kml_doc.createElement('Camera')
    longitude = kml_doc.createElement('longitude')
    latitude = kml_doc.createElement('latitude')
    altitude = kml_doc.createElement('altitude')
    tilt = kml_doc.createElement('tilt')
    heading = kml_doc.createElement('heading')

    # Set the Field of View
    width = get_exif_data(file)['ExifImageWidth']
    length = get_exif_data(file)['ExifImageHeight']
    lf = str(width / length * -20.0)
    rf = str(width / length * 20.0)

    longitude.appendChild(kml_doc.createTextNode(str(clean_gps['Longitude'])))
    latitude.appendChild(kml_doc.createTextNode(str(clean_gps['Latitude'])))
    altitude.appendChild(kml_doc.createTextNode('10'))
    tilt.appendChild(kml_doc.createTextNode('90'))
    heading.appendChild(kml_doc.createTextNode(str(clean_gps['Direction'])))
    camera.appendChild(longitude)
    camera.appendChild(latitude)
    camera.appendChild(altitude)
    camera.appendChild(tilt)
    camera.appendChild(heading)
    icon.appendChild(href)
    viewvolume = kml_doc.createElement('ViewVolume')
    leftfov = kml_doc.createElement('leftFov')
    rightfov = kml_doc.createElement('rightFov')
    bottomfov = kml_doc.createElement('bottomFov')
    topfov = kml_doc.createElement('topFov')
    near = kml_doc.createElement('near')
    leftfov.appendChild(kml_doc.createTextNode(lf))
    rightfov.appendChild(kml_doc.createTextNode(rf))
    bottomfov.appendChild(kml_doc.createTextNode('-20'))
    topfov.appendChild(kml_doc.createTextNode('20'))
    near.appendChild(kml_doc.createTextNode('10'))
    viewvolume.appendChild(leftfov)
    viewvolume.appendChild(rightfov)
    viewvolume.appendChild(bottomfov)
    viewvolume.appendChild(topfov)
    viewvolume.appendChild(near)
    po.appendChild(camera)
    po.appendChild(icon)
    po.appendChild(viewvolume)
    point = kml_doc.createElement('point')
    coordinates = kml_doc.createElement('coordinates')
    coordinates.appendChild(kml_doc.createTextNode('%s,%s,%s' % (clean_gps['Longitude'],
                                                                 clean_gps['Latitude'],
                                                                 clean_gps['Altitude'])))
    point.appendChild(coordinates)
    po.appendChild(point)
    document = kml_doc.getElementsByTagName('Document')[0]
    document.appendChild(po)

def CreateKmlFile(file, new_kml_name):
    kml_doc = create_kml_doc()
    clean_gps = get_gps_data(file)
    photo_overlay(kml_doc, clean_gps, file)
    kml_file = open(new_kml_name, 'w')
    kml_file.write(kml_doc.toprettyxml())

def process_photo(file):
    try:
        image = PIL.Image.open(file)
        for orientation in PIL.ExifTags.TAGS.keys():
            if PIL.ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
        exifinfo = image.info['exif']
        image.save(file, exif=exifinfo)
        image.close()
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

def main(file):
    process_photo(file)
    CreateKmlFile(file, new_kml_name='dummy.kml')

main(file)
#print(get_raw_gps_data(file))

