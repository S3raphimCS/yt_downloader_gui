import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from des import *
import youtube_dl
from os import chdir


class Downloader(QtCore.QThread):
    mysignal = QtCore.pyqtSignal(str)

    class MyLogger:

        def __init__(self, window):
            self.window = window

        def debug(self, msg):
            self.window.ui.logs.append(msg)

        def warning(self, msg):
            self.window.ui.logs.append(msg)

        def error(self, msg):
            if 'is not a valid url' in msg:
                raise ValueError('Invalid url')

            else:
                return f'An error has occured - {msg}'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.url = None
        self.window = None

    def run(self):
        try:
            self.mysignal.emit('Download has been started')

            with youtube_dl.YoutubeDL({'logger': self.MyLogger(self.window)}) as ydl:
                ydl.download([self.url])

        except Exception as error:
            self.mysignal.emit(f'Download has been canceled due to {error}')

        else:
            self.mysignal.emit('The video is successfully uploaded')

        finally:
            self.mysignal.emit('Download completed')
            self.window.locker(False)

    def init_args(self, url, window):
        self.url = url
        self.window = window


class GUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Standard download folder
        self.download_folder = None

        # Initialization of thread
        self.downloader = Downloader(self)
        self.downloader.mysignal.connect(self.handler)

        # Function for clicked button "Choose the folder"
        self.ui.choose_folder.clicked.connect(self.set_folder)

        # Function for clicked button "Download the video"
        self.ui.download.clicked.connect(lambda: self.ui.logs.setText(''))
        self.ui.download.clicked.connect(self.start)

    def start(self):
        if len(self.ui.place_for_url.text()) > 5:
            if self.download_folder is not None:
                link = self.ui.place_for_url.text()
                self.downloader.init_args(link, self)
                self.downloader.start()
                self.locker(True)
            else:
                QtWidgets.QMessageBox.warning(self, 'Error',
                                              'No folder selected')
        else:
            QtWidgets.QMessageBox.warning(self, 'Error',
                                          "No video link provided")

    def handler(self, value):
        if value == 'finish':
            self.locker(False)
        else:
            self.ui.logs.append(value)

    def locker(self, value):
        buttons = [self.ui.download, self.ui.choose_folder]
        for button in buttons:
            button.setDisabled(value)

    def set_folder(self):
        self.download_folder = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                          'Choose the folder for saving')
        if self.download_folder:
            chdir(self.download_folder)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    window.show()
    sys.exit(app.exec_())
