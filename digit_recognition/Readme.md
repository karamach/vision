# Handwritten Digits Recognition

## Introduction

This codebase is a matlab implemention of a neural network for recognizing handwritten digits. 

## Model

A feed forward neural network has been implmeneted with configurable number of layers and hidden units. Various activations like sigmoid, tanh and relu have been implemented along with other approaches like batch normalization.

## Code

All the code is in the src folder. All parameters are at the top of the src/Train.m file. Training can be done by running the src/Train.m script. Testing can be done using the src/Test.m script. 

## Data

The code was trained and tested against sample data from the mnist digits database located in data folder. The data contains 3000 training and test samples (300 examples of each class), and 1000 validation samples (10 examples of each class). A sample input for all digits is shown below

![alt text](https://github.com/karamach/course_work/blob/master/cmu/topics_dl/digit_recognition/data/montage_1_10.png)


