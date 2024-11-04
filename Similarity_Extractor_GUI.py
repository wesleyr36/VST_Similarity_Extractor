import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import random as rdm
from libs.similarity_tasks import *
import json

global file_1, file_2, difference, sim_of_dif, post_process, ZF_infer, VR_infer, model_dir, store_dir

svd_set = json.load(open("settings.json"))

file_1, file_2, difference, sim_of_dif, post_process = None, None, False, False, False

ZF_infer, VR_infer, model_dir, store_dir = svd_set["settings"]["ZF_infer"], svd_set["settings"]["VR_infer"], svd_set["settings"]["model_dir"], svd_set["settings"]["store_dir"]

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

def create_drop_down(win, text_align, set_text, style, size_xy, xy):
    drop_down = QComboBox(win)
    drop_down.setStyleSheet(f"{style}")
    drop_down.setFixedSize(size_xy[0], size_xy[1])
    drop_down.move(xy[0], xy[1])
    
    # Add items from the provided list (assuming `set_text` is a list of items)
    if isinstance(set_text, list):
        drop_down.addItems(set_text)
    else:
        drop_down.addItem(set_text)

    if text_align == 'Centre':
        drop_down.setEditable(True)
        drop_down.lineEdit().setAlignment(Qt.AlignCenter)
        drop_down.setEditable(False)
    elif text_align == 'Right':
        drop_down.setEditable(True)
        drop_down.lineEdit().setAlignment(Qt.AlignRight)
        drop_down.setEditable(False)

    return drop_down


def sel_file(win, label, file, folder = False):
    global file_1, file_2, ZF_infer, VR_infer, model_dir, store_dir
    # Open File Dialog
    if folder != False:
        fname = QFileDialog.getExistingDirectory(win, "Open Folder")
        label.setText(os.path.basename(fname))
        print(fname)
        if file == "1":
            model_dir = fname
            svd_set["settings"]["model_dir"] = fname
            print(svd_set)
        elif file == "2":
            store_dir = fname
            svd_set["settings"]["store_dir"] = fname
        with open('settings.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(svd_set))
        print(svd_set)
    else:
        fname = QFileDialog.getOpenFileName(win, "Open File")
        label.setText(os.path.basename(fname[0]))
    
        if file == "1":
            file_1 = fname[0]
        elif file == "2":
            file_2 = fname[0]
        elif file == "3":
            ZF_infer = fname[0]
            svd_set["settings"]["ZF_infer"] = fname[0]
        elif file == "4":
            VR_infer = fname[0]
            svd_set["settings"]["VR_infer"] = fname[0]
            print(svd_set)
        with open('settings.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(svd_set))
        print(svd_set)

def difference_toggle(win, label, differenc):
    global difference
    if differenc == False:
        label.setText("True")
        difference = True
    else:
        label.setText("False")
        difference = False

def sim_of_dif_toggle(win, label, sim_of_di):
    global sim_of_dif
    if sim_of_di == False:
        label.setText("True")
        sim_of_dif = True
    else:
        label.setText("False")
        sim_of_dif = False
        
def post_proc_toggle(win, label, post_proces):
    global post_process
    if post_proces == False:
        label.setText("True")
        post_process = True
    else:
        label.setText("False")
        post_process = False

"""def run_similarity_extractor(input_1, input_2, difference, output_name, sim_of_dif):
    print("pressed")
    if not None in [input_1, input_2]:
        try:
            if output_name.lower() != "optional":
                similarity_extractor(input_1, input_2, difference, output_name, sim_of_dif)
            else:
                similarity_extractor(input_1, input_2, difference, None, sim_of_dif)
            
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
        except Exception as e:
            print(e)"""

def bertom_based(win):
    #Input Text Labels
    input_1_label = create_label(win, 'Centre', "Input File 1", "color : white; background-color : black", [190, 40], [50, 20])
    input_2_label = create_label(win, 'Centre', "Input File 2", "color : white; background-color : black", [190, 40], [350, 20])

    #Input Path Labels
    input_1_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 70])
    input_2_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 70])

    #Input Selection Buttons
    input_1_sel = create_button(win, "Select Input 1", "color : white; background-color : grey", [190, 40], [50, 120], lambda:sel_file(win, input_1_path, "1"))
    input_2_sel = create_button(win, "Select Input 2", "color : white; background-color : grey", [190, 40], [350, 120], lambda:sel_file(win, input_2_path, "2"))

    #Differnce and Output Name Text Labels
    difference_label = create_label(win, 'Centre', "Output Differences?", "color : white; background-color : black", [190, 40], [50, 170])
    output_name_label = create_label(win, 'Centre', "Output File Name", "color : white; background-color : black", [190, 40], [350, 170])
    
    #Difference and Name Fields
    difference_button = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 220], lambda:difference_toggle(win, difference_button, difference))
    output_name_input = create_text_entry(win, 'Centre', "Optional", "color : white; background-color : grey", [190, 40], [350, 220])

    #Similarity of Differences
    sim_of_dif_label = create_label(win, 'Centre', "Output Similarity of inverted Differences?\n(some similarities can be phase inverted)", "color : white; background-color : black", [290, 40], [152, 270])
    sim_of_dif_button = create_button(win, "False", "color : white; background-color : grey", [190, 40], [203, 320], lambda:sim_of_dif_toggle(win, sim_of_dif_button, sim_of_dif))
    
    #Post-Processing
    post_proc_label = create_label(win, 'Centre', "Apply Post-Processing?", "color : white; background-color : black", [190, 40], [202, 420])
    post_proc_togle = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 470], lambda:post_proc_toggle(win, post_proc_togle, post_process))
    post_proc_dmenu = create_drop_down(win, 'Centre', ["VR V6.0.0b4 - 2K FFT", "VR V6.0.0b4 - 4K FFT","MDX23C - 2K FFT", "MDX23C - 4K FFT"], "color : white; background-color : grey", [190, 40], [350, 470])
    
    #Run Similarity Extraction Button
    similarity_button = create_button(win, "Extract Similarity", "color : white; background-color : grey", [490, 40], [50, 370], lambda:run_similarity_extractor("bertom", file_1, file_2, difference, output_name_input.text(), sim_of_dif, post_process, post_proc_dmenu.currentText()))

