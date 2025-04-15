import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import random as rdm
from libs.similarity_tasks import *
from libs.gui_tools import *
import json
import webbrowser

global file_1, file_2, difference, sim_of_dif, post_process, ZF_infer, VR_infer, model_dir, store_dir, opened_program

svd_set = json.load(open("settings.json"))

file_1, file_2, difference, sim_of_dif, post_process = None, None, False, False, False

opened_program, ZF_infer, VR_infer, model_dir, store_dir = svd_set["opened program"], svd_set["settings"]["ZF_infer"], svd_set["settings"]["VR_infer"], svd_set["settings"]["model_dir"], svd_set["settings"]["store_dir"]
    
def difference_toggle(win, label, differenc):
    global difference
    current_description = label.accessibleDescription() # get the current description
    #differenc will be the current value of the global variable, it is misspelled to differentiate it from the global variable
    if differenc == False:
        label.setText("True") #update the text
        label.setAccessibleDescription(current_description.replace("False", "True")) # update the description
        difference = True
    else:
        label.setText("False")
        label.setAccessibleDescription(current_description.replace("True", "False")) # update the description
        difference = False

def sim_of_dif_toggle(win, label, sim_of_di):
    global sim_of_dif
    current_description = label.accessibleDescription() # get the current description
    #sim_of_di is the value of sim_of_dif when the button was pressed
    #it didn't seem to work without doing it this way
    if sim_of_di == False:
        label.setText("True")
        label.setAccessibleDescription(current_description.replace("False", "True")) # update the description
        sim_of_dif = True
    else:
        label.setText("False")
        label.setAccessibleDescription(current_description.replace("True", "False")) # update the description
        sim_of_dif = False

def post_proc_toggle(win, label, post_proces):
    global post_process
    current_description = label.accessibleDescription() # get the current description
    if post_proces == False:
        label.setText("True")
        label.setAccessibleDescription(current_description.replace("False", "True")) # update the description
        post_process = True
    else:
        label.setText("False")
        label.setAccessibleDescription(current_description.replace("True", "False")) # update the description
        post_process = False


##ToolTips##

#file_tooltips
file_1_tooltip = "This is the first file from the pair of files you wish to extract similarities from, any file including '_1' will be a result relevant to this file."
file_2_tooltip = "This is the second file from the pair of files you wish to extract similarities from, any file including '_2' will be a result relevant to this file."

#difference tooltips
difference_tooltip = 'Export the differences between the two input files? If set to "True" the differences will be exported, if set to "False" they will not be exported.'

#output tooltips
output_filename_tooltip = "This will be the basename for results from the similarity extractor. If set to 'Optional' this output name will be based on the original input files' names.\
                           \nIf you wish to set it to, for example, 'Neo-Aspect' then the resulting filenames would be 'Neo-Aspect_similarites' and 'Neo-Aspect_difference_X' X being either 1 or 2.\
                           \nThis name can be input using the text entry below."

#model tooltips
model_selection_tooltip = "This will be the specific model that the algorithm will use for the similarity extraction process.\
                           \nEach model creates slightly different results so it is recommended to try them all and see which works best for your audio."

focus_tooltip = "This will be the output that is prioritised by the algorithm. If you select 'Similarity' as your focus the resulting similarities will be fuller but may contain more differences.\
                /nIf you select 'Differences' as your focus then you will get fuller sounding difference outputs but they may also contain more similarities."

double_processing_tooltip = "Using double processing will cause the algorithm to run the previous results of the similarity extraction back through the algorithm again for more aggressive isolation.\
                            \nIt will apply double processing based on whichever output you set as your focus, if your focus is 'Similarity' then the second pass will use the differences as an input and vice versa."

#post-processing tooltips
post_processing_tooltip = "Using post processing will help create a fuller similarity and cleaner differences by running the differences through the selected model."

