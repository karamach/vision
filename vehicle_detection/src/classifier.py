from sklearn.svm import LinearSVC


class Classifier(object):
    def __init__(self):
        pass

    def train(self, x_train, y_train):
        pass

    def score(self, x_test, y_test):
        pass

    def predict(self, x_test):
        pass


class SVMClassifier(Classifier):

    def __init__(self):
        self.svc = LinearSVC()

    def train(self, x_train, y_train):
        self.svc.fit(x_train, y_train)

    def predict(self, x_test):
        return self.svc.predict(x_test)

    def score(self, x_test, y_test):
        return self.svc.score(x_test, y_test)


