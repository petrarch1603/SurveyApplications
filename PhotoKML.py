import datetime
import os
import PIL.Image, PIL.ExifTags
import shutil
import xml.dom.minidom

target_dir = "photos/"
now = datetime.datetime.now()
today = now.strftime("%Y%m%d")


def make_KMZ_dir(new_kml_dir):
    today_dir = today
    os.makedirs(today_dir)
    os.makedirs(today_dir + "/files")
    src_files = os.listdir(target_dir)
    for file_name in src_files:
        full_file_name = os.path.join(target_dir, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, today_dir + "/files")
    shutil.move(os.path.join(os.getcwd(), new_kml_dir), today_dir)
    return today_dir


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
    orientation = raw_exif['Orientation']
    raw_gps_data = {"Orientation": orientation}
    for key in raw_exif['GPSInfo'].keys():
        decode = PIL.ExifTags.GPSTAGS.get(key, key)
        raw_gps_data[decode] = raw_exif['GPSInfo'][key]
    return raw_gps_data


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
    raw_gps_data = get_raw_gps_data(file)
    raw_lat = convert_to_degrees(value=raw_gps_data['GPSLatitude'])
    raw_long = convert_to_degrees(value=raw_gps_data['GPSLongitude'])
    orientation = raw_gps_data['Orientation']
    try:
        altitude = raw_gps_data['GPSAltitude'][0] / raw_gps_data['GPSAltitude'][1]
    except KeyError:
        altitude = 0

    if raw_gps_data['GPSLatitudeRef'] == 'S':
        lat = -raw_lat
    else:
        lat = raw_lat
    if raw_gps_data['GPSLongitudeRef'] == 'W':
        long = -raw_long
    else:
        long = raw_long
    direction = (raw_gps_data['GPSImgDirection'][0] / raw_gps_data['GPSImgDirection'][1])
    clean_gps = {
        "Longitude": long,
        "Latitude": lat,
        "Altitude": altitude,
        "Direction": direction,
        "Orientation": orientation
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


def photo_overlay(kml_doc, clean_gps, photo_file_path):
    po = kml_doc.createElement('PhotoOverlay')
    name = kml_doc.createElement('name')
    name.appendChild(kml_doc.createTextNode(photo_file_path))
    description = kml_doc.createElement('description')
    description.appendChild(kml_doc.createCDATASection('<a href="#%s">'
                                                       'Click here to fly into '
                                                       'photo</a>' % photo_file_path))
    po.appendChild(name)
    po.appendChild(description)
    icon = kml_doc.createElement('Icon')
    href = kml_doc.createElement('href')
    href.appendChild(kml_doc.createTextNode(photo_file_path))
    camera = kml_doc.createElement('Camera')
    longitude = kml_doc.createElement('longitude')
    latitude = kml_doc.createElement('latitude')
    altitude = kml_doc.createElement('altitude')
    tilt = kml_doc.createElement('tilt')
    heading = kml_doc.createElement('heading')

    # Set the Field of View
    # The following might seem counter-intuitive.
    # If the photo has been rotated, we need to switch the height and width
    # Otherwise Google Earth will stretch the image as if it is still in the landscape mode.
    orient = clean_gps['Orientation']
    if orient in (6, 8):
        width = get_exif_data(photo_file_path)['ExifImageHeight']
        length = get_exif_data(photo_file_path)['ExifImageWidth']
    else:
        width = get_exif_data(photo_file_path)['ExifImageWidth']
        length = get_exif_data(photo_file_path)['ExifImageHeight']
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
    view_volume = kml_doc.createElement('ViewVolume')
    left_fov = kml_doc.createElement('leftFov')
    right_fov = kml_doc.createElement('rightFov')
    bottom_fov = kml_doc.createElement('bottomFov')
    top_fov = kml_doc.createElement('topFov')
    near = kml_doc.createElement('near')
    left_fov.appendChild(kml_doc.createTextNode(lf))
    right_fov.appendChild(kml_doc.createTextNode(rf))
    bottom_fov.appendChild(kml_doc.createTextNode('-20'))
    top_fov.appendChild(kml_doc.createTextNode('20'))
    near.appendChild(kml_doc.createTextNode('10'))
    view_volume.appendChild(left_fov)
    view_volume.appendChild(right_fov)
    view_volume.appendChild(bottom_fov)
    view_volume.appendChild(top_fov)
    view_volume.appendChild(near)
    style = kml_doc.createElement('Style')
    iconstyle = kml_doc.createElement('IconStyle')
    # The following are elements for the style only.
    # Hence the names with '2' to avoid a conflict with other elements with the same name in the DOM
    icon2 = kml_doc.createElement('Icon')
    href2 = kml_doc.createElement('href')
    href2.appendChild(kml_doc.createTextNode('http://maps.google.com/mapfiles/kml/shapes/camera.png'))
    style.appendChild(iconstyle)
    iconstyle.appendChild(icon2)
    icon2.appendChild(href2)
    po.appendChild(style)
    po.appendChild(camera)
    po.appendChild(icon)
    po.appendChild(view_volume)
    point = kml_doc.createElement('Point')
    coordinates = kml_doc.createElement('coordinates')
    coordinates.appendChild(kml_doc.createTextNode('%s,%s,%s' % (clean_gps['Longitude'],
                                                                 clean_gps['Latitude'],
                                                                 clean_gps['Altitude'])))
    point.appendChild(coordinates)
    po.appendChild(point)
    document = kml_doc.getElementsByTagName('Document')[0]
    document.appendChild(po)


def Create_Kml_File(dir, new_kml_name):
    kml_doc = create_kml_doc()
    for photo_file in os.listdir(dir):
        if not photo_file.startswith('.'):
            photo_file_path = (dir + photo_file)
            process_photo(photo_file_path)
            clean_gps = get_gps_data(photo_file_path)
            photo_overlay(kml_doc, clean_gps, photo_file_path)
    kml_file = open(new_kml_name, 'w')
    kml_file.write(kml_doc.toprettyxml())
    print(kml_doc.toprettyxml())


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


def main():
    new_kml_name = (today + '.kml')
    today_dir = make_KMZ_dir(today)
    home_dir = os.getcwd()
    os.chdir(today_dir)
    Create_Kml_File('files/', new_kml_name=new_kml_name)
    os.chdir(home_dir)
    shutil.make_archive(base_name=(today + '.kmz'), format='zip', root_dir=today_dir)
    os.rename(today + '.kmz.zip', today + '.kmz')
    shutil.rmtree(today_dir)


if __name__ == '__main__':
    main()