post_processing_model_selection_tooltip = "This selects the model that will be used for post processing, it is recommended to use a different model to the one used in the initial processing stage for the best results."


##Accessibility Names and Descriptons##

#file selection accessibility texts
file_input_selection_1_Name = "Input 1 file selector"
file_input_selection_1_Description = "Click this button to open a file selection dialogue."

file_input_selection_2_Name = "Input 2 file selector"
file_input_selection_2_Description = "Click this button to open a file selection dialogue."

#difference toggle accessibility texts
difference_toggle_Name = "Difference extraction toggle"
difference_toggle_Description = "Click this to toggle whether you wish to export the differences or not, the current state of the toggle is: False." #Will need to be modified when the toggle updates

#filename input accessibility texts
output_filename_Name = "Output filename text input"
output_filename_Description = 'Click on this text entry and type what you wish the filename to be, type "optional" for the default names.'

#model selection accessibility texts
model_dropdown_Name = "Model selection dropdown menu"
model_dropown_Description = "This selects the model the algorithm will use." #Will need to be updated for each tab with the correct items

#model focus selection
model_focus_Name = "Model focus dropdown selection"
model_focus_Description = 'This selects which output is prioritised, by default it is set to "Similarity"' #Do I need any changes?

#double processing toggle accessibility texts
double_proc_toggle_Name = "Double processing toggle"
double_proc_toggle_Description = "Click this to toggle whether you wish to use more aggressive processing. The current state of the toggle is: False." #Will need to be modified when the toggle updates

#post-processing accessibility texts
post_processing_toggle_Name = "Post-processing toggle"
post_processing_toggle_Description = "Click on this to toggle whether you wish to use post-processing or not. The current state of the toggle is: False."

post_processing_model_selection_Name = "Post-processing model dropdown menu"
post_processing_model_selection_Description = "This selects the model that will be used for post-processing." #Will need to be updated with the correct items"

def bertom_based(win):
    #Input Text Labels
    input_1_label = create_label(win, 'Centre', "Input File 1", "color : white; background-color : black", [190, 40], [50, 20])
    input_2_label = create_label(win, 'Centre', "Input File 2", "color : white; background-color : black", [190, 40], [350, 20])

    #Input Path Labels
    input_1_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 70], file_1_tooltip)
    input_2_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 70], file_2_tooltip)

    #Input Selection Buttons
    input_1_sel = create_button(win, "Select Input 1", "color : white; background-color : grey", [190, 40], [50, 120], lambda:sel_file(win, input_1_path, "1"), None, file_input_selection_1_Name, file_input_selection_1_Description)
    input_2_sel = create_button(win, "Select Input 2", "color : white; background-color : grey", [190, 40], [350, 120], lambda:sel_file(win, input_2_path, "2"), None, file_input_selection_2_Name, file_input_selection_2_Description)

    #Differnce and Output Name Text Labels
    difference_label = create_label(win, 'Centre', "Output Differences?", "color : white; background-color : black", [150, 40], [50, 170])
    output_name_label = create_label(win, 'Centre', "Output File Name", "color : white; background-color : black", [150, 40], [390, 170])
    
    #Difference and Name Fields
    difference_button = create_button(win, "False", "color : white; background-color : grey", [150, 40], [50, 220], lambda:difference_toggle(win, difference_button, difference), difference_tooltip, difference_toggle_Name, difference_toggle_Description)
    output_name_input = create_text_entry(win, 'Centre', "Optional", "color : white; background-color : grey", [150, 40], [390, 220], output_filename_tooltip, output_filename_Name, output_filename_Description)

    #Output Folder fields
    output_folder_path = create_label(win, 'Left', "Ouput Folder", "color : white; background-color : black", [150, 40], [250, 170])
    output_folder_input = create_button(win, "Select Output Folder", "color : white; background-color : grey", [150, 40], [220, 220], lambda:sel_file(win, output_folder_path, "store_dir", True))

    #Similarity of Differences
    sim_of_dif_label = create_label(win, 'Centre', "Output Similarity of inverted Differences?\n(some similarities can be phase inverted)", "color : white; background-color : black", [290, 40], [152, 270])
    sim_of_dif_button = create_button(win, "False", "color : white; background-color : grey", [190, 40], [203, 320], lambda:sim_of_dif_toggle(win, sim_of_dif_button, sim_of_dif))
    
    #Post-Processing
    post_proc_label = create_label(win, 'Centre', "Apply Post-Processing?", "color : white; background-color : black", [190, 40], [202, 420])
    post_proc_togle = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 470], lambda:post_proc_toggle(win, post_proc_togle, post_process), post_processing_tooltip, post_processing_toggle_Name, post_processing_toggle_Description)
    post_proc_dmenu = create_drop_down(win, 'Centre', ["VR V6.0.0b4 - 2K FFT", "VR V6.0.0b4 - 4K FFT","MDX23C - 2K FFT", "MDX23C - 8K FFT"], "color : white; background-color : grey", [190, 40], [350, 470],post_processing_model_selection_tooltip ,post_processing_model_selection_Name, post_processing_model_selection_Description)
    
    #Run Similarity Extraction Button
    similarity_button = create_button(win, "Extract Similarity", "color : white; background-color : grey", [490, 40], [50, 370], lambda:run_similarity_extractor("bertom", os.getenv("SIMILARITY_EXTRACTOR_FILE_1"),
                                                                                                                                                                 os.getenv("SIMILARITY_EXTRACTOR_FILE_2"), difference, output_name_input.text(),
                                                                                                                                                                 sim_of_dif, post_process, post_proc_dmenu.currentText(),
                                                                                                                                                                 json.load(open("settings.json"))))

