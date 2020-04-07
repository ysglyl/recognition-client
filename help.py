from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton

from db.db_helper import DbHelper
from tool import Tool


class ClientRegister(QDialog):
    def __init__(self):
        super(ClientRegister, self).__init__()
        self.setFixedSize(300, 150)
        self.setWindowIcon(QIcon('icons/auth.png'))
        self.setWindowTitle('客户端注册')

        client = DbHelper.query_client()

        lbl_app_id = QLabel('APP ID', self)
        lbl_app_id.setGeometry(10, 20, 50, 26)
        lbl_app_id.setAlignment(Qt.AlignCenter)
        self.le_app_id = QLineEdit(self)
        self.le_app_id.setText(client[0] if client is not None else '')
        self.le_app_id.setGeometry(70, 20, 200, 26)
        self.le_app_id.setDisabled(True if client is not None else False)
        lbl_security = QLabel('密钥', self)
        lbl_security.setGeometry(10, 66, 50, 26)
        lbl_security.setAlignment(Qt.AlignCenter)
        self.le_security = QLineEdit(self)
        self.le_security.setEchoMode(QLineEdit.Password)
        self.le_security.setText(client[1] if client is not None else '')
        self.le_security.setGeometry(70, 66, 200, 26)
        self.le_security.setDisabled(True if client is not None else False)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('已注册' if client is not None else '注册')
        self.btn_save.setDisabled(True if client is not None else False)
        self.btn_save.setGeometry(10, 110, 280, 30)
        self.btn_save.clicked.connect(self.register)

    def register(self):
        app_id = self.le_app_id.text().strip(' ')
        if app_id == '':
            self.btn_save.setText('请输入APP ID')
            self.le_app_id.setFocus()
            return
        security = self.le_security.text().strip(' ')
        if security == '':
            self.btn_save.setText('请输入密钥')
            self.le_security.setFocus()
            return
        self.btn_save.setDisabled(True)
        result, data = Tool.client_register(app_id, Tool.get_md5(security))
        if result:
            DbHelper.insert_client(data, app_id, security)
            self.le_app_id.setDisabled(True)
            self.le_security.setDisabled(True)
            self.btn_save.setText("注册成功")
        elif data is not None:
            self.btn_save.setDisabled(False)
            self.btn_save.setText(data)
        else:
            self.btn_save.setDisabled(False)
            self.btn_save.setText("注册失败")
