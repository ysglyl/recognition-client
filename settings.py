from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton

from config.config import Config


class ServerSetting(QDialog):
    def __init__(self):
        super(ServerSetting, self).__init__()
        self.setFixedSize(300, 275)
        self.setWindowIcon(QIcon('icons/server.png'))
        self.setWindowTitle('服务器配置')

        lbl_host = QLabel('域名/IP', self)
        lbl_host.setGeometry(10, 80, 50, 26)
        lbl_host.setAlignment(Qt.AlignCenter)
        self.le_host = QLineEdit(self)
        self.le_host.setText(Config.host)
        self.le_host.setGeometry(70, 80, 200, 26)
        lbl_port = QLabel('端口', self)
        lbl_port.setGeometry(10, 116, 50, 26)
        lbl_port.setAlignment(Qt.AlignCenter)
        self.le_port = QLineEdit(self)
        self.le_port.setText(Config.port)
        self.le_port.setGeometry(70, 116, 200, 26)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('保存')
        self.btn_save.setGeometry(10, 234, 280, 30)
        self.btn_save.clicked.connect(self.save)

    def save(self):
        host = self.le_host.text().strip(' ')
        if host == '':
            self.btn_save.setText('请输入主机名')
            self.le_host.setFocus()
            return
        port = self.le_port.text().strip(' ')
        if port == '' or not port.isdigit():
            self.btn_save.setText('请输入数字端口')
            self.le_port.setFocus()
            return
        if Config.save_server({'host': host, 'port': port}):
            self.close()


class DimensionSetting(QDialog):
    def __init__(self):
        super(DimensionSetting, self).__init__()
        self.setFixedSize(300, 275)
        self.setWindowIcon(QIcon('icons/server.png'))
        self.setWindowTitle('窗口设置')

        lbl_width = QLabel('宽度', self)
        lbl_width.setGeometry(10, 80, 50, 26)
        lbl_width.setAlignment(Qt.AlignCenter)
        self.le_width = QLineEdit(self)
        self.le_width.setText(str(Config.width))
        self.le_width.setGeometry(70, 80, 200, 26)
        lbl_height = QLabel('高度', self)
        lbl_height.setGeometry(10, 116, 50, 26)
        lbl_height.setAlignment(Qt.AlignCenter)
        self.le_height = QLineEdit(self)
        self.le_height.setText(str(Config.height))
        self.le_height.setGeometry(70, 116, 200, 26)

        self.btn_save = QPushButton(self)
        self.btn_save.setText('保存')
        self.btn_save.setGeometry(10, 234, 280, 30)
        self.btn_save.clicked.connect(self.save)

    def save(self):
        width = self.le_width.text().strip(' ')
        if width == '' or not width.isdigit():
            self.btn_save.setText('请输入宽度')
            self.le_width.setFocus()
            return
        height = self.le_height.text().strip(' ')
        if height == '' or not height.isdigit():
            self.btn_save.setText('请输入高度')
            self.le_height.setFocus()
            return
        if Config.save_dimension({'width': width, 'height': height}):
            self.close()
