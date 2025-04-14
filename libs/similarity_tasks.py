import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import numpy as np
from pathlib import Path
import soundfile as sf
import time
import random as rdm
import librosa
import json
from pedalboard import load_plugin
import io
from pedalboard.io import AudioFile
from .audio_tools import *

plugin_name = r"Bertom_PhantomCenter.vst3"

def bertom_similarity(inputs_L, inputs_R, samplerate, model_dir):
    try:
        #convert the pre-processed L and R channel stacks into file-like objects - needed for pedalboard
        inputs_L_wav_buffer = io.BytesIO(AudioFile.encode(inputs_L, samplerate, "wav", 2, 32))
        inputs_R_wav_buffer = io.BytesIO(AudioFile.encode(inputs_R, samplerate, "wav", 2, 32))

        #centre isolation - mix = the amount of centre to output, 100 means only include the centre
        plugin = load_plugin(f"{model_dir}/{plugin_name}", parameter_values = {'hpf': 'Off', 'lpf': 'Off', 'mix': 100, 'output': 0.0, 'bypass': 'Normal'})
        assert plugin.is_effect

        #separate similarities, i.e. centre, of the Left channels
        with AudioFile(inputs_L_wav_buffer) as f:
            similarity_L = plugin(f.read(f.frames), samplerate)

        #separate similarities of the Right channels
        with AudioFile(inputs_R_wav_buffer) as f:
            similarity_R = plugin(f.read(f.frames), samplerate)

        #merge the similarity together, for this method the similarity for input_1 and input_2 are the exact same, this isn't true for later methods.
        similarity = np.stack([similarity_L[0], similarity_R[0]], axis=1)
        similarity_2 = None
        return similarity.T, similarity_2
    except Exception as e:
        print("Error in the Bertom Phantom Center similarity extraction algorithm:", e)

