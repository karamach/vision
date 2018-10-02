from similaritytransformop_py import ostream_redirect
from similaritytransformop_py import SimilarityTransformOp, DoubleList 
from similaritytransformop_py import PyPoint3, PyRot3, PyPose3, MapStringPyPose3

# gps_views : [viewid_1, viewid_2, ...]
# gps_data : [[x1, y1, z1], [x2, y2, z2], ...]
# solve_views : [viewid_1, viewid_2, ...]
# solve_data : [[x1, y1, z1], [x2, y2, z2], ...]
def compute_transform(gps_views, gps_data, solve_views, solve_data):
    yawPrior, transPrior, scalePrior, noiseStd = PyRot3(0.01, 0.01, 0.01), PyPoint3(0.01, 0.01, 0.01), 1, 1
    estParam, estType, applyPreTransform = 5, 'huber', True
    gps_d, solve_d = MapStringPyPose3(), MapStringPyPose3()
    for v, g in zip(gps_views, gps_data):
        gps_d[v] = PyPose3(PyRot3(0, 0, 0), PyPoint3(g[0], g[1], g[2]))
    for v, s in zip(solve_views, solve_data):
        xyz, quat = s[0], [s[1][3]] + s[1][:3]  # change quat to w,x,y,z
        solve_d[v] = PyPose3(PyRot3(*quat), PyPoint3(*xyz))

    transform = DoubleList()
    op = SimilarityTransformOp(yawPrior, transPrior, scalePrior, noiseStd, estParam, estType, applyPreTransform);
    with ostream_redirect():
        ret = op.computeTransformUnnormalized(gps_d, solve_d, transform)
        return transform if ret else None

