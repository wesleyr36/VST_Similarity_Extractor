import librosa
import os
import numpy as np
from pathlib import Path
import soundfile as sf
import time

def check_audio_file(file_path):
    #check if the file exists
    try:
        if not os.path.isfile(file_path):
            print(f"File {file_path} does not exist.")
            return False
    except Exception as e:
        print(f"File {file_path} does not exist.")
        return False

    #check if the file is a valid audio file
    try:
        librosa.load(file_path, sr=None)
        return True
    except Exception as e:
        print(f"Error loading audio file {file_path}: {e}")
        return False

def check_both_audio_files(file_input_1, file_input_2):
    print("Checking audio files...")
    #issue array
    issues = []
    #check files
    file_1_result = check_audio_file(file_input_1)
    file_2_result = check_audio_file(file_input_2)
    print("File 1 result:", file_1_result)
    print("File 2 result:", file_2_result)
    #check result of file 1
    if file_1_result == False:
        issues.append("File_1")
    #check result of file 2
    if file_2_result == False:
        issues.append("File_2")
    if len(issues) == 0:
        return ["neither"]
    else:
        return issues

def pad_inputs(input_1,input_2):
    try:
        print("input_1:", input_1.shape, "input_2:", input_2.shape)
        
        # Check and transpose input_2 if it's in (length, channels) format
        if input_1.shape[0] == input_2.shape[1] and input_1.shape[0] != input_2.shape[0]:
            input_2 = input_2.T
            print("Transposed input_2 to:", input_2.shape)

        if input_1.shape[0] != 2:
            input_1 = input_1.T
            
        if input_2.shape[0] != 2:
            input_2 = input_2.T
        
        if len(input_1[0]) != len(input_2[0]):
            if len(input_1[0]) > len(input_2[0]):
                input_2 = np.stack([np.pad(input_2[0], (0, len(input_1[0]) - len(input_2[0])), 'constant', constant_values=0),\
                                    np.pad(input_2[1], (0, len(input_1[0]) - len(input_2[0])), 'constant', constant_values=0)], axis=0)
                input_1 = np.stack(input_1, axis=0)
            else:
                input_1 = np.stack([np.pad(input_1[0], (0, len(input_2[0]) - len(input_1[0])), 'constant', constant_values=0),\
                                    np.pad(input_1[1], (0, len(input_2[0]) - len(input_1[0])), 'constant', constant_values=0)], axis=0)
                input_2 = np.stack(input_2, axis=0)
        print("input_1:", input_1.shape, "input_2:", input_2.shape)
        return input_1, input_2
    except Exception as e:
        print("An error occured whilst padding inputs:", e)

def pre_process_audio(file_input_1, file_input_2, start, post_process_mode = False):
    try:
        if post_process_mode == False:
            #load inputs
            input_1, samplerate = librosa.load(file_input_1, 44100, mono=False)
            input_2, samplerate_2 = librosa.load(file_input_2, 44100, mono=False)
        else:
            input_1, input_2, samplerate = file_input_1, file_input_2, 44100

        #convert from mono to stereo if needed
        if input_1.ndim == 1:
            input_1 = np.stack([input_1, input_1], axis=1)
            input_2 = np.stack([input_2, input_2], axis=1)

        #pad array length
        input_1, input_2 = pad_inputs(input_1, input_2)
        inputs_loaded = time.time()

        print(f"Shape of input_1: {input_1.shape}")
        print(f"Shape of input_2: {input_2.shape}")

        #print out how long it took to load the inputs
        print(f"inputs loaded in {inputs_loaded - start}s")

        #split channels
        input_1_L = input_1[0]
        input_1_R = input_1[1]
        input_2_L = input_2[0]
        input_2_R = input_2[1]

        print(f"Shape of input_1_L: {input_1_L.shape}")
        print(f"Shape of input_1_R: {input_1_R.shape}")
        print(f"Shape of input_2_L: {input_2_L.shape}")
        print(f"Shape of input_2_R: {input_2_R.shape}")

        #merge stereo channels
        inputs_L = np.stack([input_1_L, input_2_L], axis=1)
        inputs_R = np.stack([input_1_R, input_2_R], axis=1)
        return input_1, input_2, samplerate, inputs_L, inputs_R, inputs_loaded
    except Exception as e:
        print("An error occured whilst pre-processing audio:",e)

def save_audio_files(similarity_1, similarity_2, input_1_differences, input_2_differences, file_input_1, file_input_2, samplerate, output_name, post_process_mode = False):
    try:
        #get output folder and the names of the input files, the default output folder is the same folder as input_1
        output_folder = os.path.dirname(file_input_1)
        file_1_name = Path(file_input_1).stem # needed for the final output file names if no custom name is selected
        file_2_name = Path(file_input_2).stem # needed for the final output file names if no custom name is selected

        #create output paths
        if output_name is not None:
            outpath_1 = os.path.join(output_folder, output_name) # use custom output name
        else:
            outpath_1 = os.path.join(output_folder, file_1_name) # use original input file names
            outpath_2 = os.path.join(output_folder, file_2_name)

        #save the extracted similarites
        if similarity_1 is not None and not post_process_mode == True:
            #save inital similarities
            sf.write(f"{outpath_1}-similarities.wav", similarity_1.T, samplerate, 'float') # we save as a float32 wav to ensure we do not run into issues with clipping

            #only for AI based methods that may return slightly different similarites for both sources
            if similarity_2 is not None:
                sf.write(f"{outpath_1}-similarities_2(debug).wav", similarity_2.T, samplerate, 'float')
        elif not post_process_mode == True:
            print("Similarity is None, there was an issue during processing.")
            return

        #check to see if the user wanted to save differences, if not they will both be None
        if input_1_differences is not None and input_2_differences is not None:
            if post_process_mode == False:
                if output_name == None:
                    #save the isolated differences with the same filename as inputs
                    sf.write(f"{outpath_1}-differences.wav", input_1_differences.T, samplerate, 'float')
                    sf.write(f"{outpath_2}-differences.wav", input_2_differences.T, samplerate, 'float')
                else:
                    #save the isolated differences with the user-given output name
                    sf.write(f"{outpath_1}-differences_1.wav", input_1_differences.T, samplerate, 'float')
                    sf.write(f"{outpath_1}-differences_2.wav", input_2_differences.T, samplerate, 'float')
            else:
                #save inital similarities
                sf.write(f"{outpath_1}-similarities_post-processed.wav", similarity_1, samplerate, 'float') # we save as a float32 wav to ensure we do not run into issues with clipping

                #only for AI based methods that may return slightly different similarites for both sources
                if similarity_2 is not None:
                    sf.write(f"{outpath_1}-similarities_2_post-processed(debug).wav", similarity_2, samplerate, 'float')
                if output_name == None:
                    #save the isolated differences with the same filename as inputs
                    sf.write(f"{outpath_1}-differences_post-processed.wav", input_1_differences, samplerate, 'float')
                    sf.write(f"{outpath_2}-differences_post-processed.wav", input_2_differences, samplerate, 'float')
                else:
                    #save the isolated differences with the user-given output name
                    sf.write(f"{outpath_1}-differences_1_post-processed.wav", input_1_differences, samplerate, 'float')
                    sf.write(f"{outpath_1}-differences_2_post-processed.wav", input_2_differences, samplerate, 'float')
    except Exception as e:
        print("An error occured whilst saving output files:", e)