def vrv6_similarity(inputs_L, inputs_R, samplerate, focus, double, VR_infer, model_dir, model):
    try:
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"temp")
        temp_path = os.path.join(temp_dir,"temp")
        print(temp_dir)

        print(inputs_L.shape,inputs_R.shape)

        os.makedirs(temp_dir, exist_ok=True)
        try:
            sf.write(f"{temp_dir}/temp_L.wav", inputs_L, samplerate, 'float')
            sf.write(f"{temp_dir}/temp_R.wav", inputs_R, samplerate, 'float')
        except Exception as e:
            print(f"Error writing file: {e}")

        print("why")

        #centre isolation
        #separate similarities

        if "4K" in model:
            n_fft = 4096
            hop_length = 2048
            crop_size = 512
            batch_size = 1
        else:
            n_fft = 2048
            hop_length = 1024
            crop_size = 256
            batch_size = 4

        #run model, should probably implement directly, as I can then use my mixed precision version
        os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_L.wav" -f {n_fft} -H {hop_length} -c {crop_size} -B {batch_size} -P "{model_dir}/{model}.pth" -X -o "{temp_dir}" --gpu 0')
        os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_R.wav" -f {n_fft} -H {hop_length} -c {crop_size} -B {batch_size} -P "{model_dir}/{model}.pth" -X -o "{temp_dir}" --gpu 0')
        print("os calls")
        if focus == "Similarity":
            similarity_L, _ = librosa.load(f"{temp_dir}/temp_L_Vocals.wav", 44100, mono=False)
            similarity_R, _ = librosa.load(f"{temp_dir}/temp_R_Vocals.wav", 44100, mono=False)
            duration_L = librosa.get_duration(filename=f"{temp_dir}/temp_L_Vocals.wav")
            duration_R = librosa.get_duration(filename=f"{temp_dir}/temp_R_Vocals.wav")
            if double == True:
                os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_L_Instruments.wav" -f {n_fft} -H {hop_length} -c {crop_size} -B {batch_size} -P "{model_dir}/{model}.pth" -X -o "{temp_dir}" --gpu 0')
                os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_R_Instruments.wav" -f {n_fft} -H {hop_length} -c {crop_size} -B {batch_size} -P "{model_dir}/{model}.pth" -X -o "{temp_dir}" --gpu 0')
                similarity_L_db, _ = librosa.load(f"{temp_dir}/temp_L_Instruments_Vocals.wav", 44100, mono=False)
                similarity_R_db, _ = librosa.load(f"{temp_dir}/temp_R_Instruments_Vocals.wav", 44100, mono=False)
                
                similarity_L = similarity_L + similarity_L_db
                similarity_R = similarity_R + similarity_R_db

            #pad_similarities
            similarity_L, inputs_L = pad_inputs(similarity_L, inputs_L)
            similarity_R, inputs_R = pad_inputs(similarity_R, inputs_R)

        else:
            differences_L, _ = librosa.load(f"{temp_dir}/temp_L_Instruments.wav", 44100, mono=False)
            differences_R, _ = librosa.load(f"{temp_dir}/temp_R_Instruments.wav", 44100, mono=False)
            if double == True:
                os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_L_Vocals.wav" -f {n_fft} -H {hop_length} -c {crop_size} -B {batch_size} -P "{model_dir}/{model}.pth" -X -o "{temp_dir}" --gpu 0')
                os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_R_Vocals.wav" -f {n_fft} -H {hop_length} -c {crop_size} -B {batch_size} -P "{model_dir}/{model}.pth" -X -o "{temp_dir}" --gpu 0')
                differences_dp_L, _ = librosa.load(f"{temp_dir}/temp_L_Vocals_Instruments.wav", 44100, mono=False)
                differences_dp_R, _ = librosa.load(f"{temp_dir}/temp_R_Vocals_Instruments.wav", 44100, mono=False)

                print(differences_L.shape, differences_dp_L.shape, inputs_L.shape)
                
                #combine double processed differences and pad the length to ensure it matches the initial inputs
                differences_dp_L, inputs_L = pad_inputs((differences_L + differences_dp_L), inputs_L)
                differences_dp_R, inputs_R = pad_inputs((differences_R + differences_dp_R), inputs_R)

                print(differences_dp_L.shape, differences_dp_R.shape)
                
                similarity_L = inputs_L - differences_dp_L
                similarity_R = inputs_R - differences_dp_R
            else:
                differences_L, inputs_L = pad_inputs(differences_L, inputs_L)
                differences_R, inputs_R = pad_inputs(differences_R, inputs_R)
                
                similarity_L = inputs_L - differences_L
                similarity_R = inputs_R - differences_R

        #pad_similarities
        similarity_L, inputs_L = pad_inputs(similarity_L, inputs_L)
        similarity_R, inputs_R = pad_inputs(similarity_R, inputs_R)

        #finalise similarities - the AI models may have different similarities
        similarity_1 = np.stack([similarity_L[0], similarity_R[0]], axis=0)
        similarity_2 = np.stack([similarity_L[1], similarity_R[1]], axis=0)

        #remove temp files
        os.remove(f"{temp_dir}/temp_L.wav")
        os.remove(f"{temp_dir}/temp_R.wav")
        if double == True:
            if focus == "Similarity":
                os.remove(f"{temp_dir}/temp_L_Instruments_Vocals.wav")
                os.remove(f"{temp_dir}/temp_R_Instruments_Vocals.wav")
                os.remove(f"{temp_dir}/temp_L_Instruments_Instruments.wav")
                os.remove(f"{temp_dir}/temp_R_Instruments_Instruments.wav")
            else:
                os.remove(f"{temp_dir}/temp_L_Vocals_Vocals.wav")
                os.remove(f"{temp_dir}/temp_R_Vocals_Vocals.wav")
                os.remove(f"{temp_dir}/temp_L_Vocals_Instruments.wav")
                os.remove(f"{temp_dir}/temp_R_Vocals_Instruments.wav")
        os.remove(f"{temp_dir}/temp_L_Vocals.wav")
        os.remove(f"{temp_dir}/temp_R_Vocals.wav")
        os.remove(f"{temp_dir}/temp_L_Instruments.wav")
        os.remove(f"{temp_dir}/temp_R_Instruments.wav")
        return similarity_1, similarity_2
    except Exception as e:
        print("Error in the VR V6.0.0b4 similarity extraction algorithm:", e)

