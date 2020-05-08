# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal, QThread, QTimer, QEvent, QTime
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QMessageBox
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon, QLabel
from PyQt5.QtGui import QIcon, QCursor
import os, sys, threading, time, traceback, platform

from Ui_main import Ui_MainWindow
from Ui_setting import Ui_DlgSetting
from lib.Exporter import Exporter
from lib.Importer import Importer
from lib.Icon import MyIcon

class MyExporter(Exporter, QThread):
    signal = pyqtSignal(object)
    def __init__(self, parent=None):
        Exporter.__init__(self,False)
        QThread.__init__(self)

    def log(self, str, extra=None):
        self.signal.emit({"str":str, "extra":extra})

class MyImporter(Importer, QThread):
    signal = pyqtSignal(object)
    def __init__(self, parent=None):
        Importer.__init__(self,False)
        QThread.__init__(self)

    def log(self, str, extra=None):
        self.signal.emit({"str":str, "extra":extra})

class DlgSetting(QDialog, Ui_DlgSetting):
    parent = None

    def __init__(self, parent=None):
        super(DlgSetting, self).__init__(parent)
        self.setupUi(self)
        self.parent = parent

        self.chk_min_tray.setChecked(parent.settings['chkMinToTray'])
    
    @pyqtSlot() 
    def on_btn_ok_clicked(self):
        self.parent.settings = {
            "chkMinToTray":self.chk_min_tray.isChecked(),
        }
        #print(self.parent.settings)
        self.close()

    @pyqtSlot() 
    def on_btn_cancel_clicked(self):
        self.close()



