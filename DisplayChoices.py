import sys
import time
import threading
from PyQt5.QtCore import Qt
import os
import ctypes
from GenerateRaces import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon
import configparser

"""

    Author Maxence LEVESQUE @waylow1 on github

"""



class InputWidget(QWidget):
    def __init__(self, label_text):
        super().__init__()
        self.label = QLabel(label_text)
        self.input_field = QLineEdit()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        self.setLayout(layout)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Make your choices')
        self.setGeometry(100, 100, 300, 250)
        self.setWindowIcon(QIcon("assets/favicon.ico"))

        self.number_of_lane_input = InputWidget("Number of lanes:")
        self.number_of_heat_input = InputWidget("Number of rounds:")
        self.number_of_racer_input = InputWidget("Number of racers:")

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.number_of_lane_input)
        layout.addWidget(self.number_of_heat_input)
        layout.addWidget(self.number_of_racer_input)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

        config = configparser.ConfigParser()
        config.read("config.ini")

        if not is_admin():
            QMessageBox.warning(self, "Warning", "You are not admin!", QMessageBox.Ok)

        try:
            self.number_of_lane_input.input_field.setText(config['DEFAULT']['LANES'])
            self.number_of_heat_input.input_field.setText(config['DEFAULT']['ROUNDS'])
        except Exception as e:
            QMessageBox.critical(self, "Config file not found", "There is no config.ini")

        self.number_of_racer_input.input_field.setFocus(Qt.OtherFocusReason)

    def create_button_clicked(self):
        try:
            num_lanes = int(self.number_of_lane_input.input_field.text())
            num_heats = int(self.number_of_heat_input.input_field.text())
            num_racers = int(self.number_of_racer_input.input_field.text())

            if (num_racers > 0) and (num_lanes > 0) and (num_heats > 0) and (
                    num_lanes <= num_racers):
                QMessageBox.information(self, "Race Creation", "Races will be created.")
                generator = GenerateRaces(num_lanes, num_heats, num_racers)
                success = generator.buildTextFile()
                if success:
                    while generator.value != num_heats * num_racers or not success:
                        generator = GenerateRaces(num_lanes, num_heats, num_racers)
                        success = generator.buildTextFile()
                    if success:
                        generator.writeRaceFile(generator.text_file_content)
                        QMessageBox.information(self, "Race Creation", "Done !")
                    else:
                        QMessageBox.information(self, "Race Creation", "Rerun")
                else:
                    QMessageBox.information(self, "Race Creation Failed", "Rerun", QMessageBox.Ok)

            else:
                error_message = "Conditions not met:\n"
                if num_racers <= 0:
                    error_message += "- Number of racers should be greater than zero.\n"
                if num_lanes <= 0:
                    error_message += "- Number of lanes should be greater than zero.\n"
                if num_heats <= 0:
                    error_message += "- Number of rounds should be greater than zero.\n"
                if num_racers < num_lanes:
                    error_message += "- You can't have more lanes than racers.\n"
                QMessageBox.warning(self, "Conditions not met", error_message)
        except ValueError as e:
            print("ValueError:", e)
            QMessageBox.critical(self, "Error", "Please enter valid numbers.")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