def mdx23c_based(win):
    #Input Text Labels
    input_1_label = create_label(win, 'Centre', "Input File 1", "color : white; background-color : black", [190, 40], [50, 20])
    input_2_label = create_label(win, 'Centre', "Input File 2", "color : white; background-color : black", [190, 40], [350, 20])

    #Input Path Labels
    input_1_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 70], file_1_tooltip)
    input_2_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 70], file_2_tooltip)

    #Input Selection Buttons
    input_1_sel = create_button(win, "Select Input 1", "color : white; background-color : grey", [190, 40], [50, 120], lambda:sel_file(win, input_1_path, "1"), None, file_input_selection_1_Name, file_input_selection_1_Description)
    input_2_sel = create_button(win, "Select Input 2", "color : white; background-color : grey", [190, 40], [350, 120], lambda:sel_file(win, input_2_path, "2"), None, file_input_selection_2_Name, file_input_selection_2_Description)

    #Differnce and Output Name Text Labels
    difference_label = create_label(win, 'Centre', "Output Differences?", "color : white; background-color : black", [150, 40], [50, 170])
    output_name_label = create_label(win, 'Centre', "Output File Name", "color : white; background-color : black", [150, 40], [390, 170])
    
    #Difference and Name Fields
    difference_button = create_button(win, "False", "color : white; background-color : grey", [150, 40], [50, 220], lambda:difference_toggle(win, difference_button, difference), difference_tooltip, difference_toggle_Name, difference_toggle_Description)
    output_name_input = create_text_entry(win, 'Centre', "Optional", "color : white; background-color : grey", [150, 40], [390, 220], output_filename_tooltip, output_filename_Name, output_filename_Description)

    #Output Folder fields
    output_folder_path = create_label(win, 'Left', "Ouput Folder", "color : white; background-color : black", [150, 40], [250, 170])
    output_folder_input = create_button(win, "Select Output Folder", "color : white; background-color : grey", [150, 40], [220, 220], lambda:sel_file(win, output_folder_path, "store_dir", True))

    #Model Selection:
    model_sel_label = create_label(win, 'Centre', "Which model?", "color : white; background-color : black", [190, 40], [202, 270])
    model_sel_dmenu = create_drop_down(win, 'Centre', ["MDX23C - 2K FFT", "MDX23C - 8K FFT"], "color : white; background-color : grey", [190, 40], [202, 320], model_selection_tooltip, model_dropdown_Name, model_dropown_Description)
    
    #Post-Processing
    post_proc_label = create_label(win, 'Centre', "Apply Post-Processing?", "color : white; background-color : black", [190, 40], [202, 420])
    post_proc_togle = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 470], lambda:post_proc_toggle(win, post_proc_togle, post_process), post_processing_tooltip, post_processing_toggle_Name, post_processing_toggle_Description)
    post_proc_dmenu = create_drop_down(win, 'Centre', ["VR V6.0.0b4 - 2K FFT", "VR V6.0.0b4 - 4K FFT","MDX23C - 2K FFT", "MDX23C - 8K FFT"], "color : white; background-color : grey", [190, 40], [350, 470], post_processing_model_selection_tooltip, post_processing_model_selection_Name, post_processing_model_selection_Description)
    
    #Run Similarity Extraction Button
    similarity_button = create_button(win, "Extract Similarity", "color : white; background-color : grey", [490, 40], [50, 370], lambda:run_similarity_extractor(model_sel_dmenu.currentText(), os.getenv("SIMILARITY_EXTRACTOR_FILE_1"),
                                                                                                                                                                 os.getenv("SIMILARITY_EXTRACTOR_FILE_2"), difference, output_name_input.text(),
                                                                                                                                                                 False, post_process, post_proc_dmenu.currentText(),json.load(open("settings.json"))))

