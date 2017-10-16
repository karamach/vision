import numpy as np
import cv2
import tensorflow as tf

from utils import *

# preprocessing (normalization, converting to grayscale)
def preproc(x, y):

    # Resize img
    def resize(img, h, w):
        return cv2.resize(img, (w, h))

    # Normalize image within the range 0 and 1
    def normalize(image):
        return cv2.normalize(image, np.zeros(image.shape), alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

    return (np.array([normalize(resize(img, 32, 32)) for img in x]), y)


def LeNet(x):
    # Arguments used for tf.truncated_normal, randomly defines variables for the weights and biases for each layer
    mu = 0
    sigma = 0.1

    # Layer 1: Convolutional. Input = 32x32x3. Output = 28x28x6.
    wc1 = tf.Variable(tf.truncated_normal([5, 5, 3, 6], mean=mu, stddev=sigma))
    bc1 = tf.Variable(tf.truncated_normal([6], mean=mu, stddev=sigma))
    c1 = tf.nn.conv2d(x, wc1, strides=[1, 1, 1, 1], padding='VALID')
    c1 = tf.nn.bias_add(c1, bc1)
    c1 = tf.nn.relu(c1) # Activation.

    # Pooling. Input = 28x28x6. Output = 14x14x6.
    c1 = tf.nn.max_pool(c1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')

    # Layer 2: Convolutional. Output = 10x10x16.
    wc2 = tf.Variable(tf.truncated_normal([5, 5, 6, 16], mean=mu, stddev=sigma))
    bc2 = tf.Variable(tf.truncated_normal([16], mean=mu, stddev=sigma))
    c2 = tf.nn.conv2d(c1, wc2, strides=[1, 1, 1, 1], padding='VALID')
    c2 = tf.nn.bias_add(c2, bc2)
    c2 = tf.nn.relu(c2) # Activation.

    # Pooling. Input = 10x10x16. Output = 5x5x16.
    c2 = tf.nn.max_pool(c2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')

    # Flatten. Input = 5x5x16. Output = 400.
    cf2 = tf.contrib.layers.flatten(c2)

    # Layer 3: Fully Connected. Input = 400. Output = 120.
    wfc1 = tf.Variable(tf.truncated_normal([400, 120], mean=mu, stddev=sigma))
    bfc1 = tf.Variable(tf.truncated_normal([120], mean=mu, stddev=sigma))
    fc1 = tf.add(tf.matmul(cf2, wfc1), bfc1)
    fc1 = tf.nn.relu(fc1)    # Activation.

    # Layer 4: Fully Connected. Input = 120. Output = 84.
    wfc2 = tf.Variable(tf.truncated_normal([120, 84], mean=mu, stddev=sigma))
    bfc2 = tf.Variable(tf.truncated_normal([84], mean=mu, stddev=sigma))
    fc2 = tf.add(tf.matmul(fc1, wfc2), bfc2)
    fc2 = tf.nn.relu(fc2)  # Activation.

    # Layer 5: Fully Connected. Input = 84. Output = 43.
    wfc3 = tf.Variable(tf.truncated_normal([84, 43], mean=mu, stddev=sigma))
    bfc3 = tf.Variable(tf.truncated_normal([43], mean=mu, stddev=sigma))
    fc3 = tf.add(tf.matmul(fc2, wfc3), bfc3)

    # Logits
    logits = fc3
    return logits

if '__main__' == __name__:
    X_train, y_train, X_valid, y_valid, X_test, y_test, sign_names = Utils.load_data('../data/train.p', '../data/valid.p', '../data/test.p', '../data/signnames.csv')
    X_train, y_train = preproc(X_train, y_train)
    X_valid, y_valid = preproc(X_valid, y_valid)
    X_test, y_test = preproc(X_test, y_test)

    visualize(X_train, y_train, sign_names)