class MainWindow(QMainWindow, Ui_MainWindow):
    logoIconPath = os.path.dirname(os.path.realpath(sys.argv[0])) + '/logo.png'
    tmpPath = os.path.dirname(os.path.realpath(sys.argv[0])) + '/tmp'

    exporter = None
    exporterThreads = []
    exporterTimer = None
    exporterTime = 0
    exporterTotalNum = 0
    exporterFailureNum = 0

    importer = None
    importerThreads = []
    importerTimer = None
    importerTime = 0
    importerTotalNum = 0
    importerFailureNum = 0

    tray = None
    dlgSetting = None
    settings = {
        "chkMinToTray":True,
    }

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        
        self.exporter = MyExporter()
        self.exporter.signal.connect(self.logExporter)
        self.exporter.init()

        self.importer = MyImporter()
        self.importer.signal.connect(self.logImporter)
        self.importer.init()
        
    def changeEvent(self, e):
        if e.type() == QEvent.WindowStateChange:
            if self.isMinimized() and isWindows():
                if self.settings["chkMinToTray"]:
                    self.hide()
            elif self.isMaximized():
                pass
            elif self.isFullScreen():
                pass
            elif self.isActiveWindow():
                pass
        elif e.type()==QEvent.ActivationChange:
            #self.repaint()
            pass

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to exit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
        if reply == QMessageBox.Yes: 
            self.exitSystem()
            sys.exit()
        else: 
            event.ignore()

    def addSystemTray(self):
        self.tray = QSystemTrayIcon() 

        #self.icon = QIcon(self.logoIconPath)
        self.icon = MyIcon.getLogoIcon()
        self.tray.setIcon(self.icon) 
            

        self.tray.activated.connect(self.clickTray) 
        self.tray.messageClicked.connect(self.clickTray)
        self.tray_menu = QMenu(QApplication.desktop()) 
        self.RestoreAction = QAction('Show', self, triggered=self.restoreAction)
        self.SettingsAction = QAction('Settings', self, triggered=self.settingsAction) 
        self.QuitAction = QAction('Exit', self, triggered=self.exitAction) 
        self.tray_menu.addAction(self.RestoreAction) 
        self.tray_menu.addAction(self.SettingsAction)
        self.tray_menu.addAction(self.QuitAction)
        self.tray.setContextMenu(self.tray_menu) 
        self.tray.show()

    def settingsAction(self):
        self.dlgSetting = DlgSetting(self)
        self.dlgSetting.show()

    def exitAction(self):
        reply = QMessageBox.question(self, 'Message', "Are you sure to exit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
        if reply == QMessageBox.Yes: 
            self.exitSystem()
            sys.exit()

    def clickTray(self, reason):
        if reason != QSystemTrayIcon.DoubleClick:
            return

        self.restoreAction()

    def restoreAction(self):
        if self.isMaximized():
            self.showMaximized()
        elif self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()
            
        self.activateWindow()

        #scrollbar
        self.txt_error_export.verticalScrollBar().setValue(self.txt_error_export.verticalScrollBar().maximum())
        self.txt_export.verticalScrollBar().setValue(self.txt_export.verticalScrollBar().maximum())
        self.txt_error_import.verticalScrollBar().setValue(self.txt_error_import.verticalScrollBar().maximum())
        self.txt_import.verticalScrollBar().setValue(self.txt_import.verticalScrollBar().maximum())

    def addContextMenu(self):
        #export log
        self.exporterContextMenu = QMenu(self)
        self.txt_export.setContextMenuPolicy(Qt.CustomContextMenu)
        self.txt_export.customContextMenuRequested.connect(lambda: self.exporterContextMenu.exec_(QCursor.pos()))
        self.clearExporterAction = self.exporterContextMenu.addAction('Clear All')
        self.clearExporterAction.triggered.connect(lambda: self.txt_export.clear())

        #export error
        self.exporterErrorContextMenu = QMenu(self)
        self.txt_error_export.setContextMenuPolicy(Qt.CustomContextMenu)
        self.txt_error_export.customContextMenuRequested.connect(lambda: self.exporterErrorContextMenu.exec_(QCursor.pos()))
        self.clearExporterErrorAction = self.exporterErrorContextMenu.addAction('Clear All')
        self.clearExporterErrorAction.triggered.connect(lambda: self.txt_error_export.clear())

        #import log
        self.importerContextMenu = QMenu(self)
        self.txt_import.setContextMenuPolicy(Qt.CustomContextMenu)
        self.txt_import.customContextMenuRequested.connect(lambda: self.importerContextMenu.exec_(QCursor.pos()))
        self.clearImporterAction = self.importerContextMenu.addAction('Clear All')
        self.clearImporterAction.triggered.connect(lambda: self.txt_import.clear())

        #import error
        self.importerErrorContextMenu = QMenu(self)
        self.txt_error_import.setContextMenuPolicy(Qt.CustomContextMenu)
        self.txt_error_import.customContextMenuRequested.connect(lambda: self.importerErrorContextMenu.exec_(QCursor.pos()))
        self.clearImporterErrorAction = self.importerErrorContextMenu.addAction('Clear All')
        self.clearImporterErrorAction.triggered.connect(lambda: self.txt_error_import.clear())


    def setExporterTimer(self):
        if self.exporterTime>0:
            self.lbl_timer_export.setText(self.convertTime(time.time() - self.exporterTime))
    
    def setImporterTimer(self):
        if self.importerTime>0:
            self.lbl_timer_import.setText(self.convertTime(time.time() - self.importerTime))

    def convertTime(self, raw_time):
        hour = int(raw_time // 3600)
        minute = int((raw_time % 3600) // 60)
        second = int(raw_time % 60)

        return '{:0>2d}:{:0>2d}:{:0>2d}'.format(hour, minute, second)

    def exitSystem(self):
        if self.tray:
            self.tray.hide()

    def exitAll(self):
        if self.tray:
            self.tray.hide()
        sys.exit()


    @pyqtSlot()
    def on_btn_start_export_clicked(self):
        if len(self.exporterThreads) <= 0:
            #check
            if self.exporter.taskExists():
                reply = QMessageBox.question(self, 'Message', "The existing data will be cleared. Are you sure you want to restart?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
                allow = reply == QMessageBox.Yes
            else:
                allow = True
            if not allow:
                return

            self.exporterTime = time.time()
            self.pb_export.setValue(0)
            
            self.btn_start_export.setDisabled(True)
            self.btn_resume_export.setDisabled(True)
            self.btn_stop_export.setDisabled(False) 

            self.exporterTotalNum = 0
            self.exporterFailureNum = 0
            self.lbl_export.setText('Total %d Failure %d' % (self.exporterTotalNum, self.exporterFailureNum))

            t = threading.Thread(target=self.exporter.runTask,args=(False, self.chk_loop_export.isChecked()))
            self.exporterThreads.append(t)
            self.exporterThreads[0].setDaemon(True)
            self.exporterThreads[0].start()

        else:
            self.logExporter({'str':'There are other processes already running, please run later.','extra':None})


    @pyqtSlot()
    def on_btn_resume_export_clicked(self):
        if len(self.exporterThreads) <= 0:
            self.exporterTime = time.time()
            self.pb_export.setValue(0)
            
            self.btn_start_export.setDisabled(True)
            self.btn_resume_export.setDisabled(True)
            self.btn_stop_export.setDisabled(False) 

            t = threading.Thread(target=self.exporter.runTask,args=(True, self.chk_loop_export.isChecked()))
            self.exporterThreads.append(t)
            self.exporterThreads[0].setDaemon(True)
            self.exporterThreads[0].start()

        else:
            self.logExporter({'str':'There are other processes already running, please run later.','extra':None})
        
    @pyqtSlot()
    def on_btn_stop_export_clicked(self):
        self.exporter.stopTask()
        self.exporterThreads.clear()

        self.btn_start_export.setDisabled(False)
        self.btn_resume_export.setDisabled(False)
        self.btn_stop_export.setDisabled(True)

        self.exporterTime = 0


    @pyqtSlot()
    def on_btn_start_import_clicked(self):
        if len(self.importerThreads) <= 0:
            #check
            if self.importer.taskExists():
                reply = QMessageBox.question(self, 'Message', "The existing data will be cleared. Are you sure you want to restart?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
                allow = reply == QMessageBox.Yes
            else:
                allow = True
            if not allow:
                return

            self.importerTime = time.time()
            self.pb_import.setValue(0)
            
            self.btn_start_import.setDisabled(True)
            self.btn_resume_import.setDisabled(True)
            self.btn_stop_import.setDisabled(False) 

            self.importerTotalNum = 0
            self.importerFailureNum = 0
            self.lbl_import.setText('Total %d Failure %d' % (self.importerTotalNum, self.importerFailureNum))

            t = threading.Thread(target=self.importer.runTask,args=(False, self.chk_loop_import.isChecked()))
            self.importerThreads.append(t)
            self.importerThreads[0].setDaemon(True)
            self.importerThreads[0].start()

        else:
            self.logImporter({'str':'There are other processes already running, please run later.','extra':None})


    @pyqtSlot()
    def on_btn_resume_import_clicked(self):
        if len(self.importerThreads) <= 0:
            self.importerTime = time.time()
            self.pb_import.setValue(0)
            
            self.btn_start_import.setDisabled(True)
            self.btn_resume_import.setDisabled(True)
            self.btn_stop_import.setDisabled(False) 

            t = threading.Thread(target=self.importer.runTask,args=(True, self.chk_loop_import.isChecked()))
            self.importerThreads.append(t)
            self.importerThreads[0].setDaemon(True)
            self.importerThreads[0].start()

        else:
            self.logImporter({'str':'There are other processes already running, please run later.','extra':None})
        
    @pyqtSlot()
    def on_btn_stop_import_clicked(self):
        self.importer.stopTask()
        self.importerThreads.clear()

        self.btn_start_import.setDisabled(False)
        self.btn_resume_import.setDisabled(False)
        self.btn_stop_import.setDisabled(True)

        self.importerTime = 0

    def logExporter(self, o):
        msg = '['+time.strftime("%H:%M:%S", time.localtime()) + ']' + o['str']
        self.txt_export.appendPlainText(msg) 

        if o['extra']:
            if o['extra'][0] == 'exit':
                QMessageBox.critical(self, 'Message', o['str'], QMessageBox.Ok, QMessageBox.Ok) 
                sys.exit()

            elif o['extra'][0] == 'error':
                self.txt_error_export.appendPlainText(msg)
                self.exporter.saveError(msg) 

            elif o['extra'][0] == 'update':
                self.exporterTotalNum += int(o['extra'][2])
                self.exporterFailureNum += int(o['extra'][3])
                self.lbl_export.setText('Total %s Failure %s' % (format(self.exporterTotalNum, '0,'), format(self.exporterFailureNum, '0,')))

            elif o['extra'][0] == 'end':
                self.btn_start_export.setDisabled(False)
                self.btn_resume_export.setDisabled(False)
                self.btn_stop_export.setDisabled(False)
                self.exporterThreads.clear()
                self.exporterTime = 0
                    
            #progress
            if o['extra'][0] in ['progress', 'end', 'update']:
                #o['extra'][1]>self.pb_export.value() and self.pb_export.setValue(o['extra'][1])
                self.pb_export.setValue(o['extra'][1])


    def logImporter(self, o):
        msg = '['+time.strftime("%H:%M:%S", time.localtime()) + ']' + o['str']
        self.txt_import.appendPlainText(msg) 

        if o['extra']:
            if o['extra'][0] == 'exit':
                QMessageBox.critical(self, 'Message', o['str'], QMessageBox.Ok, QMessageBox.Ok) 
                sys.exit()

            elif o['extra'][0] == 'error':
                self.txt_error_import.appendPlainText(msg) 
                self.importer.saveError(msg)

            elif o['extra'][0] == 'update':
                self.importerTotalNum += int(o['extra'][2])
                self.importerFailureNum += int(o['extra'][3])
                self.lbl_import.setText('Total %s Failure %s' % (format(self.importerTotalNum, '0,'), format(self.importerFailureNum, '0,')))

            elif o['extra'][0] == 'end':
                self.btn_start_import.setDisabled(False)
                self.btn_resume_import.setDisabled(False)
                self.btn_stop_import.setDisabled(False)
                self.importerThreads.clear()
                self.importerTime = 0
                    
            #progress
            if o['extra'][0] in ['progress','end', 'update']:
                #o['extra'][1]>self.pb_import.value() and self.pb_import.setValue(o['extra'][1])
                self.pb_import.setValue(o['extra'][1])


    def loadData(self):
        if self.exporter.cfg['disabled']:
            self.groupBox.setHidden(True)

        if self.importer.cfg['disabled']:
            self.groupBox_2.setHidden(True)

        data = self.exporter.getTaskInfo()
        self.exporterTotalNum = data['total']
        self.exporterFailureNum = data['error']
        self.lbl_export.setText('Total %s Failure %s' % (format(self.exporterTotalNum, '0,'), format(self.exporterFailureNum, '0,')))
        self.pb_export.setValue(data['process'])

        data = self.importer.getTaskInfo()
        self.importerTotalNum = data['total']
        self.importerFailureNum = data['error']
        self.lbl_import.setText('Total %s Failure %s' % (format(self.importerTotalNum, '0,'), format(self.importerFailureNum, '0,')))
        self.pb_import.setValue(data['process'])

        self.btn_stop_export.setDisabled(True)
        self.btn_stop_import.setDisabled(True)

        self.txt_export.setReadOnly(True)
        self.txt_export.clear()
        self.txt_error_export.setReadOnly(True)
        self.txt_error_export.clear()
        self.txt_import.setReadOnly(True)
        self.txt_import.clear()
        self.txt_error_import.setReadOnly(True)
        self.txt_error_import.clear()

        self.exporterTimer = QTimer()
        self.exporterTimer.timeout.connect(self.setExporterTimer)
        self.exporterTimer.start(1000)

        self.importerTimer = QTimer()
        self.importerTimer.timeout.connect(self.setImporterTimer)
        self.importerTimer.start(1000)
        
        
        #splitter
        self.top_splitter.setStretchFactor(1,2)
        self.bottom_splitter.setStretchFactor(1,2)

#common func
def isNewSystem():
    return float('%d.%d' % (sys.version_info[0],sys.version_info[1])) >= 3.7

def isWindows():
    return platform.system() == 'Windows'

#handle error
def saveError(v):
    #save
    s = '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']\n' + v + '\n'
    p = os.path.dirname(os.path.realpath(sys.argv[0])) + '/error.log'
    with open(p, "a+", encoding="utf-8") as f:
        f.write(s)
def errorHandler(type, value, trace):  
    v = 'Main Error: \n%s' % (''.join(traceback.format_exception(type, value, trace)))
    print(v)
    saveError(v)
    sys.__excepthook__(type, value, trace) 
sys.excepthook = errorHandler

#main
if __name__ == '__main__':
    #scale
    if isNewSystem():QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    if isNewSystem():app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setQuitOnLastWindowClosed(False)
    
    dlg = MainWindow()
    
    #single instance
    if  isWindows() and isNewSystem():
        import win32con,win32file,pywintypes
        
        LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
        LOCK_SH = 0
        LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
        __overlapped = pywintypes.OVERLAPPED()

        pid_dir = dlg.tmpPath
        self_name = os.path.basename(sys.argv[0])[0:os.path.basename(sys.argv[0]).rfind('.')]
        if os.path.exists(pid_dir):
            try:
                fd = open(pid_dir + '/'+self_name+'.pid', 'w')
                hfile = win32file._get_osfhandle(fd.fileno())
                win32file.LockFileEx(hfile, LOCK_EX | LOCK_NB, 0, 0xffff0000,__overlapped)
            except:
                QMessageBox.critical(dlg, 'Message', "The program is already running, please click on the lower right tray icon to show window!", QMessageBox.Ok, QMessageBox.Ok) 
                sys.exit()
    elif not isWindows():
        import fcntl
        pid_dir = dlg.tmpPath
        self_name = os.path.basename(sys.argv[0])[0:os.path.basename(sys.argv[0]).rfind('.')]
        if os.path.exists(pid_dir):
            try:
                fd = open(pid_dir + '/'+self_name+'.pid', 'w')
                fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except:
                #traceback.print_exc()
                QMessageBox.critical(dlg, 'Message', "The program is already running, please click on the lower right tray icon to show window!", QMessageBox.Ok, QMessageBox.Ok) 
                sys.exit()
    
    
    #resize
    desktop = QApplication.desktop()
    screenRect = desktop.availableGeometry()
    dlgRect = dlg.geometry()
    if screenRect.width() < dlgRect.width() or screenRect.height()<dlgRect.height():
        dlg.resize(screenRect.width(), screenRect.height())
        dlg.showMaximized()
        dlg.show()
    else:
        #dlg.setWindowFlags(Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        dlg.show()
    del desktop
    del screenRect
    del dlgRect

    #show window
    try:
        #dlg.setWindowIcon(QIcon(dlg.logoIconPath))
        dlg.setWindowIcon(MyIcon.getLogoIcon())
        dlg.setWindowTitle('Synczer (%s)' % os.path.realpath(sys.argv[0]))
        dlg.loadData()

        if isWindows():
            dlg.addSystemTray()
        dlg.addContextMenu()
    except:
        traceback.print_exc()
        saveError('Startup Error:\n' + traceback.format_exc())
    finally:
        sys.exit(app.exec_())
