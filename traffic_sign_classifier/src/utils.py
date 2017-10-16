import pickle
import matplotlib.pyplot as plt
import math
import numpy as np
from matplotlib import gridspec

class Utils(object):

    # Load pickled data
    @staticmethod
    def load_data(training_file, validation_file, testing_file, sign_file):
        with open(training_file, mode='rb') as f:
            train = pickle.load(f)
        with open(validation_file, mode='rb') as f:
            valid = pickle.load(f)
        with open(testing_file, mode='rb') as f:
            test = pickle.load(f)
    
        X_train, y_train = train['features'], train['labels']
        X_valid, y_valid = valid['features'], valid['labels']
        X_test, y_test = test['features'], test['labels']
        sign_names = [line.rstrip().split(',') for line in open(sign_file).readlines()]
        sign_names = dict([(item[0], item[1]) for item in sign_names])
        return X_train, y_train, X_valid, y_valid, X_test, y_test, sign_names

    @staticmethod
    def show_images(images, labels, grid_size):
        gs = gridspec.GridSpec(grid_size[0], grid_size[1])
        gs.update(wspace=0.3, hspace=0.3, left=0.1, right=0.7, bottom=0.1, top=0.9)
        f = plt.figure(figsize=(20, 20))
        for i in range(len(images)):
            row = int(i / grid_size[1])
            col = (i % grid_size[1])
            s = f.add_subplot(gs[row, col])
            s.set_axis_off()
            s.imshow(images[i].squeeze())
            s.set_title(labels[i], fontsize=10)
        plt.show()

    # Display one image of each class.
    @staticmethod
    def visualize(images, labels, sign_names):
        unique_images, unique_labels, labels_set = [], [], set([])
        for count in range(len(images)):
            if labels[count] not in labels_set:
                unique_images.append(images[count])
                unique_labels.append(sign_names[str(labels[count])][0:20] + ',[' + str(labels[count]) + ']')
            labels_set.add(labels[count])
        Utils.show_images(unique_images, unique_labels, [math.ceil(len(unique_images) / 5), 5])
            
if '__main__' == __name__:
    X_train, y_train, X_valid, y_Valid, X_test, y_test, sign_names = Utils.load_data('../data/train.p', '../data/valid.p', '../data/test.p', '../data/signnames.csv')
    print("Number of training examples =", len(X_train))
    print("Number of validation examples =", len(X_valid))
    print("Number of testing examples =", len(X_test))
    print("Image data shape =", X_train[0].shape)
    print("Number of classes =", len(set(y_train)))

    Utils.visualize(X_train, y_train, sign_names)
    
    
