from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton

from db.db_helper import DbHelper


class ClientAuth(QDialog):
    def __init__(self):
        super(ClientAuth, self).__init__()
        self.setFixedSize(300, 275)
        self.setWindowIcon(QIcon('icons/auth.png'))
        self.setWindowTitle('客户端认证')

        client = DbHelper.query_client()

        lbl_app_id = QLabel('APP ID', self)
        lbl_app_id.setGeometry(10, 80, 50, 26)
        lbl_app_id.setAlignment(Qt.AlignCenter)
        self.le_app_id = QLineEdit(self)
        self.le_app_id.setText(client[0] if client is not None else '')
        self.le_app_id.setGeometry(70, 80, 200, 26)
        self.le_app_id.setDisabled(True if client is not None else False)
        lbl_security = QLabel('密钥', self)
        lbl_security.setGeometry(10, 116, 50, 26)
        lbl_security.setAlignment(Qt.AlignCenter)
        self.le_security = QLineEdit(self)
        self.le_security.setText(client[1] if client is not None else '')
        self.le_security.setGeometry(70, 116, 200, 26)
        self.le_security.setDisabled(True if client is not None else False)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('已认证' if client is not None else '认证')
        self.btn_save.setDisabled(True if client is not None else False)
        self.btn_save.setGeometry(10, 234, 280, 30)
        self.btn_save.clicked.connect(self.save)

    def save(self):
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
        DbHelper.insert_client(app_id, security)
        self.close()
