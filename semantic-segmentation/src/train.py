import sys
import os.path
import argparse
import re
from glob import glob
import shutil

import random
import numpy as np
import scipy.misc
import tensorflow as tf

from utils import Utils
from model import FCN_VGGModel

class Trainer:

    def __init__(self, input_model_dir, output_model_dir, training_data_dir, run_dir, num_classes, batch_size, epochs, image_shape=(256, 256)):
        self.input_model_dir = input_model_dir
        self.output_model_dir = output_model_dir
        self.training_data_dir = training_data_dir
        self.run_dir = run_dir
        self.num_classes = num_classes
        self.batch_size = batch_size
        self.epochs = epochs
        self.image_shape = image_shape
        self.learning_rate = .0009
        self.keep_prob = .5

    @staticmethod
    def optimize(logits, correct_label, learning_rate, num_classes):
        correct_label = tf.reshape(correct_label, (-1,num_classes))
        cross_entropy_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=correct_label))
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        train_op = optimizer.minimize(cross_entropy_loss)
        return train_op, cross_entropy_loss

    def train(self, sess, model, get_batches_fn, input_image, correct_label, train_op, cross_entropy_loss,
                 keep_prob, learning_rate):
        sess.run(tf.global_variables_initializer())    
        print("Training...")
        for i in range(self.epochs):
            print("EPOCH {} ...".format(i+1))
            for image, label in get_batches_fn(self.batch_size):
                _, loss = sess.run(
                    [train_op, cross_entropy_loss], 
                    feed_dict = {
                        input_image: image,
                        correct_label: label,
                        keep_prob: self.keep_prob,
                        learning_rate: self.learning_rate
                    }
                )
                print("Loss: = {:.3f}".format(loss))

    @staticmethod
    def  _preprocess(data_folder, image_shape):

        def get_batches_fn(batch_size):
            
            image_paths = glob(os.path.join(data_folder, 'raw', '*.png'))
            label_paths = {
                re.sub(r'.png.gt.png', '.png', os.path.basename(path)): path
                for path in glob(os.path.join(data_folder, 'gt_label', '*.png'))
            }
            background_color = np.array([0, 0, 0])
            random.shuffle(image_paths)
            
            for batch_i in range(0, len(image_paths), batch_size):
                images, gt_images = [], []

                for image_file in image_paths[batch_i:batch_i+batch_size]:
                    gt_image_file = label_paths[os.path.basename(image_file)]
  
                    image = scipy.misc.imread(image_file)[:, :, :3]
                    image = scipy.misc.imresize(image, image_shape)

                    gt_image = scipy.misc.imread(gt_image_file)[:, :, :3]
                    gt_image = scipy.misc.imresize(gt_image, image_shape)
                
                    gt_bg = np.all(gt_image == background_color, axis=2)
                    gt_bg = gt_bg.reshape(*gt_bg.shape, 1)
                    gt_image = np.concatenate((gt_bg, np.invert(gt_bg)), axis=2)
                    images.append(image)
                    gt_images.append(gt_image)

                yield np.array(images), np.array(gt_images)
              
        return get_batches_fn
                
    def run(self):
        with tf.Session() as sess:            
            vgg_path = self.input_model_dir
            model = FCN_VGGModel(sess, vgg_path)
            logits = model.layers(self.num_classes)
            get_batches_fn = Trainer._preprocess(self.training_data_dir, self.image_shape)
            correct_label = tf.placeholder(tf.int32, [None, None, None, self.num_classes], name='correct_label')
            learning_rate = tf.placeholder(tf.float32, name='learning_rate')
            train_op, cross_entropy_loss = Trainer.optimize(logits, correct_label, learning_rate, self.num_classes)            
            self.train(sess, model, get_batches_fn, model.input_image, correct_label, train_op, cross_entropy_loss,
                       model.keep_prob, learning_rate)
            saver = tf.train.Saver()
            if not os.path.exists(self.output_model_dir):
                os.makedirs(self.output_model_dir)
            return saver.save(sess, os.path.join(self.output_model_dir, 'model'))

if '__main__' == __name__:

    parser = argparse.ArgumentParser(description='semantic segmentation trainer')
    parser.add_argument('--input_model_dir', required=True)
    parser.add_argument('--output_model_dir', required=True)
    parser.add_argument('--data_dir', required=True)
    parser.add_argument('--run_dir', required=True)
    parser.add_argument('--num_classes', required=True, type=int)
    parser.add_argument('--batch_size', required=False, type=int, default=5)
    parser.add_argument('--epochs', required=False, type=int, default=10)    
    
    args = parser.parse_args()
    
    Utils.check_gpu()
    Utils.check_tf_version()
    Trainer(args.input_model_dir, args.output_model_dir, args.data_dir, args.run_dir, args.num_classes, args.batch_size, args.epochs).run()
    