def mdx23c_similarity(inputs_L, inputs_R, samplerate, ZF_infer, model_dir, model):
    try:
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"temp")
        sf.write(f"{temp_dir}/temp_L.wav", inputs_L, samplerate, 'float')
        sf.write(f"{temp_dir}/temp_R.wav", inputs_R, samplerate, 'float')

        #centre isolation
        os.system(f'python "{ZF_infer}" --input_folder "{temp_dir}" --config_path "{model_dir}/{model}.yaml" --start_check_point "{model_dir}/{model}.ckpt" --store_dir "{temp_dir}"')

        similarity_L, _ = librosa.load(f"{temp_dir}/temp_L/similarity.wav", 44100, mono=False)
        similarity_R, _ = librosa.load(f"{temp_dir}/temp_R/similarity.wav", 44100, mono=False)

        #remove temp files
        os.remove(f"{temp_dir}/temp_L.wav")
        os.remove(f"{temp_dir}/temp_R.wav")
        os.remove(f"{temp_dir}/temp_L/similarity.wav")
        os.remove(f"{temp_dir}/temp_R/similarity.wav")

        #finalise similarities - the AI models may have different similarities
        similarity_1 = np.stack([similarity_L[0], similarity_R[0]], axis=0)
        similarity_2 = np.stack([similarity_L[1], similarity_R[1]], axis=0)

        return similarity_1, similarity_2
    except Exception as e:
        print("Error in the MDX23C similarity extraction algorithm:", e)

def similarity_extractor(model, file_input_1, file_input_2, difference, output_name, double, VR_infer, ZF_infer, model_dir, focus, output_folder):
    try:
        start = time.time()
        #load inputs, get samplerate, pre-process audio and get the time it took to load the audio
        input_1, input_2, samplerate, inputs_L, inputs_R, inputs_loaded = pre_process_audio(file_input_1, file_input_2, start)

        #run correct process based on the selected model
        if model == "bertom":
            similarity, similarity_2 = bertom_similarity(inputs_L, inputs_R, samplerate, model_dir)
        elif "V6.0.0b4" in model:
            similarity, similarity_2 = vrv6_similarity(inputs_L, inputs_R, samplerate, focus, double, VR_infer, model_dir, model)
        elif any(model_type in model for model_type in ["MDX23C"]):
            #ZFTurbo's code is very universal, it supports quite a few models, so we can use this function for them in the future
            similarity, similarity_2 = mdx23c_similarity(inputs_L, inputs_R, samplerate, ZF_infer, model_dir, model)
        else:
            print("Error:", model, "is either not implemented or an error has occured.")
            return
        #output similarity shape as a debug check
        print(f"Shape of similarity: {similarity.shape}")

        #subtract the similarites from the inputs to get the differences, set them to None if the user doesn't want them
        if difference == True:
            difference_1 = input_1 - similarity

            #you get cleaner results if using the second similarity for input_2 on algorithms that use it
            if model == "bertom":
                difference_2 = input_2 - similarity
            else:
                difference_2 = input_2 - similarity_2

            #print shapes as a debug check
            print(f"Shape of difference_1: {difference_1.shape}")
            print(f"Shape of difference_2: {difference_2.shape}")
        else:
            difference_1 = None
            difference_2 = None

        #save the extracted similarites and differences, similarity_2 is passed as None as this method doesn't require it
        save_audio_files(similarity, similarity_2, difference_1, difference_2, file_input_1, file_input_2, samplerate, output_name, False, output_folder)

        #output the time it took to finish processing
        finished = time.time()
        print(f"Processing complete after: {finished - inputs_loaded}s \n Total time: {finished - start}s")

        #pass on differences for optional post-processing
        return difference_1, difference_2
    except Exception as e:
        print("Exception during similarity extraction:", e)

