import os
import cv2
import numpy as np


class HaarcascadeDetective(object):
    def __init__(self):
        self.cascade_classifier = cv2.CascadeClassifier()

    def get_face_classifier(self):
        try:
            cur_path = os.path.split(os.path.realpath(__file__))[0]
            self.cascade_classifier.load(
                cur_path + os.path.sep + 'haarcascades' + os.path.sep + 'haarcascade_frontalface_default.xml')
        except Exception as e:
            print(e)
        return self

    def get_faces(self, image):
        gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
        faces = self.cascade_classifier.detectMultiScale(gray, 1.2, 10)
        for (x, y, w, h) in faces:
            yield image[y:y + h, x:x + w]

    def get_faces_position(self, image):
        gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
        faces = self.cascade_classifier.detectMultiScale(gray, 1.3, 10)
        return faces