def vr_v6b4_based(win):
    #Input Text Labels
    input_1_label = create_label(win, 'Centre', "Input File 1", "color : white; background-color : black", [190, 40], [50, 20])
    input_2_label = create_label(win, 'Centre', "Input File 2", "color : white; background-color : black", [190, 40], [350, 20])

    #Input Path Labels
    input_1_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 70], file_1_tooltip)
    input_2_path = create_label(win, 'Left', "", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 70], file_2_tooltip)

    #Input Selection Buttons
    input_1_sel = create_button(win, "Select Input 1", "color : white; background-color : grey", [190, 40], [50, 120], lambda:sel_file(win, input_1_path, "1"), None, file_input_selection_1_Name, file_input_selection_1_Description)
    input_2_sel = create_button(win, "Select Input 2", "color : white; background-color : grey", [190, 40], [350, 120], lambda:sel_file(win, input_2_path, "2"), None, file_input_selection_2_Name, file_input_selection_2_Description)

    #Differnce and Output Name Text Labels
    difference_label = create_label(win, 'Centre', "Output Differences?", "color : white; background-color : black", [150, 40], [50, 170])
    output_name_label = create_label(win, 'Centre', "Output File Name", "color : white; background-color : black", [150, 40], [390, 170])
    
    #Difference and Name Fields
    difference_button = create_button(win, "False", "color : white; background-color : grey", [150, 40], [50, 220], lambda:difference_toggle(win, difference_button, difference), difference_tooltip, difference_toggle_Name, difference_toggle_Description)
    output_name_input = create_text_entry(win, 'Centre', "Optional", "color : white; background-color : grey", [150, 40], [390, 220], output_filename_tooltip, output_filename_Name, output_filename_Description)

    #Output Folder fields
    output_folder_path = create_label(win, 'Left', "Ouput Folder", "color : white; background-color : black", [150, 40], [249, 170])
    output_folder_input = create_button(win, "Select Output Folder", "color : white; background-color : grey", [150, 40], [220, 220], lambda:sel_file(win, output_folder_path, "store_dir", True))

    #Model Selection
    model_sel_label = create_label(win, 'Centre', "Which model?", "color : white; background-color : black", [190, 40], [35, 270])
    model_sel_dmenu = create_drop_down(win, 'Centre', ["VR V6.0.0b4 - 2K FFT", "VR V6.0.0b4 - 4K FFT"], "color : white; background-color : grey", [150, 40], [50, 320], model_selection_tooltip, model_dropdown_Name, model_dropown_Description)

    #Processing focus
    focus_label = create_label(win, 'Centre', "Model focus:", "color : white; background-color : black", [231, 40], [180, 270])
    focus_dmenu = create_drop_down(win, 'Centre', ["Similarity", "Differences"], "color : white; background-color : grey", [150, 40], [220, 320], focus_tooltip, model_focus_Name, model_focus_Description)

    #Double Processing - reusing sim_of_dif since it's not too dissimilar
    double_proc_label = create_label(win, 'Centre', "Use double Processing?", "color : white; background-color : black", [234, 40], [350, 270])
    double_proc_togle = create_button(win, "False", "color : white; background-color : grey", [150, 40], [390, 320], lambda:sim_of_dif_toggle(win, double_proc_togle, sim_of_dif), double_processing_tooltip, double_proc_toggle_Name, double_proc_toggle_Description)
    
    #Post-Processing
    post_proc_label = create_label(win, 'Centre', "Apply Post-Processing?", "color : white; background-color : black", [190, 40], [202, 420])
    post_proc_togle = create_button(win, "False", "color : white; background-color : grey", [190, 40], [50, 470], lambda:post_proc_toggle(win, post_proc_togle, post_process), post_processing_tooltip, post_processing_toggle_Name, post_processing_toggle_Description)
    post_proc_dmenu = create_drop_down(win, 'Centre', ["VR V6.0.0b4 - 2K FFT", "VR V6.0.0b4 - 4K FFT","MDX23C - 2K FFT", "MDX23C - 8K FFT"], "color : white; background-color : grey", [190, 40], [350, 470], post_processing_model_selection_tooltip, post_processing_model_selection_Name, post_processing_model_selection_Description)
    
    #Run Similarity Extraction Button
    similarity_button = create_button(win, "Extract Similarity", "color : white; background-color : grey", [490, 40], [50, 370], lambda:run_similarity_extractor(model_sel_dmenu.currentText(), os.getenv("SIMILARITY_EXTRACTOR_FILE_1"),
                                                                                                                                                                 os.getenv("SIMILARITY_EXTRACTOR_FILE_2"), difference, output_name_input.text(),
                                                                                                                                                                 sim_of_dif, post_process, post_proc_dmenu.currentText(),
                                                                                                                                                                 json.load(open("settings.json")), focus_dmenu.currentText(), 
                                                                                                                                                                 output_folder_path.text()))

