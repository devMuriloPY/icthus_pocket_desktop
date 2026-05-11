# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'servidor.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Server(object):
    def setupUi(self, Server):
        if not Server.objectName():
            Server.setObjectName(u"Server")
        Server.setWindowModality(Qt.WindowModality.ApplicationModal)
        Server.resize(300, 685)
        Server.setMinimumSize(QSize(300, 685))
        Server.setMaximumSize(QSize(300, 685))
        icon = QIcon()
        icon.addFile(u"../../../assets/database.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        Server.setWindowIcon(icon)
        Server.setStyleSheet(u"QGroupBox{\n"
"	border: 1px solid #d9d9d9;\n"
"	padding-top: 20px;\n"
"}")
        Server.setInputMethodHints(Qt.InputMethodHint.ImhHiddenText)
        self.verticalLayout_3 = QVBoxLayout(Server)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gbServer = QGroupBox(Server)
        self.gbServer.setObjectName(u"gbServer")
        self.gbServer.setMinimumSize(QSize(250, 0))
        self.gbServer.setMaximumSize(QSize(300, 16777215))
        self.gbServer.setInputMethodHints(Qt.InputMethodHint.ImhPreferUppercase)
        self.verticalLayout_2 = QVBoxLayout(self.gbServer)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lbServer = QLabel(self.gbServer)
        self.lbServer.setObjectName(u"lbServer")

        self.verticalLayout_2.addWidget(self.lbServer)

        self.leServer = QLineEdit(self.gbServer)
        self.leServer.setObjectName(u"leServer")
        self.leServer.setMinimumSize(QSize(0, 34))
        self.leServer.setMaximumSize(QSize(16777215, 34))
        self.leServer.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.leServer)

        self.lbUser = QLabel(self.gbServer)
        self.lbUser.setObjectName(u"lbUser")

        self.verticalLayout_2.addWidget(self.lbUser)

        self.leUser = QLineEdit(self.gbServer)
        self.leUser.setObjectName(u"leUser")
        self.leUser.setMinimumSize(QSize(0, 34))
        self.leUser.setMaximumSize(QSize(16777215, 34))
        self.leUser.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.leUser)

        self.lbPassword = QLabel(self.gbServer)
        self.lbPassword.setObjectName(u"lbPassword")
        self.lbPassword.setMinimumSize(QSize(2, 0))

        self.verticalLayout_2.addWidget(self.lbPassword)

        self.lePassword = QLineEdit(self.gbServer)
        self.lePassword.setObjectName(u"lePassword")
        self.lePassword.setMinimumSize(QSize(0, 34))
        self.lePassword.setMaximumSize(QSize(16777215, 34))
        self.lePassword.setEchoMode(QLineEdit.EchoMode.Password)
        self.lePassword.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.lePassword)

        self.lbDatabase = QLabel(self.gbServer)
        self.lbDatabase.setObjectName(u"lbDatabase")

        self.verticalLayout_2.addWidget(self.lbDatabase)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.cbDatabase = QComboBox(self.gbServer)
        self.cbDatabase.setObjectName(u"cbDatabase")
        self.cbDatabase.setMinimumSize(QSize(0, 34))
        self.cbDatabase.setMaximumSize(QSize(500, 34))

        self.horizontalLayout_2.addWidget(self.cbDatabase)

        self.btnLoadDatabases = QPushButton(self.gbServer)
        self.btnLoadDatabases.setObjectName(u"btnLoadDatabases")
        self.btnLoadDatabases.setMinimumSize(QSize(34, 34))
        self.btnLoadDatabases.setMaximumSize(QSize(34, 34))
        self.btnLoadDatabases.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon1 = QIcon()
        icon1.addFile(u"../../../assets/refresh.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon1.addFile(u"../../../assets/refresh.png", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.btnLoadDatabases.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.btnLoadDatabases)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.label = QLabel(self.gbServer)
        self.label.setObjectName(u"label")
        self.label.setInputMethodHints(Qt.InputMethodHint.ImhFormattedNumbersOnly)

        self.verticalLayout_2.addWidget(self.label)

        self.lineEdit = QLineEdit(self.gbServer)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 34))
        self.lineEdit.setMaximumSize(QSize(120, 34))
        self.lineEdit.setInputMethodHints(Qt.InputMethodHint.ImhDigitsOnly)
        self.lineEdit.setDragEnabled(False)
        self.lineEdit.setCursorMoveStyle(Qt.CursorMoveStyle.LogicalMoveStyle)
        self.lineEdit.setClearButtonEnabled(True)

        self.verticalLayout_2.addWidget(self.lineEdit)

        self.label_2 = QLabel(self.gbServer)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.lineEdit_2 = QLineEdit(self.gbServer)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setMinimumSize(QSize(0, 30))
        self.lineEdit_2.setMaximumSize(QSize(16777215, 30))
        self.lineEdit_2.setInputMethodHints(Qt.InputMethodHint.ImhNone)
        self.lineEdit_2.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.lineEdit_2)

        self.lbImpressora = QLabel(self.gbServer)
        self.lbImpressora.setObjectName(u"lbImpressora")

        self.verticalLayout_2.addWidget(self.lbImpressora)

        self.cbImpressora = QComboBox(self.gbServer)
        self.cbImpressora.setObjectName(u"cbImpressora")
        self.cbImpressora.setMinimumSize(QSize(0, 30))
        self.cbImpressora.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout_2.addWidget(self.cbImpressora)

        self.chkLinhaSeparadaMesmoItem = QCheckBox(self.gbServer)
        self.chkLinhaSeparadaMesmoItem.setObjectName(u"chkLinhaSeparadaMesmoItem")

        self.verticalLayout_2.addWidget(self.chkLinhaSeparadaMesmoItem)

        self.lbColunas = QLabel(self.gbServer)
        self.lbColunas.setObjectName(u"lbColunas")

        self.verticalLayout_2.addWidget(self.lbColunas)

        self.leColunas = QLineEdit(self.gbServer)
        self.leColunas.setObjectName(u"leColunas")
        self.leColunas.setMinimumSize(QSize(0, 30))
        self.leColunas.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout_2.addWidget(self.leColunas)

        self.lbUsuarioWindows = QLabel(self.gbServer)
        self.lbUsuarioWindows.setObjectName(u"lbUsuarioWindows")

        self.verticalLayout_2.addWidget(self.lbUsuarioWindows)

        self.cbUsuarioWindows = QComboBox(self.gbServer)
        self.cbUsuarioWindows.setObjectName(u"cbUsuarioWindows")
        self.cbUsuarioWindows.setMinimumSize(QSize(0, 30))
        self.cbUsuarioWindows.setMaximumSize(QSize(16777215, 30))

        self.verticalLayout_2.addWidget(self.cbUsuarioWindows)


        self.verticalLayout_3.addWidget(self.gbServer)

        self.frActions = QFrame(Server)
        self.frActions.setObjectName(u"frActions")
        self.frActions.setMaximumSize(QSize(363, 56))
        self.frActions.setStyleSheet(u"QFrame{\n"
"	border: 1px solid #d9d9d9;\n"
"}")
        self.frActions.setFrameShape(QFrame.Shape.StyledPanel)
        self.frActions.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout = QHBoxLayout(self.frActions)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(82, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btnCancel = QPushButton(self.frActions)
        self.btnCancel.setObjectName(u"btnCancel")
        self.btnCancel.setMinimumSize(QSize(100, 34))
        self.btnCancel.setMaximumSize(QSize(100, 34))
        self.btnCancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon2 = QIcon()
        icon2.addFile(u"../../../assets/back.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnCancel.setIcon(icon2)

        self.horizontalLayout.addWidget(self.btnCancel)

        self.btnSave = QPushButton(self.frActions)
        self.btnSave.setObjectName(u"btnSave")
        self.btnSave.setMinimumSize(QSize(100, 32))
        self.btnSave.setMaximumSize(QSize(100, 32))
        self.btnSave.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnSave.setAutoFillBackground(False)
        self.btnSave.setStyleSheet(u"")
        icon3 = QIcon()
        icon3.addFile(u"../../../assets/check.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnSave.setIcon(icon3)

        self.horizontalLayout.addWidget(self.btnSave)


        self.verticalLayout_3.addWidget(self.frActions)

        QWidget.setTabOrder(self.leServer, self.leUser)
        QWidget.setTabOrder(self.leUser, self.lePassword)
        QWidget.setTabOrder(self.lePassword, self.cbDatabase)
        QWidget.setTabOrder(self.cbDatabase, self.btnLoadDatabases)
        QWidget.setTabOrder(self.btnLoadDatabases, self.cbUsuarioWindows)
        QWidget.setTabOrder(self.cbUsuarioWindows, self.btnCancel)
        QWidget.setTabOrder(self.btnCancel, self.btnSave)

        self.retranslateUi(Server)

        QMetaObject.connectSlotsByName(Server)
    # setupUi

    def retranslateUi(self, Server):
        Server.setWindowTitle(QCoreApplication.translate("Server", u"Configura\u00e7\u00e3o da Conex\u00e3o", None))
        self.gbServer.setTitle(QCoreApplication.translate("Server", u"Conex\u00e3o", None))
        self.lbServer.setText(QCoreApplication.translate("Server", u"Servidor", None))
        self.lbUser.setText(QCoreApplication.translate("Server", u"Usu\u00e1rio", None))
        self.lbPassword.setText(QCoreApplication.translate("Server", u"Senha", None))
        self.lbDatabase.setText(QCoreApplication.translate("Server", u"Banco de dados", None))
#if QT_CONFIG(tooltip)
        self.btnLoadDatabases.setToolTip(QCoreApplication.translate("Server", u"Atualizar Banco de Dados", None))
#endif // QT_CONFIG(tooltip)
        self.btnLoadDatabases.setText("")
        self.label.setText(QCoreApplication.translate("Server", u"Porta Servidor (Padr\u00e3o 5757)", None))
        self.label_2.setText(QCoreApplication.translate("Server", u"IP Servidor", None))
        self.lbImpressora.setText(QCoreApplication.translate("Server", u"Impressora", None))
        self.chkLinhaSeparadaMesmoItem.setText(QCoreApplication.translate("Server", u"Linha separada para mesmo item", None))
        self.lbColunas.setText(QCoreApplication.translate("Server", u"Colunas", None))
        self.lbUsuarioWindows.setText(QCoreApplication.translate("Server", u"Usu\u00e1rio Windows para Inicializa\u00e7\u00e3o Autom\u00e1tica", None))
#if QT_CONFIG(tooltip)
        self.btnCancel.setToolTip(QCoreApplication.translate("Server", u"Fechar", None))
#endif // QT_CONFIG(tooltip)
        self.btnCancel.setText(QCoreApplication.translate("Server", u"Cancelar", None))
#if QT_CONFIG(tooltip)
        self.btnSave.setToolTip(QCoreApplication.translate("Server", u"Salvar", None))
#endif // QT_CONFIG(tooltip)
        self.btnSave.setText(QCoreApplication.translate("Server", u"Salvar", None))
    # retranslateUi

