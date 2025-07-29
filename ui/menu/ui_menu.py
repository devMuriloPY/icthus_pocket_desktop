# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'menu.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMenu, QMenuBar, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Menu(object):
    def setupUi(self, Menu):
        if not Menu.objectName():
            Menu.setObjectName(u"Menu")
        Menu.resize(752, 472)
        Menu.setStyleSheet(u"")
        Menu.setUnifiedTitleAndToolBarOnMac(True)
        self.actionExit = QAction(Menu)
        self.actionExit.setObjectName(u"actionExit")
        icon = QIcon()
        icon.addFile(u"../../../Users/assets/logout.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionExit.setIcon(icon)
        self.actionSobre = QAction(Menu)
        self.actionSobre.setObjectName(u"actionSobre")
        icon1 = QIcon()
        icon1.addFile(u"../../../Users/assets/info.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionSobre.setIcon(icon1)
        self.actionDatabase = QAction(Menu)
        self.actionDatabase.setObjectName(u"actionDatabase")
        self.actionCadastro_de_Protudos = QAction(Menu)
        self.actionCadastro_de_Protudos.setObjectName(u"actionCadastro_de_Protudos")
        self.actionProdutos_Vinculados = QAction(Menu)
        self.actionProdutos_Vinculados.setObjectName(u"actionProdutos_Vinculados")
        self.centralwidget = QWidget(Menu)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(113, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(441, 280))
        self.label.setMaximumSize(QSize(441, 280))
        self.label.setTextFormat(Qt.TextFormat.AutoText)
        self.label.setPixmap(QPixmap(u"../../../Users/assets/logo.png"))
        self.label.setScaledContents(True)

        self.verticalLayout.addWidget(self.label)

        self.verticalSpacer_2 = QSpacerItem(20, 42, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.lbVersion = QLabel(self.frame)
        self.lbVersion.setObjectName(u"lbVersion")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(9)
        font.setBold(True)
        self.lbVersion.setFont(font)
        self.lbVersion.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.lbVersion)


        self.horizontalLayout.addWidget(self.frame)

        self.horizontalSpacer = QSpacerItem(112, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        Menu.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Menu)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 752, 33))
        self.menubar.setStyleSheet(u"QMenuBar{\n"
"	background-color: #0088ff;\n"
"	color: black;\n"
"}")
        self.menubar.setNativeMenuBar(True)
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        Menu.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionExit)
        self.menuSettings.addAction(self.actionDatabase)

        self.retranslateUi(Menu)

        QMetaObject.connectSlotsByName(Menu)
    # setupUi

    def retranslateUi(self, Menu):
        Menu.setWindowTitle(QCoreApplication.translate("Menu", u"ICThUS Pocket", None))
        self.actionExit.setText(QCoreApplication.translate("Menu", u"Sair", None))
        self.actionSobre.setText(QCoreApplication.translate("Menu", u"Sobre", None))
        self.actionDatabase.setText(QCoreApplication.translate("Menu", u"Banco de dados", None))
        self.actionCadastro_de_Protudos.setText(QCoreApplication.translate("Menu", u"Vincular Produtos", None))
        self.actionProdutos_Vinculados.setText(QCoreApplication.translate("Menu", u"Produtos Vinculados", None))
        self.label.setText("")
        self.lbVersion.setText(QCoreApplication.translate("Menu", u"Vers\u00e3o: 2025.07.23", None))
        self.menuHelp.setTitle(QCoreApplication.translate("Menu", u"Ajuda", None))
        self.menuSettings.setTitle(QCoreApplication.translate("Menu", u"Configura\u00e7\u00f5es", None))
    # retranslateUi

