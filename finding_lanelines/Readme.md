# Lane line detection

## Introduction

The code uses hough transforms and canny edge detector to detect lane lines on images of roads.

[//]: # (Image References)

[image1]: ./output/laneLines_thirdPass.jpg "lane lines 1"
[image2]: ./output/line-segments-example.jpg "lane lines 2"
[image3]: ./output/solidWhiteRight.jpg "solid white right"
[image4]: ./output/solidYellowCurve.jpg "solid yellow curve"
[image5]: ./output/solidYellowCurve2.jpg "solid yellow curve2"
[image6]: ./output/solidYellowLeft.jpg "solid yellow left"
[image7]: ./output/whiteCarLaneSwitch.jpg "white car lane switch"
[image8]: ./output/output_video.png 


## Data

Data can be downloaded [here](https://drive.google.com/open?id=0B5e5oUCOCYhAZERNODc4Ul9sdjQ)

## Approach

The images were first preprocessed using grayscaling and gaussian smoothing. These are passed through a Canny Edge Detector to detect edges and a region of interest is picked in the image based on the knowledge of where the lane lines are found on images. A final hough transform then gives the exact lane lines.

## Results

Some results on lane line images are shown below with the lane lines marked in red. The accuracy of the algorithm seems to depend a lot on the hyperparameters like
region of interest boundaries, hough min line length and max line gap, thresholds and limits on the kind of lines (based on slopes and coordinates) to be considered as candidates for the final lanes. One improvement could be to develop a framework to autotune these parameters based on large amount of tagged data. The current algorithm was manually tuned for steep turns or curves in the road, effects like shadows and less dark roads that make it difficult to detect lane lines.

![alt text][image1] ![alt text][image2] ![alt text][image3]
![alt text][image4] ![alt text][image5] ![alt text][image6]
![alt text][image7] 

A sample video output is shown below. For generating the video, ffmpeg needs to be in the src folder which can be downloaded from [here](https://www.ffmpeg.org/)

![alt text][image8] 

[video link](https://youtu.be/gtlieREidm4)