def settings_func(win):
    #Settings Labels
    ZF_infer_label = create_label(win, 'Centre', "ZFTurbo Inference\nScript Path", "color : white; background-color : black", [190, 40], [50, 20])
    VR_infer_label = create_label(win, 'Centre', "VR v6.0.0b4 Inference\nScript Path", "color : white; background-color : black", [190, 40], [350, 20])
    model_dir_label = create_label(win, 'Centre', "Model Folder", "color : white; background-color : black", [190, 40], [50, 170])

    #Settings Path Label
    ZF_infer_path = create_label(win, 'Left', f"{ZF_infer}", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 70])
    VR_infer_path = create_label(win, 'Left', f"{VR_infer}", "color : white; border : 1px solid white; background-color : black", [190, 40], [350, 70])
    model_dir_path = create_label(win, 'Left', f"{model_dir}", "color : white; border : 1px solid white; background-color : black", [190, 40], [50, 220])

    #Input Selection Buttons
    ZF_infer_sel = create_button(win, "Select Inference Script", "color : white; background-color : grey", [190, 40], [50, 120], lambda:sel_file(win, ZF_infer_path, "ZF_infer", False))
    VR_infer_sel = create_button(win, "Select Inference Script", "color : white; background-color : grey", [190, 40], [350, 120], lambda:sel_file(win, VR_infer_path, "VR_infer", False))
    model_dir_sel = create_button(win, "Select Models Directory", "color : white; background-color : grey", [190, 40], [50, 270], lambda:sel_file(win, model_dir_path, "model_dir", True))

    #User Guide Button
    user_guide_label = create_label(win, 'Centre', "User Guide", "color : white; background-color : black", [190, 40], [350, 170])
    user_guide = create_button(win, "Open User Guide", "color : white; background-color : grey", [190, 40], [350, 270], lambda: webbrowser.open("Help_Guide.html"), None)