def mdx23c_based(win):
    #Input Text Labels
    input_1_label = create_label(win, 'Centre', "Input File 1", "color : white; background-color : black", [190, 40], [50, 20])
    input_2_label = create_label(win, 'Centre', "Input File 2", "color : white; background-color : black", [190, 40], [350, 20])

    #Input Path Labels
    input_1_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 70])
    input_2_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 70])

    #Input Selection Buttons
    input_1_sel = create_button(win, "Select Input 1", "color : white; background-color : grey", [190, 40], [50, 120], lambda:sel_file(win, input_1_path, "1"))
    input_2_sel = create_button(win, "Select Input 2", "color : white; background-color : grey", [190, 40], [350, 120], lambda:sel_file(win, input_2_path, "2"))

    #Differnce and Output Name Text Labels
    difference_label = create_label(win, 'Centre', "Output Differences?", "color : white; background-color : black", [190, 40], [50, 170])
    output_name_label = create_label(win, 'Centre', "Output File Name", "color : white; background-color : black", [190, 40], [350, 170])
    
    #Difference and Name Fields
    difference_button = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 220], lambda:difference_toggle(win, difference_button, difference))
    output_name_input = create_text_entry(win, 'Centre', "Optional", "color : white; background-color : grey", [190, 40], [350, 220])

    #Model Selection:
    model_sel_label = create_label(win, 'Centre', "Which model?", "color : white; background-color : black", [190, 40], [202, 270])
    model_sel_dmenu = create_drop_down(win, 'Centre', ["MDX23C - 2K FFT", "MDX23C - 4K FFT"], "color : white; background-color : grey", [190, 40], [202, 320])
    
    #Post-Processing
    post_proc_label = create_label(win, 'Centre', "Apply Post-Processing?", "color : white; background-color : black", [190, 40], [202, 420])
    post_proc_togle = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 470], lambda:post_proc_toggle(win, post_proc_togle, post_process))
    post_proc_dmenu = create_drop_down(win, 'Centre', ["VR V6.0.0b4 - 2K FFT", "VR V6.0.0b4 - 4K FFT","MDX23C - 2K FFT", "MDX23C - 4K FFT"], "color : white; background-color : grey", [190, 40], [350, 470])
    
    #Run Similarity Extraction Button
    similarity_button = create_button(win, "Extract Similarity", "color : white; background-color : grey", [490, 40], [50, 370], lambda:run_similarity_extractor(model_sel_dmenu.currentText(), file_1, file_2, difference, output_name_input.text(), False, post_process, post_proc_dmenu.currentText()))

