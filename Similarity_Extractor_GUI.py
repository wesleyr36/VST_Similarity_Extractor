import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import random as rdm

from Similarity_Extractor import similarity_difference_extractor as similarity_extractor

global file_1, file_2, difference

file_1, file_2, difference = None, None, False

def create_label(win, text_align, set_text, style, size_xy, xy):
    label = QLabel(win)
    label.setText(f"{set_text}")
    label.setStyleSheet(f"{style}")
    label.setFixedSize(size_xy[0], size_xy[1])
    label.move(xy[0], xy[1])
    
    if text_align == 'Centre':
        label.setAlignment(Qt.AlignCenter)
    elif text_align == 'Right':
        label.setAlignment(Qt.AlignRight)

    return label

def create_button(win, set_text, style, size_xy, xy, function):
    button = QPushButton(win)
    button.setText(f"{set_text}")
    button.setStyleSheet(f"{style}")
    button.setFixedSize(size_xy[0], size_xy[1])
    button.move(xy[0], xy[1])
    button.clicked.connect(function)
    
    return button

def create_text_entry(win, text_align, set_text, style, size_xy, xy):
    entry = QLineEdit(win)
    entry.setText(f"{set_text}")
    entry.setStyleSheet(f"{style}")
    entry.setFixedSize(size_xy[0], size_xy[1])
    entry.move(xy[0], xy[1])
    
    if text_align == 'Centre':
        entry.setAlignment(Qt.AlignCenter)
    elif text_align == 'Right':
        entry.setAlignment(Qt.AlignRight)
    
    return entry

def sel_file(win, label, file):
    global file_1, file_2
    # Open File Dialog
    fname = QFileDialog.getOpenFileName(win, "Open File")
    label.setText(os.path.basename(fname[0]))
    
    if file == "1":
        file_1 = fname[0]
    elif file == "2":
        file_2 = fname[0]

def difference_toggle(win, label, differenc):
    global difference
    if differenc == False:
        label.setText("True")
        difference = True
    else:
        label.setText("False")
        difference = False

def run_similarity_extractor(input_1, input_2, difference, output_name):
    if not None in [input_1, input_2]:
        if output_name.lower() != "optional":
            similarity_extractor(input_1, input_2, difference, output_name)
        else:
            similarity_extractor(input_1, input_2, difference, None)

        done = QMessageBox.information(None,
                                  "Processing Finished",
                                  "Your files have been processed, please check the folder containing input 1.",
                                  QMessageBox.Ok)
        if done == QMessageBox.Ok:
            return

    else:
        choice = QMessageBox.critical(None,
                                  "Error: No Inputs",
                                  "Please make sure you have selected both input files!",
                                  QMessageBox.Retry | QMessageBox.Cancel)
        if choice == QMessageBox.Retry:
            return
        else:
            print("Cancel")
            exit()

def window():
    app = QApplication(sys.argv)
    win = QDialog()
    win.setStyleSheet("background-color : black")

    #Input Text Labels
    input_1_label = create_label(win, 'Centre', "Input File 1", "color : white; background-color : black", [190, 40], [50, 20])
    input_2_label = create_label(win, 'Centre', "Input File 2", "color : white; background-color : black", [190, 40], [350, 20])

    #Input Path Labels
    input_1_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 70])
    input_2_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 70])

    #Input Selection Buttons
    input_1_sel = create_button(win, "Select Input 1", "color : white; background-color : grey", [190, 40], [50, 120], lambda:sel_file(win, input_1_path, "1"))
    input_1_sel = create_button(win, "Select Input 2", "color : white; background-color : grey", [190, 40], [350, 120], lambda:sel_file(win, input_2_path, "2"))

    #Differnce and Output Name Text Labels
    difference_label = create_label(win, 'Centre', "Output Differences?", "color : white; background-color : black", [190, 40], [50, 170])
    output_name_label = create_label(win, 'Centre', "Output File Name", "color : white; background-color : black", [190, 40], [350, 170])
    
    #Input Selection Buttons
    difference_button = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 220], lambda:difference_toggle(win, difference_button, difference))
    output_name_input = create_text_entry(win, 'Centre', "Optional", "color : white; background-color : grey", [190, 40], [350, 220])

    #Run Similarity Extraction Button
    similarity_button = create_button(win, "Extract Similarity", "color : white; background-color : grey", [490, 40], [50, 270], lambda:run_similarity_extractor(file_1, file_2, difference, output_name_input.text()))
    
    win.setFixedSize(590,360)
    win.setWindowTitle("Similarity Extractor GUI")
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
   window()
