from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon, QImage, QPixmap
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QComboBox
import os
import time

from db.db_helper import DbHelper
from tool import Tool
from haarcascade_detective import HaarcascadeDetective

import cv2


class AddUser(QDialog):

    def __init__(self):
        super(AddUser, self).__init__()
        self.setFixedSize(300, 190)
        self.setWindowIcon(QIcon('icons/auth.png'))
        self.setWindowTitle('添加用户')

        self.client = DbHelper.query_client()

        lbl_name = QLabel('姓名', self)
        lbl_name.setGeometry(10, 20, 50, 26)
        lbl_name.setAlignment(Qt.AlignCenter)
        self.le_name = QLineEdit(self)
        self.le_name.setGeometry(70, 20, 200, 26)
        self.le_name.setDisabled(True if self.client is None else False)
        lbl_color = QLabel('颜色值', self)
        lbl_color.setGeometry(10, 100, 50, 26)
        lbl_color.setAlignment(Qt.AlignCenter)
        self.le_color = QLineEdit(self)
        self.le_color.setGeometry(70, 100, 200, 26)
        self.le_color.setDisabled(True if self.client is None else False)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('添加' if self.client is not None else '客户端未连接')
        self.btn_save.setGeometry(10, 140, 280, 30)
        self.btn_save.clicked.connect(self.save)
        self.btn_save.setDisabled(True if self.client is None else False)

    def save(self):
        name = self.le_name.text().strip(' ')
        if name == '':
            self.btn_save.setText('请输入姓名')
            self.le_name.setFocus()
            return
        if not name.replace(' ', '').encode("utf-8").isalpha():
            self.btn_save.setText('只支持英文字母和空格～')
            self.le_name.setFocus()
            return
        color = self.le_color.text().strip(' ')
        if color == '':
            self.btn_save.setText('请输入颜色值')
            self.le_color.setFocus()
            return
        colors = color.split(',')
        if len(colors) != 3:
            self.btn_save.setText('颜色值不正确')
            self.le_color.setFocus()
            return
        for c in colors:
            if not c.isdigit() or int(c) > 255 or int(c) < 0:
                self.btn_save.setText('颜色值不正确')
                self.le_color.setFocus()
                return
        self.btn_save.setDisabled(True)

        result, data = Tool.user_add(self.client[0], name, color)
        if result:
            DbHelper.insert_user(data, name, color, self.client[0])
            self.close()
        elif data is not None:
            self.btn_save.setDisabled(False)
            self.btn_save.setText(data)
        else:
            self.btn_save.setDisabled(False)
            self.btn_save.setText("添加失败")


class AddUserFace(QDialog):
    def __init__(self, image):
        super(AddUserFace, self).__init__()
        self.setFixedSize(300, 275)
        self.setWindowIcon(QIcon('icons/add.png'))
        self.setWindowTitle('添加')
        lbl_face = QLabel('人脸', self)
        lbl_face.setGeometry(10, 22, 50, 26)
        lbl_face.setAlignment(Qt.AlignCenter)

        lbl_name = QLabel('名称', self)
        lbl_name.setGeometry(10, 80, 50, 26)
        lbl_name.setAlignment(Qt.AlignCenter)
        self.cb_user = QComboBox(self)
        users = DbHelper.query_users()
        for user in users:
            self.cb_user.addItem(user[2], userData=user)
        self.cb_user.setGeometry(70, 80, 200, 26)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('保存')
        self.btn_save.setGeometry(10, 234, 280, 30)
        self.btn_save.clicked.connect(self.save)

        self.cache_faces = {}
        self.face = None

        faces = HaarcascadeDetective().get_face_classifier().get_faces(image)
        index = 0
        for face in faces:
            viewer_face = QPushButton(self)
            viewer_face.setGeometry(70 * (index + 1), 10, 60, 60)
            viewer_face.setIconSize(QSize(56, 56))
            img = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            image = QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
            pix_map = QPixmap.fromImage(image)
            viewer_face.setIcon(QIcon(pix_map))
            viewer_face.clicked.connect(self.select_face)
            self.cache_faces[viewer_face] = face
            if index == 0:
                self.face = face
                viewer_face.setStyleSheet('border-color: rgb(255, 0, 0);border-style: outset;border-width: 2px;')
            index += 1
            if index > 2:
                break

        if index == 0:
            lbl_message = QLabel(self)
            lbl_message.setText('未检测到人脸信息')
            lbl_message.setGeometry(70, 22, 200, 26)
            self.btn_save.setDisabled(True)

    def select_face(self):
        sender = self.sender()
        for btn in self.cache_faces:
            btn.setStyleSheet('border-style: none')
        sender.setStyleSheet("border-color: rgb(255, 0, 0);border-style: outset;border-width: 2px;")
        self.face = self.cache_faces[btn]

    def save(self):
        if self.face is None:
            return
        self.btn_save.setDisabled(True)
        if not os.path.exists('faces/tmp'):
            os.mkdir('faces/tmp')
        tmp_name = 'faces/tmp/{}.png'.format(time.time())
        cv2.imwrite(tmp_name, self.face)
        user = self.cb_user.currentData()
        result, data = Tool.user_face_add(user[1], tmp_name)
        if result:
            if not os.path.exists('faces/{}'.format(user[0])):
                os.mkdir('faces/{}'.format(user[0]))
            user_face_path = 'faces/{}/{}.png'.format(user[0], data)
            cv2.imwrite(user_face_path, self.face)
            self.close()
        else:
            self.btn_save.setText(data if data is not None else '保存失败，请稍后再试')
            self.btn_save.setDisabled(False)
