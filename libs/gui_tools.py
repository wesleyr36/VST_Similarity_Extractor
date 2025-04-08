import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import random as rdm
from libs.similarity_tasks import *
import json

svd_set = json.load(open("settings.json"))

def create_pbar(win, style, size_xy, xy, accessible_name = "", accessible_description = ""):
    progress_bar = QProgressBar(win)
    progress_bar.setStyleSheet(f"{style}") #set style info
    progress_bar.setFixedSize(size_xy[0], size_xy[1]) #set the size of the label
    progress_bar.move(xy[0], xy[1]) #set its postion
    progress_bar.setAccessibleName(accessible_name) #set the name for accesibility, to be read out by a screenreader
    progress_bar.setAccessibleDescription(accessible_description) #set the description for accesibility, to be read out by a screenreader

    return progress_bar

def update_pbar(pbar, increment):
    #get the current value of the progess bar
    current_value = pbar.value()
    #add the increment to the current value of the progress bar but ensuring it never goes above 100
    new_value = min(increment + current_value, 100)
    #set the new value
    pbar.setValue(new_value)

def create_label(win, text_align, set_text, style, size_xy, xy, tool_tip=None, accessible_name = "", accessible_description = ""):
    label = QLabel(win) #init label
    label.setText(f"{set_text}") #add text
    label.setStyleSheet(f"{style}") #set style info
    label.setFixedSize(size_xy[0], size_xy[1]) #set the size of the label
    label.move(xy[0], xy[1]) #set its postion
    label.setAccessibleName(accessible_name) #set the name for accesibility, to be read out by a screenreader
    label.setAccessibleDescription(accessible_description) #set the description for accesibility, to be read out by a screenreader

    #set its text alginment
    if text_align == 'Centre':
        label.setAlignment(Qt.AlignCenter)
    elif text_align == 'Right':
        label.setAlignment(Qt.AlignRight)

    if tool_tip != None:
        label.setToolTip(tool_tip)

    return label #return the label

def create_button(win, set_text, style, size_xy, xy, function, tool_tip=None, accessible_name = "", accessible_description = ""):
    button = QPushButton(win) #init button
    button.setText(f"{set_text}") #add text
    button.setStyleSheet(f"{style}") #set style info
    button.setFixedSize(size_xy[0], size_xy[1]) #set the size of the button
    button.move(xy[0], xy[1]) #set the position of the button
    button.clicked.connect(function) #set the function of the button
    button.setAccessibleName(accessible_name) #set the name for accesibility, to be read out by a screenreader
    button.setAccessibleDescription(accessible_description) #set the description for accesibility, to be read out by a screenreader

    if tool_tip != None:
        button.setToolTip(tool_tip)

    return button #return the button

def create_text_entry(win, text_align, set_text, style, size_xy, xy, tool_tip=None, accessible_name = "", accessible_description = ""):
    entry = QLineEdit(win) #init text entry box
    entry.setText(f"{set_text}") #set default text
    entry.setStyleSheet(f"{style}") #set style info
    entry.setFixedSize(size_xy[0], size_xy[1]) #set the size of the text entry
    entry.move(xy[0], xy[1]) #set the position of the text entry
    entry.setAccessibleName(accessible_name) #set the name for accesibility, to be read out by a screenreader
    entry.setAccessibleDescription(accessible_description) #set the description for accesibility, to be read out by a screenreader

    #set its text alginment
    if text_align == 'Centre':
        entry.setAlignment(Qt.AlignCenter)
    elif text_align == 'Right':
        entry.setAlignment(Qt.AlignRight)

    if tool_tip != None:
        entry.setToolTip(tool_tip)

    return entry #return the text entry

def create_drop_down(win, text_align, set_text, style, size_xy, xy, tool_tip=None, accessible_name = "", accessible_description = ""):
    drop_down = QComboBox(win) #init dropdown box
    drop_down.setStyleSheet(f"{style}") #set style info
    drop_down.setFixedSize(size_xy[0], size_xy[1]) #set the size of the dropdown
    drop_down.move(xy[0], xy[1]) #set the position of the dropdown
    drop_down.setAccessibleName(accessible_name) #set the name for accesibility, to be read out by a screenreader
    drop_down.setAccessibleDescription(accessible_description) #set the description for accesibility, to be read out by a screenreader

    #add items from the provided list (assuming `set_text` is a list of items)
    if isinstance(set_text, list):
        drop_down.addItems(set_text)
    else:
        drop_down.addItem(set_text)

    #set text alginment
    if text_align == 'Centre':
        drop_down.setEditable(True)
        drop_down.lineEdit().setAlignment(Qt.AlignCenter)
        drop_down.setEditable(False)
    elif text_align == 'Right':
        drop_down.setEditable(True)
        drop_down.lineEdit().setAlignment(Qt.AlignRight)
        drop_down.setEditable(False)

    if tool_tip != None:
        drop_down.setToolTip(tool_tip)

    return drop_down #return dropdown selection

