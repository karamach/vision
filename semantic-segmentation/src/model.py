import os.path
import tensorflow as tf

# Base VGG model extended with Fully convolutional layers for sem segmentation
class FCN_VGGModel:

    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'
    fcn_logits = 'logits'
    
    def __init__(self, sess, vgg_path):

        tf.saved_model.loader.load(sess, [self.vgg_tag], vgg_path)
        self.input_image = tf.get_default_graph().get_tensor_by_name(self.vgg_input_tensor_name)
        self.keep_prob = tf.get_default_graph().get_tensor_by_name(self.vgg_keep_prob_tensor_name)
        self.layer3_out = tf.get_default_graph().get_tensor_by_name(self.vgg_layer3_out_tensor_name)
        self.layer4_out = tf.get_default_graph().get_tensor_by_name(self.vgg_layer4_out_tensor_name)
        self.layer7_out = tf.get_default_graph().get_tensor_by_name(self.vgg_layer7_out_tensor_name)

    # 1x1 conv layer 7 vgg followed by upsampling
    # 1x1 conv layer 4 vgg
    # skip connection through element-wise addition followed by upsampling
    # 1x1 conv layer 3 vgg
    # skip connection through element-wise addition followed by upsampling
    def layers(self, num_classes):
        layer7a_out = tf.layers.conv2d(self.layer7_out, num_classes, 1, 
                                       padding='same', 
                                       kernel_initializer= tf.random_normal_initializer(stddev=0.01),
                                       kernel_regularizer= tf.contrib.layers.l2_regularizer(1e-3))
        layer4a_in1 = tf.layers.conv2d_transpose(layer7a_out, num_classes, 4, 
                                                 strides=(2, 2), 
                                                 padding='same', 
                                                 kernel_initializer=tf.random_normal_initializer(stddev=0.01), 
                                                 kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))
        layer4a_in2 = tf.layers.conv2d(self.layer4_out, num_classes, 1, 
                                       padding='same', 
                                       kernel_initializer=tf.random_normal_initializer(stddev=0.01),                                   
                                       kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))    
        layer4a_out = tf.add(layer4a_in1, layer4a_in2)    
        layer3a_in1 = tf.layers.conv2d_transpose(layer4a_out, num_classes, 4,  
                                                 strides=(2, 2), 
                                                 padding='same', 
                                                 kernel_initializer=tf.random_normal_initializer(stddev=0.01), 
                                                 kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))    
        layer3a_in2 = tf.layers.conv2d(self.layer3_out, num_classes, 1, 
                                       padding='same', 
                                       kernel_initializer=tf.random_normal_initializer(stddev=0.01), 
                                       kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))    
        layer3a_out = tf.add(layer3a_in1, layer3a_in2)    
        nn_last_layer = tf.layers.conv2d_transpose(layer3a_out, num_classes, 16,  
                                                   strides=(8, 8), 
                                                   padding='same', 
                                                   kernel_initializer=tf.random_normal_initializer(stddev=0.01), 
                                                   kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-3))

        logits = tf.reshape(nn_last_layer, (-1, num_classes), self.fcn_logits)
        return logits
        

