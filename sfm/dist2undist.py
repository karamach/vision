import argparse
import math, cmath
from functools import reduce

import PyOpenImageIO as oiio

def undistort(img, out_img, focal_length, k1):

    img = oiio.ImageBuf(img)
    
    width, height, chans = img.spec().width, img.spec().height, img.spec().nchannels
    norm = focal_length*max(width, height)
    width_half, height_half = width/2.0, height/2.0

    def compute_undistorted(y, x, k1, width_half, height_half, norm):
        fx = (float(x) - width_half)/norm
        fy = (float(y) - height_half)/norm
        fy = 1e-10 if fy == 0 else fy
        t2 = fy*fy
        t3 = t2*t2*t2
        t4 = fx*fx
        t7 = k1*(fy*fy+fx*fx)

        if k1 > 0:
            t8 = 1.0/t7
            t10 = t3/(t7*t7)
            t14 = math.sqrt(t10*(.25+t8/27.0))
            t15 = t2*t8*fy*.5
            t17 = math.pow(t14+t15, 1.0/3.0)
            t18 = t17-t2*t8/(t17*3.0)
            fx = t18*fx/fy
            fy = t18
        else:
            t9 = t3/(t7*t7*4.0)
            t11 = t3/(t7*t7*t7*27.0)
            t12 = complex(t9+t11)
            t13 = cmath.sqrt(t12)
            t14 = t2/t7
            t15 = t14*fy*.5
            t16 = complex(t13+t15)
            t17 = cmath.pow(t16, 1.0/3.0)
            t18 = (t17+t14/(t17*3.0))*complex(0.0, math.sqrt(3.0))
            t19 = -.5*(t17+t18) + t14/(t17*6.0)
            fx = t19.real * fx/fy
            fy = t19.real

        fx, fy = fx*norm +width_half, fy*norm+height_half
        if fx < -.5 or fx > width-.5 or fy < .5 or fy > height-.5:
            return None
        return (x, y, fx, fy)

    dst = oiio.ImageBuf()
    dst.reset(oiio.ImageSpec(width, height, chans, oiio.FLOAT))

    pixel_correspondences = [
        [compute_undistorted(y, x, k1, width_half, height_half, norm) for x in range(width)]
        for y in range(height)
    ]
    print(len(pixel_correspondences))
    for l in pixel_correspondences:
        for coord in l:
            if coord:
                x, y, fx, fy = coord
                dst.setpixel(x, y, img.getpixel(int(fx), int(fy)))
    
    dst.write(out_img)
                
if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='raw2exr')
    parser.add_argument('--input_image', help='input dng image', required=True)
    parser.add_argument('--output_image', help='output exr image', required=True)
    parser.add_argument('--focal_length', help='focal_length', required=True, type=float)
    parser.add_argument('--k1', help='distortion coefficient', required=True, type=float)

    args = parser.parse_args()
    undistort(args.input_image, args.output_image, args.focal_length, args.k1)
    

# Sample invocation
# python q/containers/q_exec/py_ops/exrdist2exrundist.py --input_image /tmp/DJI_py_exrdist.0229.exr -output_image /tmp/DJI_py_undist.0229.exr --k1 .3 --focal_length .66
