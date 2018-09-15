from similaritytransformop_py import SimilarityTransformOp, DoubleList 
from similaritytransformop_py import PyPoint3, PyRot3, MapStringPyPoint3

# gps_views : [viewid_1, viewid_2, ...]
# gps_data : [[x1, y1, z1], [x2, y2, z2], ...]
# solve_views : [viewid_1, viewid_2, ...]
# solve_data : [[x1, y1, z1], [x2, y2, z2], ...]
def compute_transform(gps_views, gps_data, solve_views, solve_data):
    yawPrior, transPrior, scalePrior, noiseMean = PyRot3(0, 0, 0), PyPoint3(0, 0, 0), 1, 1
    op = SimilarityTransformOp(yawPrior, transPrior, scalePrior, noiseMean);
    gps_d, solve_d = MapStringPyPoint3(), MapStringPyPoint3()
    for v, g in zip(gps_views, gps_data):
        gps_d[v] = PyPoint3(g[0], g[1], g[2])
    for v, s in zip(solve_views, solve_data):
        solve_d[v] = PyPoint3(s[0], s[1], s[2])
        
    transform = DoubleList()
    ret = op.computeTransformUnnormalized(gps_d, solve_d, transform)
    return transform if ret else None