def vr_v6b4_based(win):
    #Input Text Labels
    input_1_label = create_label(win, 'Centre', "Input File 1", "color : white; background-color : black", [190, 40], [50, 20])
    input_2_label = create_label(win, 'Centre', "Input File 2", "color : white; background-color : black", [190, 40], [350, 20])

    #Input Path Labels
    input_1_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 70])
    input_2_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 70])

    #Input Selection Buttons
    input_1_sel = create_button(win, "Select Input 1", "color : white; background-color : grey", [190, 40], [50, 120], lambda:sel_file(win, input_1_path, "1"))
    input_2_sel = create_button(win, "Select Input 2", "color : white; background-color : grey", [190, 40], [350, 120], lambda:sel_file(win, input_2_path, "2"))

    #Differnce and Output Name Text Labels
    difference_label = create_label(win, 'Centre', "Output Differences?", "color : white; background-color : black", [190, 40], [50, 170])
    output_name_label = create_label(win, 'Centre', "Output File Name", "color : white; background-color : black", [190, 40], [350, 170])
    
    #Difference and Name Fields
    difference_button = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 220], lambda:difference_toggle(win, difference_button, difference))
    output_name_input = create_text_entry(win, 'Centre', "Optional", "color : white; background-color : grey", [190, 40], [350, 220])

    #Model Selection
    model_sel_label = create_label(win, 'Centre', "Which model?", "color : white; background-color : black", [190, 40], [50, 270])
    model_sel_dmenu = create_drop_down(win, 'Centre', ["VR V6.0.0b4 - 2K FFT", "VR V6.0.0b4 - 4K FFT"], "color : white; background-color : grey", [190, 40], [50, 320])

    #Double Processing - reusing sim_of_dif since it's not too dissimilar
    double_proc_label = create_label(win, 'Centre', "Use double Processing?\n (more complete but more bleeding)", "color : white; background-color : black", [255, 40], [315, 270])
    double_proc_togle = create_button(win, "False", "color : white; background-color : grey", [190, 40], [350, 320], lambda:sim_of_dif_toggle(win, double_proc_togle, sim_of_dif))
    
    #Post-Processing
    post_proc_label = create_label(win, 'Centre', "Apply Post-Processing?", "color : white; background-color : black", [190, 40], [202, 420])
    post_proc_togle = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 470], lambda:post_proc_toggle(win, post_proc_togle, post_process))
    post_proc_dmenu = create_drop_down(win, 'Centre', ["VR V6.0.0b4 - 2K FFT", "VR V6.0.0b4 - 4K FFT","MDX23C - 2K FFT", "MDX23C - 4K FFT"], "color : white; background-color : grey", [190, 40], [350, 470])
    
    #Run Similarity Extraction Button
    similarity_button = create_button(win, "Extract Similarity", "color : white; background-color : grey", [490, 40], [50, 370], lambda:run_similarity_extractor(model_sel_dmenu.currentText(), file_1, file_2, difference, output_name_input.text(), sim_of_dif, post_process, post_proc_dmenu.currentText()))

