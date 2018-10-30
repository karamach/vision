import argparse
import json

import PyOpenImageIO as oiio
from buffer_ops import GradeOp

def raw2exr(dng_img, exr_img, blackpoint, whitepoint, gamma):
    dng_inp = oiio.ImageBuf(dng_img)
    [graded_out] = GradeOp(blackpoint, whitepoint, gamma).op([dng_inp])    
    graded_out.write(exr_img)

if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='raw2exr')
    parser.add_argument("--input_image", help='input dng image', required=True)
    parser.add_argument("--output_image", help='output exr image', required=True)
    parser.add_argument("--blackpoint", nargs='+', help='blackpoint for rgb', required=True, type=float)
    parser.add_argument("--whitepoint", nargs='+', help='whitepoint for rgb', required=True, type=float)
    parser.add_argument("--gamma", nargs='+', help='gamma for rgb', required=True, type=float)

    args = parser.parse_args()
    raw2exr(args.input_image, args.output_image, args.blackpoint, args.whitepoint, args.gamma)

# Sample invocation
# python q/containers/q_exec/py_ops/raw2exr.py --input_image q/containers/q_exec/py_ops/data/DJI.0228.DNG --output_image q/containers/q_exec/py_ops/data/DJI.0228.exr --blackpoint 0 0 0 --whitepoint 1 1 1 --gamma 1 1 1
    
