from skimage.feature import hog
import cv2

from utils import *
from params import *


class FeatureExtractor(object):

    def __init__(self, params):
        self.params = params

    def extract(self, img):
        pass


class HOGFeatureExtractor(FeatureExtractor):

    def __init__(self, params):
        super(HOGFeatureExtractor, self).__init__(params)

    def get_hog_features(self, img):
        return hog(img, orientations=self.params['orientation'], pixels_per_cell=(self.params['pixels_per_cell'],
                                                                                  self.params['pixels_per_cell']),
                   cells_per_block=(self.params['cells_per_block'], self.params['cells_per_block']),
                   feature_vector=self.params['feature_vector'], visualise=self.params['visualise'])

    def extract(self, img):
        hog_features = []
        if self.params['channel'] == 'ALL':
            for channel in range(img.shape[2]):
                # hog_feature, img = self.get_hog_features(img[:, :, channel])
                # Utils.show_image(img)
                hog_feature = self.get_hog_features(img[:, :, channel])
                hog_features.append(hog_feature)
            hog_features = np.ravel(hog_features)
        else:
            # hog_features, img = self.get_hog_features(img[:, :, int(self.params['channel'])])
            hog_features = self.get_hog_features(img[:, :, int(self.params['channel'])])
            #Utils.show_image(img, cmap='gray')
        return hog_features


class ColorFeatureExtractor(FeatureExtractor):

    def __init__(self, params):
        super(ColorFeatureExtractor, self).__init__(params)

    def bin_spatial(self, img):
        return cv2.resize(img, self.params['spatial_size']).ravel()

    # Compute histogram of rgb channels separately and concatenate into a single feature vector
    def color_hist(self, img):
        rhist = np.histogram(img[:, :, 0], bins=self.params['bins'], range=self.params['range'])
        ghist = np.histogram(img[:, :, 1], bins=self.params['bins'], range=self.params['range'])
        bhist = np.histogram(img[:, :, 2], bins=self.params['bins'], range=self.params['range'])
        return np.concatenate((rhist[0], ghist[0], bhist[0]))

    def extract(self, img):
        feature_img = Utils.convert_image(img, self.params['src_space'], self.params['dst_space'])
        spatial_features = self.bin_spatial(feature_img)
        # plt.plot(spatial_features)
        # plt.show()
        hist_features = self.color_hist(feature_img)
        # plt.plot(hist_features)
        # plt.show()
        return np.concatenate((spatial_features, hist_features))


class FeatureExtractorFactory(FeatureExtractor):
    def __init__(self, params):
        super(FeatureExtractorFactory, self).__init__(params)
        self.featureExtractors = {
            'color_feature': ColorFeatureExtractor(params),
            'hog_feature': HOGFeatureExtractor(params)
        }

    def extract(self, img):
        features = []
        for fe in self.featureExtractors.keys():
            if fe in self.params:
                features.append(self.featureExtractors[fe].extract(img))

        return np.concatenate(features)


def test_hog_features(params, file):
    img = Utils.read_image(file)
    fe = HOGFeatureExtractor(params)
    fe = fe.extract(img)


def test_color_features(params, file):
    img = Utils.read_image(file)
    fe = ColorFeatureExtractor(params)
    fe = fe.extract(img)


def test_factory(params):
    img = Utils.read_image('../test_images/test1.jpg')
    fe = FeatureExtractorFactory(params)
    fe.extract(img)

if "__main__" == __name__:

    # Test hog features
    #test_hog_features(global_params, '../train_images/vehicles_smallset/cars1/1.jpeg')

    # Test color features
    test_color_features(global_params, '../train_images/vehicles_smallset/cars1/1.jpeg')

    # Test factory features
    #test_factory(global_params)



