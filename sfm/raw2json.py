import argparse
import json

import PyOpenImageIO as oiio

json_key_mapping = dict([
    ("AbsoluteAltitude",       "AbsoluteAltitude"),
    ("CamReverse",             "CamReverse"),
    ("Exif:ApertureValue",     "ApertureValue"),
    ("Exif:BodySerialNumber",  "SerialNumber"),
    ("Exif:DateTimeOriginal",  "DateTime"),
    ("Exif:FocalLength",       "FocalLength"),
    ("Exif:ISOSpeedRatings",   "ISOSpeedRatings"),
    ("Exif:ShutterSpeedValue", "ShutterSpeed"),
    ("Exif:WhiteBalance",      "WhiteBalance"),
    ("ExposureTime",           "Exposure"),
    ("MaxApertureValue",       "MaxApertureValue"),
    ("FlightPitchDegree",      "FlightPitch"),
    ("FlightRollDegree",       "FlightRoll"),
    ("FlightYawDegree",        "FlightYaw"),
    ("GimbalPitchDegree",      "GimbalPitch"),
    ("GimbalRollDegree",       "GimbalRoll"),
    ("GimbalYawDegree",        "GimbalYaw"),
    ("GimbalReverse",          "GimbalReverse"),
    ("GPS:Altitude",           "GPSAltitude"),
    ("GPS:AltitudeRef",        "GPSAltitudeRef"),
    ("GPS:LatitudeRef",        "GPSLatitudeRef"),
    ("GPS:LongitudeRef",       "GPSLongitudeRef"),
    ("GPS:Latitude",           "GPSLatitude"),
    ("GPS:Longitude",          "GPSLongitude"),
    ("Make",                   "Make"),
    ("Model",                  "Model"),
    ("Orientation",            "Orientation"),
    ("pixelAspectRatio",       "pixelAspectRatio"),
    ("rdf:about",              "About"),
    ("RelativeAltitude",       "RelativeAltitude")
])


def raw2json(dng_img, json_out):
    dng_spec = oiio.ImageBuf(dng_img).spec()
    print(dng_spec.serialize(format='txt', verbose='detailedhuman'))
    attribs = dng_spec.extra_attribs                                                       # get extra_attribs from spec
    attribs = [(attribs[i].name, attribs[i].value) for i in range(len(attribs))]           # convert to key, value
    attribs = filter(lambda attrib: attrib[0] in json_key_mapping, attribs)                # keep only relevant attribs
    attribs = map(lambda attrib: (json_key_mapping[attrib[0]], attrib[1]), attribs)        # replace key with mapping above
    with open(json_out, 'w') as out:                                                       # write as json
        json.dump(dict(attribs), out)    

if '__main__' == __name__:

    parser = argparse.ArgumentParser(description="dng2png")
    parser.add_argument("--input_image", help="input dng image", required=True)
    parser.add_argument("--output_json", help="output json metadata", required=True)
    args = parser.parse_args()
    raw2json(args.input_image, args.output_json)
    
