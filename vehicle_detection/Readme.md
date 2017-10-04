# Vehicle Detection

## Introduction

The codebase implements a classifier for detecting vehicles in images. Histogram of Oriented Gradients and Color features on a labeled training set of images are used to train an SVM classifier. The output is then passed through a sliding window based search technique to detect potential candiates. Heat map based techniques are applied to the potential candidates to further reduce false positives and track vehicles.

## Feature Extraction

Feature Extraction is done on both positive and negative image cases. An example of both types (one with car and one without car) can be seen below. The datasets used for training were non-vehicles/Extras, non-vehicles/GTI,  vehicles/GTI_Far, vehicles/GTI_left, vehicles/GTI_Middle_close, vehicles/GTI_Right and vehicles/KTTI_extracted.Two sets of features were used namely Histogram of Oriented Gradients and Color based spatial binning and histogram of color channels. Here is a link to the [data] (https://drive.google.com/open?id=0B3EkEy76sbi6eXJ2ZVhzanhYN0U)

![alt](https://github.com/karamach/vision/blob/karamach/vehicle_detection/vehicle_detection/images/train_data.png){:height="36px" width="36px"}

## Histogram of oriented gradients

Histogram of oriented gradients is computed for  both positive (images with cars) and negative cases(no cars). Hog function from skimage.feature is used to compute the Hog features. In this project, hog features are computed for all channels. Some of the parameters that govern hog features are orientations, number of pixels to be considered per cell and number of cells per block. Various parameters and color channels to understand which combination works better. Below is an example HOG image for Channel 1 and the corresponding original image. The parameters used for this were orientation=9, pixels_per_cell=8, cells_per_block=2, channel=0.

## Color based Features

For color based features, spatial binning and color histogram for each of the channels was used. The spatial binned and color histogram for the image above are shown below.

## Classifier

Once the feature extraction is done, the next step is to use a classifier to classify the images based on the features. For this, an SVM classifier was used. The LinearSVC from sklearn was used for the SVM.  The code for constructing the classifier and its API is in classifer.py lines 1-30. The classifier interface provides three functions namely train, test and predict. Training is done by extracting features from both positive and negative images. The features are then scaled using a Standard Scaler and then split into train and test datasets. The classifier is then trained on the train dataset and evaluated on the test dataset. The accuracy score came out to be roughly 98. 

## Sliding Window Search

Once the training is done, the classifier was used to test the incoming images to find vehicles in the image. For doing this, a sliding window search was implemented. The sliding window is implemented by searching the test images with increasing sized windows with some overlap. For efficient search, only the bottom portion of the test image is searched, since, the likelihood of a vehicle appearing in the top portion is pretty low. Some parameters that govern this search are window_size, x_start_stop, y_start_stop, xy_overlap. The values of these parameters can be seen in the params.py file lines 33-38.  Some of the windows that were generated is shown below.

In terms of features, the final version uses HOGFeatures with all channels along with Color histogram and spatial bin features.
Below are examples of the candidate boxes that were generated for some of the images. The code for generating candidate boxes is in pipeline.py lines 48-54

## Video

For handling false positives, a heatmap based approach was implemented. The heatmap keeps track of pixels that appear in boxes in multiple frames and applies a thresholding to pick blobs that appear in multiple frames. For applying thresholding, a percentage of the maximum count was used. scipy.ndimage.measurements.label() was used to identify the blobs and they were used to detect the vehicles. Some frames and the corresponding heatmaps are shown below:

## Future work

The most challenging part was towards the last part of the pipeline to adjust the parameters to reduce false positives while at the same time ensuring good classification and bounding box accuracy. A lot of time had to be spent tuning the various parameters to achieve some accuracy and still the output is not as accurate as I would have liked it to be. One of the situations the pipeline might face is if the cars make rapid movements or if the current car slows down suddenly, then the tracking code might not work as robustly. This needs to be handled in some way. Maybe in future some other approaches like deep learning etc can be explored. I also shall work on improving the performance of the pipeline and see how it can be done in real time.


![alt text](https://github.com/karamach/course_work/blob/master/cmu/topics_dl/digit_recognition/data/montage_1_10.png)

