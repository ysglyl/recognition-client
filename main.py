import collections
import os
import shutil
from threading import Thread
import time

import cv2
import numpy as np
from PySide2.QtCore import QRect, Qt, QSize
from PySide2.QtGui import QIcon, QFont, QImage, QPixmap
from PySide2.QtWidgets import QMainWindow, QDesktopWidget, QLabel, QPushButton, QCheckBox, QFrame, QAction, QMessageBox

from manage import ClientLogin
from settings import ServerSetting, DimensionSetting
from user import AddUser, AddUserFace
from help import ClientRegister
from config.config import Config
from haarcascade_detective import HaarcascadeDetective
from db.db_helper import DbHelper
from tool import Tool


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.users = None
        self.camera = None
        self.playing = False
        self.frames = None
        self.capturing = False
        self.capture_frame = None
        self.flag_recognize = False
        self.model = None

        # key:user_id, value:((x,y,w,h),name,color,welcome_msg)
        self.recognized_faces = {}

        self.lbl_viewer = None
        self.btn_open_camera = None
        self.btn_close_camera = None
        self.btn_open_video = None
        self.btn_close_video = None
        self.cb_recognize = None
        self.btn_sync_face = None
        self.btn_capture = None
        self.lbl_capture_pic = None
        self.btn_capture_save = None

        self.init_ui()
        self.train_model()
        if os.path.exists('faces{}tmp'.format(os.sep)):
            shutil.rmtree('faces{}tmp'.format(os.sep))

    def init_ui(self):
        self.setFixedSize(Config.width, Config.height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowIcon(QIcon('icons/icon.png'))
        self.setWindowTitle('客户端')

        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        manage_menu = menu_bar.addMenu("信息管理")
        client_login_action = manage_menu.addAction("服务器连接")
        client_login_action.triggered.connect(self.manage_client_login)
        user_action = manage_menu.addAction("用户管理")
        user_action.triggered.connect(self.manage_user)

        setting_menu = menu_bar.addMenu("设置")
        server_action = setting_menu.addAction("服务器")
        server_action.triggered.connect(self.setting_server)
        dimension_action = setting_menu.addAction("窗口尺寸")
        dimension_action.triggered.connect(self.setting_dimension)

        help_menu = menu_bar.addMenu("帮助")
        client_register_action = help_menu.addAction("客户端注册")
        client_register_action.triggered.connect(self.help_client_register)

        status_bar = self.statusBar()
        status_bar.showMessage("欢迎使用客户端")

        self.lbl_viewer = QLabel(self)
        self.lbl_viewer.setGeometry(QRect(10, 26, Config.width - 130, Config.height - 60))
        self.lbl_viewer.setText('没有图像')
        font = QFont()
        font.setPointSize(20)
        self.lbl_viewer.setFont(font)
        self.lbl_viewer.setAlignment(Qt.AlignCenter)
        self.lbl_viewer.setFrameShape(QFrame.StyledPanel)

        self.btn_open_camera = QPushButton(self)
        self.btn_open_camera.setGeometry(QRect(Config.width - 110, 10, 100, 26))
        self.btn_open_camera.setText('打开摄像头')
        self.btn_open_camera.clicked.connect(self.btn_click)

        self.btn_close_camera = QPushButton(self)
        self.btn_close_camera.setGeometry(QRect(Config.width - 110, 46, 100, 26))
        self.btn_close_camera.setText('关闭摄像头')
        self.btn_close_camera.setDisabled(True)
        self.btn_close_camera.clicked.connect(self.btn_click)

        self.btn_open_video = QPushButton(self)
        self.btn_open_video.setGeometry(QRect(Config.width - 110, 82, 100, 26))
        self.btn_open_video.setText('播放视频')
        self.btn_open_video.clicked.connect(self.btn_click)

        self.btn_close_video = QPushButton(self)
        self.btn_close_video.setGeometry(QRect(Config.width - 110, 118, 100, 26))
        self.btn_close_video.setText('停止播放')
        self.btn_close_video.setDisabled(True)
        self.btn_close_video.clicked.connect(self.btn_click)

        self.cb_recognize = QCheckBox(self)
        self.cb_recognize.setText('启动识别')
        self.cb_recognize.setDisabled(True)
        self.cb_recognize.setGeometry(QRect(Config.width - 108, 154, 100, 26))
        self.cb_recognize.clicked.connect(self.cb_click)

        self.btn_sync_face = QPushButton(self)
        self.btn_sync_face.setGeometry(QRect(Config.width - 110, 190, 100, 26))
        self.btn_sync_face.setText("同步数据")
        self.btn_sync_face.clicked.connect(self.btn_click)

        self.btn_capture = QPushButton(self)
        self.btn_capture.setGeometry(QRect(Config.width - 110, Config.height - 200, 100, 26))
        self.btn_capture.setText('截屏')
        self.btn_capture.setDisabled(True)
        self.btn_capture.clicked.connect(self.btn_click)

        self.lbl_capture_pic = QLabel(self)
        self.lbl_capture_pic.setGeometry(QRect(Config.width - 110, Config.height - 160, 100, 100))
        self.lbl_capture_pic.setAlignment(Qt.AlignCenter)
        self.lbl_capture_pic.setFrameShape(QFrame.StyledPanel)

        self.btn_capture_save = QPushButton(self)
        self.btn_capture_save.setGeometry(QRect(Config.width - 110, Config.height - 60, 100, 26))
        self.btn_capture_save.setText('保存截图')
        self.btn_capture_save.setDisabled(True)
        self.btn_capture_save.clicked.connect(self.btn_click)

    def btn_click(self):
        btn = self.sender()
        if btn == self.btn_open_camera:
            self.btn_open_camera.setDisabled(True)
            self.btn_close_camera.setDisabled(False)
            self.btn_capture.setDisabled(False)
            self.cb_recognize.setDisabled(False)
            self.camera = cv2.VideoCapture(0)
            self.frames = collections.deque(maxlen=33)
            self.start_play()
        elif btn == self.btn_close_camera:
            self.stop_play()
            self.btn_open_camera.setDisabled(False)
            self.btn_close_camera.setDisabled(True)
            self.btn_capture.setDisabled(True)
            self.cb_recognize.setDisabled(True)
        elif btn == self.btn_sync_face:
            self.btn_sync_face.setDisabled(True)
            self.sync_data()
        elif btn == self.btn_capture:
            self.capturing = True
            self.btn_capture_save.setDisabled(False)
        elif btn == self.btn_capture_save:
            AddUserFace(self.capture_frame).exec_()
            self.train_model()

    def cb_click(self):
        cb = self.sender()
        if cb == self.cb_recognize:
            if cb.isChecked():
                self.flag_recognize = True
            else:
                self.flag_recognize = False

    def start_play(self):
        self.playing = True
        play_thread = Thread(target=self.play)
        play_thread.start()
        recognize_thread = Thread(target=self.recognize)
        recognize_thread.start()

    def stop_play(self):
        self.playing = False

    def play(self):
        while self.camera.isOpened():
            try:
                if not self.playing:
                    break
                ret, frame = self.camera.read()
                if ret:
                    if self.flag_recognize:
                        self.frames.appendleft(frame.copy())
                        faces = self.recognized_faces.copy()
                        for user_id in faces:
                            face = faces[user_id]
                            x, y, w, h = face[0]
                            cv2.rectangle(frame, (x, y), (x + w, y + h), tuple(list(map(int, face[2].split(',')))), 1, cv2.LINE_AA)
                            if Config.show_name:
                                cv2.putText(frame, face[1], (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                            tuple(list(map(int, face[2].split(',')))), 2)
                            if Config.show_match_result:
                                cv2.putText(frame, 'Match degree:' + str(face[3]), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 2, tuple(list(map(int, face[2].split(',')))), 2)
                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
                    pix_map = QPixmap.fromImage(image)
                    pix_map = pix_map.scaled(Config.width - 130, Config.height - 60, Qt.KeepAspectRatio)
                    self.lbl_viewer.setPixmap(pix_map)
                    # 保存截图
                    if self.capturing:
                        self.capture_frame = frame.copy()
                        pix_map = pix_map.scaled(100, 100, Qt.KeepAspectRatio)
                        self.lbl_capture_pic.setPixmap(pix_map)
                        self.capturing = False
            except Exception as e:
                print(e)
        self.lbl_viewer.clear()
        self.camera.release()

    def recognize(self):
        classifier = HaarcascadeDetective().get_face_classifier()
        while self.playing:
            try:
                if len(self.frames) == 0:
                    time.sleep(0.05)
                    continue
                if self.flag_recognize:
                    frame = self.frames.pop()
                    faces = classifier.get_faces_position(frame)
                    self.recognized_faces.clear()
                    for (x, y, w, h) in faces:
                        face = frame[y:y + h, x:x + w]
                        if self.model is not None:
                            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                            params = self.model.predict(gray)
                            user = self.find_user_by_id(params[0])
                            if user is not None:
                                self.recognized_faces[user[1]] = ((x, y, w, h), user[2], user[3], int(params[1]))
                            else:
                                self.recognized_faces['-1'] = ((x, y, w, h), 'No this user', '255,0,0', 0)
                        else:
                            self.recognized_faces['-2'] = ((x, y, w, h), 'No model', '255,0,0', 0)
            except Exception as e:
                print(e)

    def sync_data(self):
        client = DbHelper.query_client()
        if client is None:
            Tool.show_msg_box('客户端尚未认证！')
            self.btn_sync_face.setDisabled(False)
            return
        shutil.rmtree('faces')
        os.mkdir('faces')
        DbHelper.delete_users()
        users = Tool.user_face_list(client[0])
        if users is not None:
            for user in users:
                user_id = DbHelper.insert_user(user['rowId'], user['name'], user['color'], user['clientId'])
                faces = user['faces']
                for face in faces:
                    Tool.download_face(face['rowId'], str(user_id))
        self.btn_sync_face.setDisabled(False)
        # 重新训练模型
        self.train_model()

    def train_model(self):
        self.users = DbHelper.query_users()
        y, x = [], []
        faces_dir = os.listdir('faces')
        for user_dir in faces_dir:
            if user_dir == 'tmp':
                continue
            faces = os.listdir('faces{}{}'.format(os.sep, user_dir))
            for face in faces:
                y.append(int(user_dir))
                im = cv2.imread('faces{}{}{}{}'.format(os.sep, user_dir, os.sep, face), 0)
                x.append(np.asarray(im, dtype=np.uint8))
        if len(x) != 0 and len(y) != 0:
            self.model = cv2.face.LBPHFaceRecognizer_create()
            self.model.train(np.asarray(x), np.asarray(y, dtype=np.int64))

    def find_user_by_id(self, user_id):
        for user in self.users:
            if user[0] == user_id:
                return user

    def closeEvent(self, *args, **kwargs):
        self.playing = False
        if os.path.exists('faces{}tmp'.format(os.sep)):
            shutil.rmtree('faces{}tmp'.format(os.sep))

    @staticmethod
    def manage_client_login():
        ClientLogin().exec_()

    @staticmethod
    def manage_user():
        AddUser().exec_()

    @staticmethod
    def setting_server():
        ServerSetting().exec_()

    @staticmethod
    def setting_dimension():
        DimensionSetting().exec_()

    @staticmethod
    def help_client_register():
        ClientRegister().exec_()
