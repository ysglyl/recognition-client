from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton

from db.db_helper import DbHelper
from tool import Tool


class ClientLogin(QDialog):
    def __init__(self):
        super(ClientLogin, self).__init__()
        self.setFixedSize(300, 180)
        self.setWindowIcon(QIcon('icons/auth.png'))
        self.setWindowTitle('服务连接')

        client = DbHelper.query_client()

        lbl_app_id = QLabel('APP ID', self)
        lbl_app_id.setGeometry(10, 20, 50, 26)
        lbl_app_id.setAlignment(Qt.AlignCenter)
        self.le_app_id = QLineEdit(self)
        self.le_app_id.setText(client[1] if client is not None else '')
        self.le_app_id.setGeometry(70, 20, 200, 26)
        self.le_app_id.setDisabled(True if client is not None else False)
        lbl_security = QLabel('密钥', self)
        lbl_security.setGeometry(10, 66, 50, 26)
        lbl_security.setAlignment(Qt.AlignCenter)
        self.le_security = QLineEdit(self)
        self.le_security.setEchoMode(QLineEdit.Password)
        self.le_security.setText(client[2] if client is not None else '')
        self.le_security.setGeometry(70, 66, 200, 26)
        self.le_security.setDisabled(True if client is not None else False)

        self.btn_login = QPushButton(self)
        self.btn_login.setText('已连接' if client is not None else '连接')
        self.btn_login.setDisabled(True if client is not None else False)
        self.btn_login.setGeometry(10, 110, 280, 30)
        self.btn_login.clicked.connect(self.login)

        self.btn_logout = QPushButton(self)
        self.btn_logout.setText('注销' if client is not None else '未连接')
        self.btn_logout.setDisabled(True if client is None else False)
        self.btn_logout.setGeometry(10, 140, 280, 30)
        self.btn_logout.clicked.connect(self.logout)

    def login(self):
        app_id = self.le_app_id.text().strip(' ')
        if app_id == '':
            self.btn_login.setText('请输入APP ID')
            self.le_app_id.setFocus()
            return
        security = self.le_security.text().strip(' ')
        if security == '':
            self.btn_login.setText('请输入密钥')
            self.le_security.setFocus()
            return
        self.btn_login.setDisabled(True)
        result, data = Tool.client_login(app_id, Tool.get_md5(security))
        if result:
            DbHelper.insert_client(data, app_id, security)
            self.btn_login.setText("已连接")
            self.le_app_id.setDisabled(True)
            self.le_security.setDisabled(True)
            self.btn_logout.setDisabled(False)
            self.btn_logout.setText("注销")
            self.btn_logout.setFocus()
        else:
            self.btn_login.setDisabled(False)
            self.btn_login.setText("APP ID或者密钥不正确")

    def logout(self):
        self.btn_logout.setDisabled(True)
        self.btn_logout.setText("未连接")
        self.btn_login.setDisabled(False)
        self.btn_login.setText("连接")
        self.le_app_id.setDisabled(False)
        self.le_security.setDisabled(False)
        DbHelper.delete_client()

