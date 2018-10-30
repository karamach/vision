import warnings
from distutils.version import LooseVersion
import tensorflow as tf

class Utils:

    @staticmethod
    def check_gpu():
        if not tf.test.gpu_device_name():
            warnings.warn('[warn][no gpu found .. ]')
            return False
        
        print('[ok][gpu device name ..][val=%s]' % tf.test.gpu_device_name())
        return True

    @staticmethod
    def check_tf_version():
        if LooseVersion(tf.__version__) >= LooseVersion('1.0'):
            print('[error][tensor flow version old ..][version=%s]' % tf.__version__)
            return False
        
        print('[ok][tensor flow version ok ..][version=%s]' % tf.__version__)
        return True
