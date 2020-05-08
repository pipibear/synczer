# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\python\synczer\main.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(912, 582)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_splitter = QtWidgets.QSplitter(self.centralWidget)
        self.frame_splitter.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_splitter.setOrientation(QtCore.Qt.Vertical)
        self.frame_splitter.setObjectName("frame_splitter")
        self.groupBox = QtWidgets.QGroupBox(self.frame_splitter)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_3.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 50))
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_start_export = QtWidgets.QPushButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btn_start_export.setFont(font)
        self.btn_start_export.setObjectName("btn_start_export")
        self.horizontalLayout_2.addWidget(self.btn_start_export)
        self.btn_resume_export = QtWidgets.QPushButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btn_resume_export.setFont(font)
        self.btn_resume_export.setObjectName("btn_resume_export")
        self.horizontalLayout_2.addWidget(self.btn_resume_export)
        self.btn_stop_export = QtWidgets.QPushButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btn_stop_export.setFont(font)
        self.btn_stop_export.setObjectName("btn_stop_export")
        self.horizontalLayout_2.addWidget(self.btn_stop_export)
        self.chk_loop_export = QtWidgets.QCheckBox(self.groupBox_3)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        self.chk_loop_export.setFont(font)
        self.chk_loop_export.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.chk_loop_export.setObjectName("chk_loop_export")
        self.horizontalLayout_2.addWidget(self.chk_loop_export)
        self.lbl_timer_export = QtWidgets.QLabel(self.groupBox_3)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        self.lbl_timer_export.setFont(font)
        self.lbl_timer_export.setObjectName("lbl_timer_export")
        self.horizontalLayout_2.addWidget(self.lbl_timer_export)
        self.pb_export = QtWidgets.QProgressBar(self.groupBox_3)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pb_export.setFont(font)
        self.pb_export.setProperty("value", 24)
        self.pb_export.setObjectName("pb_export")
        self.horizontalLayout_2.addWidget(self.pb_export)
        self.gridLayout_2.addWidget(self.groupBox_3, 2, 0, 1, 2)
        self.lbl_export = QtWidgets.QLabel(self.groupBox)
        self.lbl_export.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        self.lbl_export.setFont(font)
        self.lbl_export.setObjectName("lbl_export")
        self.gridLayout_2.addWidget(self.lbl_export, 1, 0, 1, 1)
        self.top_splitter = QtWidgets.QSplitter(self.groupBox)
        self.top_splitter.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.top_splitter.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.top_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.top_splitter.setObjectName("top_splitter")
        self.txt_error_export = QtWidgets.QPlainTextEdit(self.top_splitter)
        self.txt_error_export.setMinimumSize(QtCore.QSize(0, 0))
        self.txt_error_export.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.txt_error_export.setBaseSize(QtCore.QSize(0, 0))
        self.txt_error_export.setObjectName("txt_error_export")
        self.txt_export = QtWidgets.QPlainTextEdit(self.top_splitter)
        self.txt_export.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.txt_export.setObjectName("txt_export")
        self.gridLayout_2.addWidget(self.top_splitter, 0, 0, 1, 2)
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame_splitter)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.bottom_splitter = QtWidgets.QSplitter(self.groupBox_2)
        self.bottom_splitter.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.bottom_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.bottom_splitter.setObjectName("bottom_splitter")
        self.txt_error_import = QtWidgets.QPlainTextEdit(self.bottom_splitter)
        self.txt_error_import.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.txt_error_import.setBaseSize(QtCore.QSize(0, 0))
        self.txt_error_import.setObjectName("txt_error_import")
        self.txt_import = QtWidgets.QPlainTextEdit(self.bottom_splitter)
        self.txt_import.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.txt_import.setObjectName("txt_import")
        self.gridLayout.addWidget(self.bottom_splitter, 0, 0, 1, 1)
        self.lbl_import = QtWidgets.QLabel(self.groupBox_2)
        self.lbl_import.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        self.lbl_import.setFont(font)
        self.lbl_import.setObjectName("lbl_import")
        self.gridLayout.addWidget(self.lbl_import, 1, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox_2)
        self.groupBox_4.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_4.setMaximumSize(QtCore.QSize(16777215, 50))
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btn_start_import = QtWidgets.QPushButton(self.groupBox_4)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btn_start_import.setFont(font)
        self.btn_start_import.setObjectName("btn_start_import")
        self.horizontalLayout_3.addWidget(self.btn_start_import)
        self.btn_resume_import = QtWidgets.QPushButton(self.groupBox_4)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btn_resume_import.setFont(font)
        self.btn_resume_import.setObjectName("btn_resume_import")
        self.horizontalLayout_3.addWidget(self.btn_resume_import)
        self.btn_stop_import = QtWidgets.QPushButton(self.groupBox_4)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.btn_stop_import.setFont(font)
        self.btn_stop_import.setObjectName("btn_stop_import")
        self.horizontalLayout_3.addWidget(self.btn_stop_import)
        self.chk_loop_import = QtWidgets.QCheckBox(self.groupBox_4)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        self.chk_loop_import.setFont(font)
        self.chk_loop_import.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.chk_loop_import.setObjectName("chk_loop_import")
        self.horizontalLayout_3.addWidget(self.chk_loop_import)
        self.lbl_timer_import = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        self.lbl_timer_import.setFont(font)
        self.lbl_timer_import.setObjectName("lbl_timer_import")
        self.horizontalLayout_3.addWidget(self.lbl_timer_import)
        self.pb_import = QtWidgets.QProgressBar(self.groupBox_4)
        font = QtGui.QFont()
        font.setFamily("宋体")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pb_import.setFont(font)
        self.pb_import.setProperty("value", 24)
        self.pb_import.setObjectName("pb_import")
        self.horizontalLayout_3.addWidget(self.pb_import)
        self.gridLayout.addWidget(self.groupBox_4, 2, 0, 1, 1)
        self.verticalLayout.addWidget(self.frame_splitter)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "Export session"))
        self.btn_start_export.setText(_translate("MainWindow", "Launch"))
        self.btn_resume_export.setText(_translate("MainWindow", "Resume"))
        self.btn_stop_export.setText(_translate("MainWindow", "Stop"))
        self.chk_loop_export.setText(_translate("MainWindow", "Loop"))
        self.lbl_timer_export.setText(_translate("MainWindow", "00:00:00"))
        self.lbl_export.setText(_translate("MainWindow", "Total 0 Failure 0"))
        self.txt_error_export.setPlaceholderText(_translate("MainWindow", "Error output window"))
        self.txt_export.setPlaceholderText(_translate("MainWindow", "Log output window"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Import session"))
        self.txt_error_import.setPlaceholderText(_translate("MainWindow", "Error output window"))
        self.txt_import.setPlaceholderText(_translate("MainWindow", "Log output window"))
        self.lbl_import.setText(_translate("MainWindow", "Total 0 Failure 0"))
        self.btn_start_import.setText(_translate("MainWindow", "Launch"))
        self.btn_resume_import.setText(_translate("MainWindow", "Resume"))
        self.btn_stop_import.setText(_translate("MainWindow", "Stop"))
        self.chk_loop_import.setText(_translate("MainWindow", "Loop"))
        self.lbl_timer_import.setText(_translate("MainWindow", "00:00:00"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

