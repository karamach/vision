# Vehicle Detection

## Introduction

The codebase implements a classifier for detecting vehicles in images. Histogram of Oriented Gradients and Color features on a labeled training set of images are used to train an SVM classifier. The output is then passed through a sliding window based search technique to detect potential candiates. Heat map based techniques are applied to the potential candidates to further reduce false positives and track vehicles.

## Feature Extraction

Feature Extraction is done on both positive and negative image cases. An example of both types (one with car and one without car) can be seen below. The datasets used for training were non-vehicles/Extras, non-vehicles/GTI,  vehicles/GTI_Far, vehicles/GTI_left, vehicles/GTI_Middle_close, vehicles/GTI_Right and vehicles/KTTI_extracted.Two sets of features were used namely Histogram of Oriented Gradients and Color based spatial binning and histogram of color channels. Here is a link to the   [data](https://drive.google.com/open?id=0B3EkEy76sbi6eXJ2ZVhzanhYN0U)

![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/train_data.png)

## Histogram of oriented gradients

Histogram of oriented gradients is computed for  both positive (images with cars) and negative cases(no cars) for all channels.  Some of the parameters that govern hog features are orientations, number of pixels to be considered per cell and number of cells per block.  Below is an example HOG image for Channel 1 and the corresponding original image. The parameters used for this were orientation=9, pixels_per_cell=8, cells_per_block=2, channel=0.

![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/hog.png)

## Color based Features

For color based features, spatial binning and color histogram for each of the channels was used. The spatial binned and color histogram for the image above are shown below.

![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/hist.png)

## Classifier

Once the feature extraction is done, the next step is to use a classifier to classify the images based on the features. For this, an SVM classifier was used. The LinearSVC from sklearn was used for the SVM.  The code for constructing the classifier and its API is in classifer.py lines 1-30. The classifier interface provides three functions namely train, test and predict. Training is done by extracting features from both positive and negative images. The features are then scaled using a Standard Scaler and then split into train and test datasets. The classifier is then trained on the train dataset and evaluated on the test dataset. The accuracy score came out to be roughly 98. 

## Sliding Window Search

A sliding window search is used to locate the object within the image with increasing sized windows with some overlap. For efficient search, only the bottom portion of the image is searched, since, the likelihood of a vehicle appearing in the top portion is pretty low. Some parameters that govern this search are window_size, x_start_stop, y_start_stop, xy_overlap.  Some of the windows that were generated is shown below.

![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/sliding_window.png)

In terms of features, the final version uses HOGFeatures with all channels along with Color histogram and spatial bin features.
Below are examples of the candidate boxes that were generated for some of the images.

![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/candidate_boxes.png)

For handling false positives, a heatmap based approach was implemented. The heatmap keeps track of pixels that appear in boxes in multiple frames and applies a thresholding to pick blobs that appear in multiple frames. For applying thresholding, a percentage of the maximum count was used. Some frames and the corresponding heatmaps are shown below:

![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/hm1.png)
![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/hm2.png)
![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/hm3.png)
![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/chm.png)
![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/bb.png)

## Video

![alt](https://github.com/karamach/vision/blob/master/vehicle_detection/images/vid.png)

[link to video](https://drive.google.com/file/d/0B5e5oUCOCYhANURIbG1VM1djTzQ/view)

## Future work

A key challenge was to adjust the parameters to reduce false positives while at the same time ensuring good classification and bounding box accuracy. Situations like rapid movements or slows downs need to be handled better.

