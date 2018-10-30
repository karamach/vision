import argparse
import os
import time
from glob import glob

import tensorflow as tf
import scipy.misc
import numpy as np

from utils import Utils
from model import FCN_VGGModel

import PyOpenImageIO as oiio
from buffer_ops import Pixels2BufOp, SelectChannelsByIndexOp, ConcatenateBufsOp

class Classifier:

    def __init__(self, model_path, data_dir, runs_dir, num_classes, image_shape=(256, 256)):
        self.model_path = model_path
        self.data_dir = data_dir
        self.runs_dir = runs_dir

        #TODO infer below members from model
        self.num_classes = num_classes
        self.image_shape = image_shape   

    @staticmethod
    def  _preprocess(sess, logits, keep_prob, image_pl, data_folder, image_shape):
        '''
        Returns:
            image_name, segmented_image_out, pixel_prob_out
        '''
        
        for image_file in glob(os.path.join(data_folder, '*.png')):
            image = scipy.misc.imread(image_file)[:, :, :3]   # strip alpha
            image = scipy.misc.imresize(image, image_shape)
            im_softmax = sess.run(
                [tf.nn.softmax(logits)], {
                    keep_prob: 1.0,
                    image_pl: [image]
                }
            )
            im_softmax = im_softmax[0][:, 1].reshape(image_shape[0], image_shape[1])            
            segmentation = (im_softmax > 0.5).reshape(image_shape[0], image_shape[1], 1)
            mask = np.dot(segmentation, np.array([[0, 255, 0, 127]]))
            mask = scipy.misc.toimage(mask, mode='RGBA')
            im = scipy.misc.toimage(image)
            im.paste(mask, box=None, mask=mask)
            yield os.path.basename(image_file), np.array(im), im_softmax.reshape(image_shape[0], image_shape[1], 1)

    @staticmethod
    def _create_exr(out_file, image, pixel_prob):
        [img, dense_seg] = Pixels2BufOp().op([image, pixel_prob],  ['uint8', 'float'])        
        [dense_seg] = SelectChannelsByIndexOp([0], ['Contamination_Prob']).op([dense_seg])
        [exr_out] = ConcatenateBufsOp().op([img, dense_seg])
        exr_out.write(out_file)
        
    @staticmethod
    def _do_inference(runs_dir, data_dir, sess, image_shape, logits, keep_prob, input_image):
        output_dir = os.path.join(runs_dir, str(time.time()))
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        image_outputs = Classifier._preprocess(
            sess, logits, keep_prob, input_image, os.path.join(data_dir, 'raw'), image_shape
        )

        for name, image, pixel_prob in image_outputs:
            print(name)
            test_img = scipy.misc.imread(os.path.join(data_dir, 'raw', name))
            test_img = scipy.misc.imresize(test_img, image_shape)
            alpha_channel = test_img[:, :, 3]
            image_with_alpha = np.dstack((image, alpha_channel))
            imgs_comb = np.hstack((test_img, image_with_alpha))
            scipy.misc.imsave(os.path.join(output_dir, name), imgs_comb)
            Classifier._create_exr(os.path.join(output_dir, name.replace('.png', '.exr')), image, pixel_prob)            
        
    def classify(self):
        with tf.Session() as sess:
            saver = tf.train.import_meta_graph(os.path.join(self.model_path, 'model.meta'))
            saver.restore(sess, tf.train.latest_checkpoint(self.model_path))
            keep_prob = tf.get_default_graph().get_tensor_by_name(FCN_VGGModel.vgg_keep_prob_tensor_name)
            input_image = tf.get_default_graph().get_tensor_by_name(FCN_VGGModel.vgg_input_tensor_name)
            logits = tf.get_default_graph().get_tensor_by_name(FCN_VGGModel.fcn_logits + ':0')
            Classifier._do_inference(self.runs_dir, self.data_dir, sess, self.image_shape, logits, keep_prob, input_image)


if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='semantic segmentation classifier')
    parser.add_argument('--model_dir', required=True)
    parser.add_argument('--data_dir', required=True)
    parser.add_argument('--run_dir', required=True)
    parser.add_argument('--num_classes', required=True, type=int)
    
    args = parser.parse_args()

    Utils.check_gpu()
    Utils.check_tf_version()    
    Classifier(args.model_dir, args.data_dir, args.run_dir, args.num_classes).classify()
    
