import os
import time
import hashlib
import requests
import json
from config.config import Config
from PySide2.QtWidgets import QMessageBox


class Tool(object):

    @staticmethod
    def get_md5(string):
        h1 = hashlib.md5()
        h1.update(string.encode(encoding='utf-8'))
        return h1.hexdigest()

    @staticmethod
    def show_msg_box(msg):
        box = QMessageBox()
        box.setText(msg)
        box.exec_()

    @staticmethod
    def client_login(app_id, security):
        try:
            data = {
                'appId': app_id,
                'security': security
            }
            r = requests.post('{}:{}/recognition/client/detail'.format(Config.host, Config.port), data=data)
            result = json.loads(r.text)
            if result['code'] == 200:
                return True, result['data']
            else:
                return False, None
        except Exception as e:
            print(e)
            return False, None

    @staticmethod
    def client_register(app_id, security):
        try:
            data = {
                'appId': app_id,
                'security': security
            }
            r = requests.post('{}:{}/recognition/client/save'.format(Config.host, Config.port), data=data)
            result = json.loads(r.text)
            if result['code'] == 200:
                return True, result['data']
            else:
                return False, result['msg']
        except Exception as e:
            print(e)
            return False, None

    @staticmethod
    def user_add(client_id, name, color):
        try:
            data = {
                'clientId': client_id,
                'name': name,
                'color': color
            }
            r = requests.post('{}:{}/recognition/user/save'.format(Config.host, Config.port), data=data)
            result = json.loads(r.text)
            if result['code'] == 200:
                return True, result['data']
            else:
                return False, result['msg']
        except Exception as e:
            print(e)
            return False, None

    @staticmethod
    def user_face_add(user_id, face):
        try:
            files = {'file': open(face, 'rb')}
            data = {
                'userId': user_id
            }
            r = requests.post('{}:{}/recognition/face/upload'.format(Config.host, Config.port), data=data, files=files)
            result = json.loads(r.text)
            if result['code'] == 200:
                return True, result['data']
            else:
                return False, result['msg']
        except Exception as e:
            print(e)
            return False, None

    @staticmethod
    def user_face_list(client_id):
        try:
            data = {
                "clientId": client_id
            }
            r = requests.post('{}:{}/recognition/user/allList'.format(Config.host, Config.port), data=data)
            result = json.loads(r.text)
            if result['code'] == 200:
                return result['data']
            else:
                return None
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def download_face(face_id, user_id):
        res = requests.get('{}:{}/recognition/face/download/{}'.format(Config.host, Config.port, face_id))
        cur_path, _ = os.path.split(os.path.realpath(__file__))
        path = cur_path + os.sep + "faces" + os.sep + user_id
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + os.sep + face_id + ".png", 'wb') as f:
            f.write(res.content)
