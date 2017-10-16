# Traffic Sign Recognition

## Introduction

The code implements a simple CNN to classifiy images into traffic sign labels. The lenet architecture is used for the CNN.

[//]: # (Image References)

[image1]: ./images/visualization1.png "Visualization1"
[image2]: ./images/visualization2.png "Visualization2"
[image3]: ./images/visualization3.png "Visualization3"
[image4]: ./images/stop_preproc.png "stop preproc"
[image5]: ./images/stop_postproc.png "stop postpoc"
[image6]: ./images/img1.jpeg "img1"
[image7]: ./images/img2.jpeg "img2"
[image8]: ./images/img3.jpeg "img3"
[image9]: ./images/img4.jpeg "img4"
[image10]: ./images/img5.jpeg "img5"


## Data Set

The input is pickled as train, valid and test sets. 

Below are some stats for the dataset used for train and test
* The size of training set is 34799
* The size of test set is 12630
* The shape of a traffic sign image is (32, 32, 3)
* The number of unique classes/labels in the data set is 43

The visualization below contains one  image from each label category

![alt text][image1]
![alt text][image2]
![alt text][image3]

Some preprocessing was done on the image to resize it to a 32x32 image followed by normalization. Below is an  example of a traffic sign image before and after preprocessing.

![alt text][image4]
![alt text][image5]


## CNN Model

The CNN model is a standard Lenet architecture with the following layers

| Layer         		|     Description	        					|
|:---------------------:|:---------------------------------------------:|
| Input         		| 32x32x3 RGB image   							|
| Convolution 5x5     	| 1x1 stride, valid padding, outputs 28x28x6 	|
| RELU					|												|
| Max pooling	      	| 2x2 stride, valid padding,  outputs 14x14x6   |
| Convolution 5x5	    | 1x1 stride, valid padding, outputs 10x10x16 	|
| Fully connected		| Output 120        							|
| Fully connected		| Output 84                                     |
| Fully connected		| Output 43	                                    |
| Softmax    			|												|

The standard Lenet architecture was tried for this problem with some changes to incorporate 3 color channels. The architecture consists of 2 convolution layers with a max pooling layer in between, followed by 2 fully connected layers. A non shared weight model was used where in each subsection of the image had a different set of weights for a given  convolution. This intuitively should work better for this problem since, the traffic signs are the main focus in the image and the edges detected on one side are not equivalent to the edges detected on the other side.

## Training

The model was trained with an Adam optimizer with a softmax cross entropy loss,  for 50 Epochs with a batch size of 128 and a learning rate of .0009. A couple of learning
rates were tried and .0009 seemed to give the best result.

## Results

Initially with random normal distributions for the weights, the accuracy was very low. Once this was changed to truncated normal, the accuracy started improving. The final training , validation and test accuracies were 100, 95.2 and 93.5. Lower test accuracy could imply some overfitting.  Regularization or dropout could improve the model.

The system was tried on  five random traffic images from the web namely: pedestrian, general caution, speed limit 60, speed limit 30 and road work. 

![alt text][image6] ![alt text][image7] ![alt text][image8]
![alt text][image9] ![alt text][image10]

Here are the results of the prediction:

| Image			        |     Prediction	        					|
|:---------------------:|:---------------------------------------------:|
| Pedestrian     		| General caution								|
| General Caution		| General caution    							|
| Speed limit 60		| Speed limit 30								|
| Speed limit 30  		| Speed limit 30    			 				|
| Road work    		    | Road work         							|


The model was able to correctly guess 3 of the 5 traffic signs, which gives an accuracy of 60%. This is actually worse than the test set accuracy which was beyond 90%
The general caution, Speed limit 30 and road work images were predicted correctly but, the pedestrians and  speed limit 60 labels were predicted incorrectly. The pedestrian label was incorrectly predicted as general caution.  This could be explained by the fact that both signs look very similar with  triangular red border and a black center. 
The same reasoning is also true for the speed limit 60 sign which was predicted as speed limit 30.

Following is the true label ids and label text for reference.

27 : pedestrian
18 : general caution
3  : speed limit 60
1  : speed limit 30
25 : road work

The top k softmax probabilites are analyzed below. The first sign was for pedestrian but was incorrectly predicted as general caution with high probability. The remaining probabilities are pretty low

| Probability         	|     Prediction	        					|
|:---------------------:|:---------------------------------------------:|
| 1         			| general caution       						|
| 2.7e-8  				| Speed limit 20								|
| 1.5e-9    			| Wild animal									|
| 1.4e-9      			| Vehicles  					 				|
| 3.6e-10			    | Speed limit 30      							|

The second sign was for general caution and  was correctly predicted so. 

| Probability         	|     Prediction	        					|
|:---------------------:|:---------------------------------------------:|
| .9         			| general caution       						|
| 2.1e-3  				| Speed limit 30								|
| 1.8e-5    			| Bicycle   									|
| 5.4e-8      			| Speed limit 20    			 				|
| 5.4e-11			    | Bumpy road         							|

The third sign was for speed limit 60  but  was incorrectly predicted as priority. 

| Probability         	|     Prediction	        					|
|:---------------------:|:---------------------------------------------:|
| .9         			| priority                 						|
| .09     				| end of no passing								|
| 1.3e-6    			| Slippery road     							|
| 1.1e-6      			| turn left ahead    			 				|
| 6.2e-9			    | keep right          							|

The fourth sign was for speed limit 30  and  was correctly predicted.

| Probability         	|     Prediction	        					|
|:---------------------:|:---------------------------------------------:|
| 1          			| speed limit 30        						|
| 2.6e-14 				| double curve  								|
| 1.e-14    			| wild animals cross  							|
| 6.8e-17      			| road work         			 				|
| 4.9e-17			    | speed limit 50       							|

The fifth sign was for road work  and  was correctly predicted.

| Probability         	|     Prediction	        					|
|:---------------------:|:---------------------------------------------:|
| 1          			| road work             						|
| 4.9e-8 				| bicycle crossing								|
| 6.9e-10    			| go straight or right  						|
| 5.7e-10      			| wild animals crossing 		 				|
| 3.3e-12			    | speed limit 100     							|
