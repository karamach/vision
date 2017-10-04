from scipy.ndimage.measurements import label

from moviepy.editor import VideoFileClip

from classifier import *
from label_tracker import *
from feature_extractor import *
from utils import *
from params import *


class Pipeline(object):

    def __init__(self, params, classifier=None, fe=None):
        self.classifier = SVMClassifier() if classifier is None else classifier
        self.fe = FeatureExtractorFactory(params) if fe is None else fe
        self.tracker = LabelTracker(params)
        self.params = params
        self.scaler = None

    def search_windows(self, img, windows):
        on_windows = []
        for window in windows:
            test_img = cv2.resize(img[window[0][1]:window[1][1], window[0][0]:window[1][0]], (64, 64))
            if self.predict(test_img) == 1:
                on_windows.append(window)
        return on_windows

    def train(self, pos_files, neg_files):
        pos_features, neg_features = [], []
        [pos_features.append(self.fe.extract(Utils.read_image(img_file))) for img_file in pos_files]
        [neg_features.append(self.fe.extract(Utils.read_image(img_file))) for img_file in neg_files]

        scaled_x, self.scaler = Utils.feature_scaler((pos_features, neg_features))
        y = np.hstack((np.ones(len(pos_features)), np.zeros(len(neg_features))))
        x_train, x_test, y_train, y_test = Utils.split_data(scaled_x, y, .2, np.random.randint(0, 100))

        # Train classifier
        self.classifier.train(x_train, y_train)
        return self.classifier.score(x_test, y_test)

    def predict(self, img):
        features = self.fe.extract(img)
        test_features = self.scaler.transform(np.array(features).reshape(1, -1))
        return self.classifier.predict(test_features)

    def test(self, img):
        windows = []
        for i in range(self.params['window_beg_size'], self.params['window_end_size'], self.params['window_incr_size']):
            windows = windows + Utils.slide_window(img, self.params['x_start_stop'], self.params['y_start_stop'], (i, i),
                                                   self.params['xy_overlap'])
        #Utils.show_image(Utils.draw_boxes(np.copy(img), windows))

        candidates = self.search_windows(img, windows)
        out = {}
        if 'label' in self.params['out_mode'] or 'heat_map' in self.params['out_mode']:
            heat_map = self.tracker.track_label(img, candidates)
            labels = label(np.clip(heat_map, 0, 255))
            out['heat_map'] = labels[0]
            out['label'] = Utils.draw_labeled_bboxes(np.copy(img), labels)
            out['last_label'] = self.tracker.labels[-1]
        if 'candidate' in self.params['out_mode']:
            out['candidate'] = Utils.draw_boxes(np.copy(img), candidates)
        return out


def load_data():
    pos_data = Utils.list_files(global_params['train_pos'].split(','))
    neg_data = Utils.list_files(global_params['train_neg'].split(','))
    return pos_data, neg_data


def test_train(pipeline, pos_data, neg_data):
    score = pipeline.train(pos_data, neg_data)
    print('Training score: ', score)


def test_predict_image(pipeline, test_img):
    boxed_img = pipeline.test(test_img)
    return boxed_img


def test_predict_video(pipeline, in_video, out_video):
    clip = VideoFileClip(in_video)
    output_clip = clip.fl_image(pipeline.test)
    output_clip.write_videofile(out_video, audio=False)


if '__main__' == __name__:
    pipeline = Pipeline(global_params)
    pos_data, neg_data = load_data()

    print('Training')
    test_train(pipeline, pos_data, neg_data)

    # print('Testing Image')
    test_images = Utils.list_files([global_params['test_data_in']])
    test_images = sorted(test_images, key=lambda file: int((file.split('_')[-1]).split('.')[0]))
    for idx, img_path in enumerate(test_images[200:400]):
        print('Testing image .. ', img_path)
        out = test_predict_image(pipeline, Utils.read_image(img_path))
        img_path = img_path.replace(global_params['test_data_in'], global_params['test_data_out'])
        Utils.write_image(out['label'], img_path + '_label.jpg')
        Utils.write_image(out['candidate'], img_path + '_candidate.jpg')
        Utils.write_image(out['heat_map'], img_path + '_heat_map.jpg')
        Utils.write_image(out['last_label'], img_path + '_last_label.jpg')

    # print('Testing Video')
    # test_predict_video(pipeline, "../project_video.mp4", "../project_video_out.mp4")