def settings_func(win):
    #Settings Labels
    ZF_infer_label = create_label(win, 'Centre', "ZFTurbo Inference\nScript Path", "color : white; background-color : black", [190, 40], [50, 20])
    VR_infer_label = create_label(win, 'Centre', "VR v6.0.0b4 Inference\nScript Path", "color : white; background-color : black", [190, 40], [350, 20])
    model_dir_label = create_label(win, 'Centre', "Model Folder", "color : white; background-color : black", [190, 40], [50, 170])
    store_dir_label = create_label(win, 'Centre', "Output Folder", "color : white; background-color : black", [190, 40], [350, 170])

    #Settings Path Label
    ZF_infer_path = create_label(win, 'Left', f"{ZF_infer}", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 70])
    VR_infer_path = create_label(win, 'Left', f"{VR_infer}", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 70])
    model_dir_path = create_label(win, 'Left', f"{model_dir}", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 220])
    store_dir_path = create_label(win, 'Left', f"{store_dir}", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 220])

    #Input Selection Buttons
    ZF_infer_sel = create_button(win, "Select Inference Script", "color : white; background-color : grey", [190, 40], [50, 120], lambda:sel_file(win, ZF_infer_path, "3", False))
    VR_infer_sel = create_button(win, "Select Inference Script", "color : white; background-color : grey", [190, 40], [350, 120], lambda:sel_file(win, VR_infer_path, "4", False))
    model_dir_sel = create_button(win, "Select Models Directory", "color : white; background-color : grey", [190, 40], [50, 270], lambda:sel_file(win, model_dir_path, "1", True))
    store_dir_sel = create_button(win, "Select Output Folder", "color : white; background-color : grey", [190, 40], [350, 270], lambda:sel_file(win, store_dir_path, "2", True))

def window():
    app = QApplication(sys.argv)
    win = QDialog()
    win.setStyleSheet("background-color : black")
    win.layout = QVBoxLayout(win) 

    #Type label
    extraction_lab = create_label(win, 'Extraction Type', "Extraction Type:", "color : white; background-color : black", [190, 40], [15, -12.5])
    
    #Initialize tab screen 
    tabs = QTabWidget()
    tabs.setStyleSheet("""
    QTabBar::tab {
        height: 20px;  /* Set the height of each tab */
        padding: 2px;  /* Add padding if needed */
        color : white;
        border : 1px solid grey;
    }
    QTabBar::tab::selected {
        color : white;
        background-color: grey;
        border : 1px solid white;
    }
    """)
    tab1 = QWidget()
    tab1.layout = QVBoxLayout(win)
    tabs.addTab(tab1, "Bertom Phantom Centre")

    tab2 = QWidget()
    tab2.layout = QVBoxLayout(win)
    tabs.addTab(tab2, "AI arch - MDX23C")

    tab3 = QWidget()
    tab3.layout = QVBoxLayout(win)
    tabs.addTab(tab3, "AI arch - VR V6.0.0b4")

    settings = QWidget()
    settings.layout = QVBoxLayout(win)
    tabs.addTab(settings, "⚙Options⚙")
          
    #Add tab contents
    bertom = bertom_based(tab1)
    tab1.layout.addWidget(bertom) 
    tab1.setLayout(tab1.layout) 

    mdx23c = mdx23c_based(tab2)
    tab2.layout.addWidget(mdx23c) 
    tab2.setLayout(tab2.layout) 
 
    vrv6 = vr_v6b4_based(tab3)
    tab3.layout.addWidget(vrv6) 
    tab3.setLayout(tab3.layout)
    
    settingss = settings_func(settings)
    settings.layout.addWidget(settingss) 
    settings.setLayout(settings.layout) 
    
    #Add tabs to widget 
    win.layout.addWidget(tabs) 
    win.setLayout(win.layout)

    #Setup Window
    win.setFixedSize(628,605)
    win.setWindowTitle("Similarity Extractor GUI")
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
   window()