def window():
    app = QApplication(sys.argv) #create app
    win = QDialog() #init window
    win.setStyleSheet("background-color : black") #set style
    win.layout = QVBoxLayout(win) #set layout
    global opened_program
    #Check if the user has opened the program before, if not, show them the user guide
    if opened_program == 0:
        done = QMessageBox.information(None,
                "Welcome to the Similarity Extractor",
                "Hit yes to open the user guide, or no to continue without it. \n\nShould you wish to open the user guide in the future, you can do so from the settings tab.",
                QMessageBox.Yes | QMessageBox.No)
        
        if done == QMessageBox.Yes:
            #open the user guide in the default web browser
            webbrowser.open("Help Guide.html")
        
        #update the opened program variable to 1, so we don't open the user guide again
        opened_program = 1 
        #update the settings file to reflect this
        svd_set["opened program"] = opened_program
        with open('settings.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(svd_set))



    #Extraction yype label
    extraction_lab = create_label(win, 'Extraction Type', "Extraction Type:", "color : white; background-color : black", [190, 40], [15, -12])

    #Initialize tab screen with stylesheet to match the rest of the GUI
    tabs = QTabWidget()
    tabs.setStyleSheet("""
    QTabBar::tab {
        height: 20px;  /* Sets the height of each tab heading */
        padding: 2px;  /* Add padding */
        color : white;
        border : 1px solid grey;
    }
    QTabBar::tab::selected {
        color : white;
        background-color: grey;
        border : 1px solid white;
    }
    QToolTip {
        background-color: black;
        color: white;
        border: 1px solid white;
    }                   
    """)

    #init the tab for the bertom phantom centre based extractor
    bertom_tab = QWidget()
    bertom_tab.layout = QVBoxLayout(win)
    tabs.addTab(bertom_tab, "Bertom Phantom Centre")

    #init the tab for the mdx23c based extractor --placeholder
    mdx23c_tab = QWidget()
    mdx23c_tab.layout = QVBoxLayout(win)
    tabs.addTab(mdx23c_tab, "AI arch - MDX23C")

    #init the vrv6 based extraction tab --placeholder
    vrv6_tab = QWidget()
    vrv6_tab.layout = QVBoxLayout(win)
    tabs.addTab(vrv6_tab, "AI arch - VR V6.0.0b4")

    #init settings tab --placeholder
    settings = QWidget()
    settings.layout = QVBoxLayout(win)
    tabs.addTab(settings, "⚙Options⚙")

    #add the bertom tab's contents
    bertom = bertom_based(bertom_tab) #todo
    bertom_tab.layout.addWidget(bertom)
    bertom_tab.setLayout(bertom_tab.layout)

    #add the contents of the mdx23c tab
    mdx23c = mdx23c_based(mdx23c_tab)
    mdx23c_tab.layout.addWidget(mdx23c)
    mdx23c_tab.setLayout(mdx23c_tab.layout)

    #add the contents of the VR v6.0.0b4 tab
    vrv6 = vr_v6b4_based(vrv6_tab)
    vrv6_tab.layout.addWidget(vrv6)
    vrv6_tab.setLayout(vrv6_tab.layout)

    #add the contents of the settings tab
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
