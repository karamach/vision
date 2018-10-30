# Semantic Segmentation for contaminated insulators

### Intro

Module for training a VGG based FCN for detecting pixel level contamination for insulators

### Data

- Sample training data can be downloaded from gs://karamach-insulators/semantic_segmentation/training
- Sample test data can be downloaded from gs://karamach-insulators/semantic_segmentation/testing
- Base vgg model can be downloaded from gs://karamach-insulators/semantic_segmentation/model/vgg
- Sample output can be found in gs://karamach-insulators/semantic-segmentation/run
- Sample fcn model can be found in gs://karamach-insulators/semantic-segmentation/model/fcn

### Prerequisites

- Download above data locally
- Setup virtual env using the requirements.txt file

### Train

- Vgg model downloaded to /tmp/semseg/model/vgg
- Training data downloaded to /tmp/semseg/training
- Run dir is /tmp/semseg/run

```
source <venv>/bin/activate
cd <monorepo>/vision/ml/semantic-segmentation/src
export PYTHONPATH=.
python train.py --input_model_dir /tmp/semseg/model/vgg --output_model_dir /tmp/semseg/model/fcn --data_dir /tmp/semseg/training --run_dir /tmp/semseg/run  --num_classes 2 --batch_size 5 --epochs 10 
```

### Inference

- Testing data downloaded to /tmp/semseg/testing
- Run dir is /tmp/semseg/run
- Trained model dir is /tmp/semseg/model/fcn

```
source <venv>/bin/activate
cd <monorepo>
bazel build -c opt //third_party/oiio:PyOpenImageIO.so
cd <monorepo>/vision/ml/semantic-segmentation/src
export PYTHONPATH=.:<monorepo>/bazel-bin/third_party/oiio/
python classify.py --model_dir /tmp/semseg/model/fcn --data_dir /tmp/semseg/testing --run_dir /tmp/semseg/run  --num_classes 2
```

Output is generated in png and exr format in the run folder. Png output comprises of the raw and segmented image placed side by side. Exr output comprises of original image along with a layer named Contamination_Prob storing probabilities for each pixel.

### Sample output

![image1](vision/ml/semantic-segmentation/images/f1087e93a417793a2143c6fb6ee556d2b6ad9df5.png)
![image2](vision/ml/semantic-segmentation/images/bc35a7ebb1c0404ff5e0c8cab1471d8b2d2ed3e1.png)

### Todo

- Improve segmentation quality