expected_vr_v6_response = """usage: inference.py [-h] [--gpu GPU] [--pretrained_model PRETRAINED_MODEL] --input INPUT [--sr SR] [--n_fft N_FFT]
                    [--hop_length HOP_LENGTH] [--batchsize BATCHSIZE] [--cropsize CROPSIZE] [--output_image] [--tta]
                    [--output_dir OUTPUT_DIR] [--complex]"""

expected_zf_turbo_response = """usage: inference.py [-h] [--model_type MODEL_TYPE] [--config_path CONFIG_PATH] [--start_check_point START_CHECK_POINT]
                    [--input_folder INPUT_FOLDER] [--store_dir STORE_DIR] [--draw_spectro DRAW_SPECTRO]
                    [--device_ids DEVICE_IDS [DEVICE_IDS ...]] [--extract_instrumental] [--disable_detailed_pbar]
                    [--force_cpu] [--flac_file] [--pcm_type {PCM_16,PCM_24}] [--use_tta]
                    [--lora_checkpoint LORA_CHECKPOINT]"""

def sel_file(win, label, file, folder = False):
    global file_1, file_2, ZF_infer, VR_infer, model_dir, store_dir
    # Open File Dialog
    #check if we're trying to select a folder, not a file
    if folder == True:
        fname = QFileDialog.getExistingDirectory(win, "Open Folder")[0] 
        label.setText(os.path.basename(fname))
        print(fname)
        if file == "store_dir":
            store_dir = fname #set the folder in which results will be stored
        elif file == "model_dir":
            model_dir = fname #set the model folder directory
            svd_set["settings"]["model_dir"] = fname #set the model folder directory in the json file
        else:
            print(file, "is not implemented.") #currently no other folders need to be selected
    else:
        fname = QFileDialog.getOpenFileName(win, "Open File")[0] 
        label.setText(os.path.basename(fname))
        
        #check which file is being selected
        if file == "1":
            file_1 = fname #set the path of input_1
            os.environ["SIMILARITY_EXTRACTOR_FILE_1"] = fname #set the path of input_1 in the environment variable 
        elif file == "2":
            file_2 = fname #set the path of input_2
            os.environ["SIMILARITY_EXTRACTOR_FILE_2"] = fname #set the path of input_2 in the environment variable
        elif file == "ZF_infer":
            #check if it's actually a python script
            if fname.endswith(".py"):
                #if it's a python script, check it's the correct one
                response = os.system(f'python {fname} --help') #run the inference script
                #check if the response is the expected one
                if expected_zf_turbo_response in response:
                    print("ZFTurbo inference script detected.")
                    svd_set["settings"]["ZF_infer"] = fname #set the path for ZFTurbo's inference script
                else:
                    alert =  QMessageBox.critical(None,
                                          f"Error: {fname} is not a valid inference script.",
                                          f"Please select a valid inference script.",
                                          QMessageBox.Ok)
                    print("ZFTurbo inference script detected.")
            else:
                alert =  QMessageBox.critical(None,
                                          f"Error: {fname} is not a valid python script.",
                                          f"Please select a valid inference script.",
                                          QMessageBox.Ok)
                print("ZFTurbo inference script not detected.")
        elif file == "VR_infer":
            #check if it's actually a python script
            if fname.endswith(".py"):
                #if it's a python script, check it's the correct one
                response = os.system(f'python {fname}')
                if expected_vr_v6_response in response:
                    print("VR V6.0.0b4 inference script detected.")
                    svd_set["settings"]["VR_infer"] = fname #set the path for ZFTurbo's inference script
                else:
                    alert =  QMessageBox.critical(None,
                                          f"Error: {fname} is not a valid inference script.",
                                          f"Please select a valid inference script.",
                                          QMessageBox.Ok)
                    print("VR V6.0.0b4 inference script not detected.")
            else:
                alert =  QMessageBox.critical(None,
                                          f"Error: {fname} is not a valid python script.",
                                          f"Please select a valid inference script.",
                                          QMessageBox.Ok)
                print("VR V6.0.0b4 inference script not detected.")
    #regardless of what we are setting, update the settings json file in case they have been updated
    with open('settings.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(svd_set))

def create_image_label(win, text_align, style, size_xy, xy, image_path, tool_tip=None, accessible_name = "", accessible_description = ""):
    #image labels have no text, so we will pass along an empty string for the text.
    image_label = create_label(win, text_align, "", style, size_xy, xy, tool_tip, accessible_name, accessible_description) #create new label
    #load image in a format supported by QT5
    image = QPixmap(image_path)
    #add image to label
    image_label.setPixmap(image)
    return image_label #return the image label