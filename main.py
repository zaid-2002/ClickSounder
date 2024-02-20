# Import modul yang diperlukan
from asset.GUI.gui import Ui_MainWindow
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QMainWindow, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from pynput.mouse import Button, Listener
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import threading
import shutil

state = False

try:
    os.makedirs("asset/sound")
    folder_path = os.path.join('asset','sound')
except FileExistsError:
    folder_path = os.path.join('asset','sound')

# default
rm = lm = True
file_lmp = file_rmp = 'click_1.wav'
file_lmr = file_rmr = 'click_2.wav'

class FileBrowser(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        file_dialog = QFileDialog()
        filenames = file_dialog.getOpenFileName(self, "Choose File", "", "WAV Files (*.wav)")
        self.filename = filenames

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Buat objek UI dari kelas yang dihasilkan oleh pyuic
        self.setWindowIcon(QIcon(QPixmap("favico.ico")))
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        ui = self.ui
        
        ui.volume_slider.setMinimum(0)
        ui.volume_slider.setMaximum(100)
        ui.volume_slider.setValue(50)
        ui.RM.setChecked(True)
        ui.LM.setChecked(True)
        self.check_file(file_rmp)
        ui.rmp_text.setText(filename)
        self.check_file(file_rmr)
        ui.rmr_text.setText(filename)
        self.check_file(file_lmp)
        ui.lmp_text.setText(filename)
        self.check_file(file_lmr)
        ui.lmr_text.setText(filename)

        ui.volume_slider.valueChanged.connect(self.set_volume)
        ui.start_button.clicked.connect(self.start_detection)
        ui.stop_button.clicked.connect(self.stop_detection)
        ui.browse_button.clicked.connect(self.browse_file)
        ui.import_button.clicked.connect(self.import_file)
        sound_dir = 'asset/sound'
        if os.path.exists(sound_dir):
            wav_files = [file for file in os.listdir(sound_dir) if file.endswith('.wav')]
            ui.RMP.addItems(wav_files)
            ui.RMR.addItems(wav_files)
            ui.LMP.addItems(wav_files)
            ui.LMR.addItems(wav_files)
            self.set_combobox_index()
        ui.save_button.clicked.connect(self.save_selected_file)

        # Deteksi mouse
        listener = Listener(on_click=self.on_click)
        listener.start()

    def check_file(self, file):
        global filename
        if os.path.exists(os.path.join("asset","sound", file)):
            filename = file
        else: 
            filename = "None"
        
    def set_combobox_index(self):
        index_rmp = self.ui.RMP.findText(file_rmp, Qt.MatchFlag.MatchFixedString)
        index_rmr = self.ui.RMR.findText(file_rmr, Qt.MatchFlag.MatchFixedString)
        index_lmp = self.ui.LMP.findText(file_lmp, Qt.MatchFlag.MatchFixedString)
        index_lmr = self.ui.LMR.findText(file_lmr, Qt.MatchFlag.MatchFixedString)
        if index_rmp >= 0:
            self.ui.RMP.setCurrentIndex(index_rmp)
        if index_rmr >= 0:
            self.ui.RMR.setCurrentIndex(index_rmr)
        if index_lmp >= 0:
            self.ui.LMP.setCurrentIndex(index_lmp)
        if index_lmr >= 0:
            self.ui.LMR.setCurrentIndex(index_lmr)

    def play_sound(self, file):
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

    def set_volume(self, value):
        volume = value / 100.0
        pygame.mixer.init()
        pygame.mixer.music.set_volume(volume)

    def save_selected_file(self):
        global file_lmp, file_lmr, file_rmp, file_rmr, rm, lm
        
        file_rmp = self.ui.RMP.currentText()
        file_rmr = self.ui.RMR.currentText()
        file_lmp = self.ui.LMP.currentText()
        file_lmr = self.ui.LMR.currentText()

        self.ui.rmp_text.setText(os.path.splitext(file_rmp)[0])
        self.ui.rmr_text.setText(os.path.splitext(file_rmr)[0])
        self.ui.lmp_text.setText(os.path.splitext(file_lmp)[0])
        self.ui.lmr_text.setText(os.path.splitext(file_lmr)[0])

        if self.ui.RM.isChecked():
            rm = True
        else:
            rm = False
        if self.ui.LM.isChecked():
            lm = True
        else:
            lm = False
        
    def browse_file(self):
        filenames = FileBrowser()
        filename = filenames.filename[0]
        if filename:
            self.ui.path.setPlainText(filename)

    def import_file(self):
        source_file = self.ui.path.toPlainText()
        destination_folder = "asset/sound"
        try:
            shutil.copy(source_file, destination_folder)
            message_box = QMessageBox()
            message_box.setWindowTitle("Notifikasi")
            message_box.setText("Success!")
            message_box.exec()
            sound_dir = 'asset/sound'
            if os.path.exists(sound_dir):
                self.ui.RMP.clear()
                self.ui.RMR.clear()
                self.ui.LMP.clear()
                self.ui.LMR.clear()
                wav_files = [file for file in os.listdir(sound_dir) if file.endswith('.wav')]
                self.ui.RMP.addItems(wav_files)
                self.ui.RMR.addItems(wav_files)
                self.ui.LMP.addItems(wav_files)
                self.ui.LMR.addItems(wav_files)
                self.set_combobox_index()
        except : 
            message_box = QMessageBox()
            message_box.setWindowTitle("Notifikasi")
            message_box.setText("Failed!")
            message_box.exec()


    def start_detection(self):
        global state
        state = True
        self.ui.status_bar.setText("ON")
        self.ui.status_bar.setStyleSheet("background-color: rgb(85, 255, 0);")

    def stop_detection(self):
        global state
        state = False
        self.ui.status_bar.setText("OFF")
        self.ui.status_bar.setStyleSheet("background-color: rgb(255, 0, 0);")

    def on_click(self, x, y, button, pressed):
        global state, rm, lm
        if pressed and state:
            if button == Button.right and rm:
                # Mendapatkan path file lengkap dari folder dan nama file
                file_path = os.path.join(folder_path, file_rmp)
                threading.Thread(target=self.play_sound, args=(file_path,)).start()
            if button == Button.left and lm:
                # Mendapatkan path file lengkap dari folder dan nama file
                file_path = os.path.join(folder_path, file_lmp)
                threading.Thread(target=self.play_sound, args=(file_path,)).start()
        if not pressed and state:
            if button == Button.right and rm:
                # Mendapatkan path file lengkap dari folder dan nama file
                file_path = os.path.join(folder_path, file_rmr)
                threading.Thread(target=self.play_sound, args=(file_path,)).start()
            if button == Button.left and lm:
                # Mendapatkan path file lengkap dari folder dan nama file
                file_path = os.path.join(folder_path, file_lmr)
                threading.Thread(target=self.play_sound, args=(file_path,)).start()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap('favico.ico')))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