def run_similarity_extractor(model, input_1, input_2, difference, output_name, sim_of_dif, post_process, post_process_model,svd_set,focus="Similarity",output_folder=None):
    try:
        ZF_infer, VR_infer, model_dir, store_dir = svd_set["settings"]["ZF_infer"], svd_set["settings"]["VR_infer"], svd_set["settings"]["model_dir"], svd_set["settings"]["store_dir"]
        print(model_dir)
        print(input_1, input_2, difference, output_name, sim_of_dif)
        print("model:",model, "\n input_1:", input_1, "\n input_2:", input_2, "\n difference:",difference, "\n out_name:", output_name, "\n double:", sim_of_dif)
        print("pressed")

        #check to see if the user has probvided valid inputs, if not show an error message
        valid_results = check_both_audio_files(input_1, input_2)

        response = ""
        valid = False
        #check the results and compile the error message
        for i in valid_results:
            if i == "neither":
                valid = True
                break
            elif response == "":
                response = i
            else:
                response += f" and {i}"

        if valid:
            try:
                if output_name.lower() == "optional":
                    output_name = None
                if output_folder.lower() == "output folder":
                    output_folder = None
                if post_process == True:
                    difference_1, difference_2 = similarity_extractor(model, input_1, input_2, difference, output_name, sim_of_dif, VR_infer, ZF_infer, model_dir,focus, output_folder)

                    #convert differences back to axis = 0 -- I hate that this is needed, I can only imagine how inefficient this is
                    difference_1 = np.stack(difference_1, axis=0)
                    difference_2 = np.stack(difference_2, axis=0)

                    #load original files with post-process mode off and return only the audio data
                    inp_1, inp_2, samplerate, _, _, _ = pre_process_audio(input_1, input_2, time.time(), False)

                    #process the differences with post-process mode on and return on the pre-processed audio
                    _, _, _, differences_L, differences_R, _ = pre_process_audio(difference_1, difference_2, time.time(), True)

                    #run correct process based on the selected post processing model
                    if "V6.0.0b4" in post_process_model:
                        similarity_addition, similarity_2_addition = vrv6_similarity(differences_L, differences_R, samplerate, focus, sim_of_dif, VR_infer, model_dir, post_process_model)
                    elif "MDX23C" in post_process_model:
                        similarity_addition, similarity_2_addition = mdx23c_similarity(differences_L, differences_R, samplerate, ZF_infer, model_dir, post_process_model)
                    else:
                        print("Error:", post_process_model, "is either not implemented or an error has occured.")
                        return

                    #apply the data extracted during post-processing and stack along the correct axis for soudfile
                    difference_1_pp = np.stack(difference_1 - similarity_addition, axis=1)
                    difference_2_pp = np.stack(difference_2 - similarity_2_addition, axis=1)
                    similarity_1_pp = np.stack(inp_1, axis=1) - difference_1_pp
                    similarity_2_pp = np.stack(inp_2, axis=1) - difference_2_pp
                    #debug
                    print("dif_pp_1:", difference_1_pp.shape, "dif_pp_2:", difference_2_pp.shape)
                    print("sim_pp_1:", similarity_1_pp.shape, "sim_pp_2:", similarity_2_pp.shape)

                    #save post_processed files
                    save_audio_files(similarity_1_pp, similarity_2_pp, difference_1_pp, difference_2_pp, input_1, input_2, samplerate, output_name, True, output_folder)
                else:
                    #run similarity extraction with no post-processing afterwards
                    similarity_extractor(model, input_1, input_2, difference, output_name, sim_of_dif, VR_infer, ZF_infer, model_dir, focus, output_folder)

                done = QMessageBox.information(None,
                                          "Processing Finished",
                                          "Your files have been processed, please check the folder containing input 1.",
                                          QMessageBox.Ok)
                if done == QMessageBox.Ok:
                    return
                print("pass")
            except Exception as e:
                print(e)
        else:
            validation_fail = QMessageBox.critical(None,
                                          f"Error: when loading {response}.",
                                          f"Please make sure you have selected valid audio files!",
                                          QMessageBox.Retry | QMessageBox.Cancel)
            if validation_fail == QMessageBox.Retry:
                return
            else:
                print("Cancel")
                exit()
    except Exception as e:
                print(e)
    print("rip")
