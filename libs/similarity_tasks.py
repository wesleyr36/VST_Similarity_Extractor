import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import numpy as np
import os
from pathlib import Path
import soundfile as sf
import time
import random as rdm
import librosa
import json
from pedalboard import load_plugin
import io
from pedalboard.io import AudioFile

def run_similarity_extractor(model, input_1, input_2, difference, output_name, sim_of_dif, post_process, post_process_model):
    try:
        svd_set = json.load(open("settings.json"))
        ZF_infer, VR_infer, model_dir, store_dir = svd_set["settings"]["ZF_infer"], svd_set["settings"]["VR_infer"], svd_set["settings"]["model_dir"], svd_set["settings"]["store_dir"]
        print(model_dir)
        print(input_1, input_2, difference, output_name, sim_of_dif)
        print("model:",model, "\n input_1:", input_1, "\n input_2:", input_2, "\n difference:",difference, "\n out_name:", output_name, "\n double:", sim_of_dif)
        print("pressed")
        if not None in [input_1, input_2]:
            try:
                if post_process == True:
                    output_folder = os.path.dirname(input_1)
                    file_1_name = Path(input_1).stem
                    file_2_name = Path(input_2).stem
                    
                    #output paths
                    if output_name is not None:
                        outpath_1 = os.path.join(output_folder, output_name)
                    else:
                        outpath_1 = os.path.join(output_folder, file_1_name)
                        outpath_2 = os.path.join(output_folder, file_2_name)
                    
                    if "V6.0.0b4" in model:
                        difference_1, difference_2 = run_vrv6_similarity_extractor(model, input_1, input_2, difference, output_name, sim_of_dif, VR_infer, model_dir,pp_mode=True)
                    elif "MDX23C" in model:
                        difference_1, difference_2 = run_mdx23c_similarity_extractor(model, input_1, input_2, difference, output_name, ZF_infer, model_dir,pp_mode=True)
                    else:
                        if output_name.lower() != "optional":
                            difference_1, difference_2 = similarity_extractor(input_1, input_2, difference, output_name, sim_of_dif)
                        else:
                            difference_1, difference_2 = similarity_extractor(input_1, input_2, difference, None, sim_of_dif)

                    inp_1, samplerate = librosa.load(input_1, 44100, mono=False)
                    inp_2, _ = librosa.load(input_2, 44100, mono=False)
                    #post_process
                    if "V6.0.0b4" in post_process_model:
                        print(model, input_1, input_2, difference, output_name, VR_infer, model_dir,pp_mode=True)
                        difference_1_pp, difference_2_pp = run_vrv6_similarity_extractor(model, input_1, input_2, difference, output_name, VR_infer, model_dir,pp_mode=True)
                    elif "MDX23C" in post_process_model:
                        difference_1_pp, difference_2_pp = mdx23c_post_process(model, difference_1, difference_2, difference, output_name, ZF_infer, model_dir,pp_mode=True)
                    else:
                        print("How did we get here?")

                    #save post_processed files
                    if difference == True and output_name is None:
                        #output differences
                        sf.write(f"{outpath_1}-differences-Post_Processed.wav", difference_1_pp, samplerate, 'float')            
                        sf.write(f"{outpath_2}-differences-Post_Processed.wav", difference_2_pp, samplerate, 'float')
                        sf.write(f"{outpath_2}-similarities-Post_Processed (debug).wav", np.stack(inp_2, axis=1)-difference_2_pp, samplerate, 'float')
                    elif difference == True and output_name is not None:
                        sf.write(f"{outpath_1}-differences_1-Post_Processed.wav", difference_1_pp, samplerate, 'float')            
                        sf.write(f"{outpath_1}-differences_-Post_Processed2.wav", difference_2_pp, samplerate, 'float')
                        sf.write(f"{outpath_1}-similarities_2-Post_Processed (debug).wav", np.stack(inp_2, axis=1)-difference_2_pp, samplerate, 'float')
                    #output similarities
                    sf.write(f"{outpath_1}-similarities-Post_Processed.wav", np.stack(inp_1, axis=1)-difference_1_pp, samplerate, 'float')
                else:
                    if "V6.0.0b4" in model:
                        run_vrv6_similarity_extractor(model, input_1, input_2, difference, output_name, sim_of_dif, VR_infer, model_dir,pp_mode=False)
                    elif "MDX23C" in model:
                        run_mdx23c_similarity_extractor(model, input_1, input_2, difference, output_name, ZF_infer, model_dir,pp_mode=False)
                    else:
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
                print("pass")
            except Exception as e:
                print(e)
    except Exception as e:
                print(e)
    print("rip")


def run_mdx23c_similarity_extractor(model, input_1, input_2, difference, output_name, ZF_infer, model_dir,pp_mode):
    print("model:",model, "\n input_1:", input_1, "\n input_2:", input_2, "\n difference:",difference, "\n out_name:", output_name, "\n ZF infer:", ZF_infer, "\n model_dir:", model_dir)
    if not None in [input_1, input_2]:
        try:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            if output_name.lower() != "optional":
                difference_1, difference_2 = mdx23c_similarity_extractor(model, input_1, input_2, difference, output_name, ZF_infer, model_dir)
            else:
                difference_1, difference_2 = mdx23c_similarity_extractor(model, input_1, input_2, difference, None, ZF_infer, model_dir)
            print("pass")
            if pp_mode == True:
                return difference_1, difference_2
            
        except Exception as e:
            print(e)
    print("rip")

def run_vrv6_similarity_extractor(model, input_1, input_2, difference, output_name, sim_of_dif, VR_infer, model_dir,pp_mode):
    if not None in [input_1, input_2]:
        try:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            if output_name.lower() != "optional":
                difference_1, difference_2 = vrv6_similarity_extractor(model, input_1, input_2, difference, output_name, sim_of_dif, VR_infer, model_dir)
            else:
                difference_1, difference_2 = vrv6_similarity_extractor(model, input_1, input_2, difference, None, sim_of_dif, VR_infer, model_dir)
            print("pass")
            if pp_mode == True:
                return difference_1, difference_2
            
        except Exception as e:
            print(e)
    print("rip")

def vrv6_similarity_extractor(model, file_input_1, file_input_2, difference, output_name, double, VR_infer, model_dir):
    try:
        start = time.time()
        #load inputs
        input_1, samplerate = librosa.load(file_input_1, 44100, mono=False)
        input_2, samplerate_2 = librosa.load(file_input_2, 44100, mono=False)
                    
        #convert from mono to stereo if needed
        if input_1.ndim == 1:
            input_1 = np.stack([input_1, input_1], axis=1)
            input_2 = np.stack([input_2, input_2], axis=1)
        
        #pad array length
        if len(input_1[0]) != len(input_2[0]):
            if len(input_1[0]) > len(input_2[0]):
                input_2 = np.stack([np.pad(input_2[0], (0, len(input_1[0]) - len(input_2[0])), 'constant', constant_values=0),\
                                    np.pad(input_2[1], (0, len(input_1[0]) - len(input_2[0])), 'constant', constant_values=0)], axis=1)
            else:

                input_1 = np.stack([np.pad(input_1[0], (0, len(input_2[0]) - len(input_1[0])), 'constant', constant_values=0),\
                                    np.pad(input_1[1], (0, len(input_2[0]) - len(input_1[0])), 'constant', constant_values=0)], axis=1)
        inputs_loaded = time.time()
        print(f"inputs loaded in {inputs_loaded - start}s")
        print(input_1.shape,input_2.shape)
        print("fucker")
        #split channels
        input_1_L = input_1[0]
        input_1_R = input_1[1]
        input_2_L = input_2[0]
        input_2_R = input_2[1]

        print("here")
        
        #merge stereo channels
        inputs_L = np.stack([input_1_L, input_2_L], axis=1)
        inputs_R = np.stack([input_1_R, input_2_R], axis=1)

        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"temp")
        temp_path = os.path.join(temp_dir,"temp")
        print(temp_dir)

        print(inputs_L,inputs_R)

        sf.write(f"{temp_dir}/temp_L.wav", inputs_L, samplerate, 'float')            
        sf.write(f"{temp_dir}/temp_R.wav", inputs_R, samplerate, 'float')
        print("why")
    
        #centre isolation
        #separate similarities
        os.chdir(temp_dir)

        if "4K" in model:
            n_fft = 4096
            hop_length = 2048
            crop_size = 512
        else:
            n_fft = 2048
            hop_length = 1024
            crop_size = 256

        os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_L.wav" -f {n_fft} -H {hop_length} -c {crop_size} -P "{model_dir}/{model}.pth" -X --gpu 0 & pause')
        os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_R.wav" -f {n_fft} -H {hop_length} -c {crop_size} -P "{model_dir}/{model}.pth" -X --gpu 0')

        #remove temp files
        os.remove(f"{temp_dir}/temp_L.wav")
        os.remove(f"{temp_dir}/temp_R.wav")

        similarity_L, _ = librosa.load(f"{temp_dir}/temp_L_Vocals.wav", 44100, mono=False)
        similarity_R, _ = librosa.load(f"{temp_dir}/temp_R_Vocals.wav", 44100, mono=False)

        #remove temp files
        os.remove(f"{temp_dir}/temp_L_Vocals.wav")
        os.remove(f"{temp_dir}/temp_R_Vocals.wav")

        if double == True:
            if "4K" in model:
                n_fft = 4096
                hop_length = 2048
                crop_size = 512
            else:
                n_fft = 2048
                hop_length = 1024
                crop_size = 256
            os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_L_Vocals.wav" -f {n_fft} -H {hop_length} -c {crop_size} -P "{model_dir}/{model}.pth" -X --gpu 0 & pause')
            os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_R_Vocals.wav" -f {n_fft} -H {hop_length} -c {crop_size} -P "{model_dir}/{model}.pth" -X --gpu 0')
            similarity_L, _ = librosa.load(f"{temp_dir}/temp/temp_L_Vocals_Vocals.wav", 44100, mono=False)
            similarity_R, _ = librosa.load(f"{temp_dir}/temp/temp_R_Vocals_Vocals.wav", 44100, mono=False)
        #finalise similarities - the AI models may have different similarities
        similarity_1 = np.stack([similarity_L[0], similarity_R[0]], axis=1)
        similarity_2 = np.stack([similarity_L[1], similarity_R[1]], axis=1)

        #make differences
        difference_1 = np.stack(input_1, axis=1) - similarity_1
        difference_2 = np.stack(input_2, axis=1) - similarity_2
        
        output_folder = os.path.dirname(file_input_1)
        file_1_name = Path(file_input_1).stem
        file_2_name = Path(file_input_2).stem
        
        #output paths
        if output_name is not None:
            outpath_1 = os.path.join(output_folder, output_name)
        else:
            outpath_1 = os.path.join(output_folder, file_1_name)
            outpath_2 = os.path.join(output_folder, file_2_name)

        if difference == True and output_name is None:
            #output differences
            sf.write(f"{outpath_1}-differences.wav", input_1_differences, samplerate, 'float')            
            sf.write(f"{outpath_2}-differences.wav", input_2_differences, samplerate, 'float')
        elif difference == True and output_name is not None:
            sf.write(f"{outpath_1}-differences_1.wav", input_1_differences, samplerate, 'float')            
            sf.write(f"{outpath_1}-differences_2.wav", input_2_differences, samplerate, 'float')
        

        #output similarities
        sf.write(f"{outpath_1}-similarities.wav", similarity_1, samplerate, 'float')
        sf.write(f"{outpath_1}-similarity_2(debug).wav", similarity_2, samplerate, 'float')
        print(outpath_1)
        finished = time.time()
        print(f"Processing complete after: {finished - inputs_loaded}s \n Total time: {finished - start}s")
        #for post_process
        return difference_1, difference_2

    except Exception as e:
        print(e)

def vrv6_post_process(model, file_input_1, file_input_2, difference, output_name, VR_infer, model_dir):
    try:
        start = time.time()
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"temp")
        sf.write(f"{temp_dir}/temp_1.wav", file_input_1, 44100, 'float')            
        sf.write(f"{temp_dir}/temp_2.wav", file_input_2, 44100, 'float')
        
        #centre isolation
        #separate similarities
        os.chdir(temp_dir)

        if "4k" in model:
            n_fft = 4096
            hop_length = 2048
            crop_size = 512
        else:
            n_fft = 2048
            hop_length = 1024
            crop_size = 256
        
        os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_1.wav" -f {n_fft} -H {hop_length} -c {crop_size} -P "{model_dir}/{model}.pth" -o "temp"')
        os.system(f'python "{VR_infer}" -i "{temp_dir}/temp_2.wav" -f {n_fft} -H {hop_length} -c {crop_size} -P "{model_dir}/{model}.pth" -o "temp"')

        #remove temp files
        os.remove(f"{temp_dir}/temp_1.wav")
        os.remove(f"{temp_dir}/temp_2.wav")

        difference_1_pp, _ = librosa.load(f"{temp_dir}/temp_1_Instruments.wav", 44100, mono=False)
        difference_2_pp, _ = librosa.load(f"{temp_dir}/temp_2_Instruments.wav", 44100, mono=False)

        #remove temp files
        os.remove(f"{temp_dir}/temp_1_Instruments.wav")
        os.remove(f"{temp_dir}/temp_2_Instruments.wav")
        
        finished = time.time()
        print(f"Processing complete after: {finished - inputs_loaded}s \n Total time: {finished - start}s")
        #for post_process
        return difference_1_pp, difference_2_pp

    except Exception as e:
        print(e)


plugin_name = r"Bertom_PhantomCenter.vst3"

def similarity_difference_extractor(file_input_1, file_input_2, difference, output_name, double):
    try:
        start = time.time()
        #load inputs
        input_1, samplerate = librosa.load(file_input_1, 44100, mono=False)
        input_2, samplerate_2 = librosa.load(file_input_2, 44100, mono=False)
                
        #convert from mono to stereo if needed
        if input_1.ndim == 1:
            input_1 = np.stack([input_1, input_1], axis=1)
            input_2 = np.stack([input_2, input_2], axis=1)
        
        #pad array length
        if len(input_1[0]) != len(input_2[0]):
            if len(input_1[0]) > len(input_2[0]):
                input_2 = np.stack([np.pad(input_2[0], (0, len(input_1[0]) - len(input_2[0])), 'constant', constant_values=0),\
                                    np.pad(input_2[1], (0, len(input_1[0]) - len(input_2[0])), 'constant', constant_values=0)], axis=0)
            else:

                input_1 = np.stack([np.pad(input_1[0], (0, len(input_2[0]) - len(input_1[0])), 'constant', constant_values=0),\
                                    np.pad(input_1[1], (0, len(input_2[0]) - len(input_1[0])), 'constant', constant_values=0)], axis=0)
        inputs_loaded = time.time()
        print(f"inputs loaded in {inputs_loaded - start}s")
        print(input_1.shape,input_2.shape)
        #split channels
        input_1_L = input_1[0]
        input_1_R = input_1[1]
        input_2_L = input_2[0]
        input_2_R = input_2[1]
        
        #merge stereo channels
        inputs_L = np.stack([input_1_L, input_2_L], axis=0)
        inputs_R = np.stack([input_1_R, input_2_R], axis=0)

        inputs_L_wav_buffer = io.BytesIO(AudioFile.encode(inputs_L, samplerate, "wav", 2, 32))
        inputs_R_wav_buffer = io.BytesIO(AudioFile.encode(inputs_R, samplerate, "wav", 2, 32))

        if difference == True or double == True:
            #side isolation
            plugin = load_plugin(plugin_name, parameter_values = {'hpf': 'Off', 'lpf': 'Off', 'mix': -100, 'output': 0.0, 'bypass': 'Normal'})
            assert plugin.is_effect
            
            #separate differences
            with AudioFile(inputs_L_wav_buffer) as f:
                differences_L = plugin(f.read(f.frames), samplerate)
                
            with AudioFile(inputs_R_wav_buffer) as f:
                differences_R = plugin(f.read(f.frames), samplerate)

            #merge differences of each source
            input_1_differences = np.stack([differences_L[0], differences_R[0]], axis=1)
            input_2_differences = np.stack([differences_L[1], differences_R[1]], axis=1)

        #centre isolation
        plugin = load_plugin(plugin_name, parameter_values = {'hpf': 'Off', 'lpf': 'Off', 'mix': 100, 'output': 0.0, 'bypass': 'Normal'})
        assert plugin.is_effect

        #separate similarities
        with AudioFile(inputs_L_wav_buffer) as f:
            similarity_L = plugin(f.read(f.frames), samplerate)
            
        with AudioFile(inputs_R_wav_buffer) as f:
            similarity_R = plugin(f.read(f.frames), samplerate)

        #finalise similarities
        similarity = np.stack([librosa.to_mono(similarity_L), librosa.to_mono(similarity_R)], axis=1)

        output_folder = os.path.dirname(file_input_1)
        file_1_name = Path(file_input_1).stem
        file_2_name = Path(file_input_2).stem
        
        #output paths
        if output_name is not None:
            outpath_1 = os.path.join(output_folder, output_name)
        else:
            outpath_1 = os.path.join(output_folder, file_1_name)
            outpath_2 = os.path.join(output_folder, file_2_name)

        if double == True:
            input_1_differences =  np.stack([-differences_L[0], -differences_R[0]], axis=0)
            input_2_differences =  np.stack([differences_L[1], differences_R[1]], axis=0)
            
            #sometimes some similarites are phase-inverted
            differences_Ls =  np.stack([input_1_differences[0], input_2_differences[0]], axis=0)
            differences_Rs =  np.stack([input_1_differences[1], input_2_differences[1]], axis=0)
            
            differences_Ls_wav_buffer = io.BytesIO(AudioFile.encode(differences_Ls, samplerate, "wav", 2, 32))
            differences_Rs_wav_buffer = io.BytesIO(AudioFile.encode(differences_Rs, samplerate, "wav", 2, 32))

            #separate similarities of differences
            with AudioFile(differences_Ls_wav_buffer) as f:
                similarity_differences_Ls = plugin(f.read(f.frames), samplerate)
                
            with AudioFile(differences_Rs_wav_buffer) as f:
                similarity_differences_Rs = plugin(f.read(f.frames), samplerate)
            
            #finalise similarities of differences
            similarity_differences = np.stack([librosa.to_mono(similarity_differences_Ls), librosa.to_mono(similarity_differences_Rs)], axis=1)
            if output_name is None:
                #output similarity differences
                sf.write(f"{outpath_1}-differences_similarity.wav", -similarity_differences, samplerate, 'float')            
                sf.write(f"{outpath_2}-differences_similarity.wav", similarity_differences, samplerate, 'float')
            else:
                sf.write(f"{outpath_1}-differences_similarity_1.wav", -similarity_differences, samplerate, 'float')            
                sf.write(f"{outpath_1}-differences_similarity_2.wav", similarity_differences, samplerate, 'float')

            #remove similarity of differences
            input_1_differences = np.stack([
                differences_Ls[0] - similarity_differences_Ls[0],
                differences_Rs[0] - similarity_differences_Rs[0]
            ], axis=1)

            input_2_differences = np.stack([
                differences_Ls[1] - similarity_differences_Ls[1],
                differences_Rs[1] - similarity_differences_Rs[1]
            ], axis=1)

        if difference == True and output_name is None:
            #output differences
            sf.write(f"{outpath_1}-differences.wav", input_1_differences, samplerate, 'float')            
            sf.write(f"{outpath_2}-differences.wav", input_2_differences, samplerate, 'float')
        elif difference == True and output_name is not None:
            sf.write(f"{outpath_1}-differences_1.wav", input_1_differences, samplerate, 'float')            
            sf.write(f"{outpath_1}-differences_2.wav", input_2_differences, samplerate, 'float')
        

        #output similarities
        sf.write(f"{outpath_1}-similarities.wav", similarity, samplerate, 'float')
        finished = time.time()
        print(f"Processing complete after: {finished - inputs_loaded}s \n Total time: {finished - start}s")
        #for post_process
        return difference_1, difference_2
    except Exception as e:
        print(e)

def mdx23c_similarity_extractor(model, file_input_1, file_input_2, difference, output_name, ZF_infer, model_dir):
    try:
        start = time.time()
        #load inputs
        input_1, samplerate = librosa.load(file_input_1, 44100, mono=False)
        input_2, samplerate_2 = librosa.load(file_input_2, 44100, mono=False)
                    
        #convert from mono to stereo if needed
        if input_1.ndim == 1:
            input_1 = np.stack([input_1, input_1], axis=1)
            input_2 = np.stack([input_2, input_2], axis=1)
        
        #pad array length
        if len(input_1[0]) != len(input_2[0]):
            if len(input_1[0]) > len(input_2[0]):
                input_2 = np.stack([np.pad(input_2[0], (0, len(input_1[0]) - len(input_2[0])), 'constant', constant_values=0),\
                                    np.pad(input_2[1], (0, len(input_1[0]) - len(input_2[0])), 'constant', constant_values=0)], axis=0)
            else:

                input_1 = np.stack([np.pad(input_1[0], (0, len(input_2[0]) - len(input_1[0])), 'constant', constant_values=0),\
                                    np.pad(input_1[1], (0, len(input_2[0]) - len(input_1[0])), 'constant', constant_values=0)], axis=0)
        inputs_loaded = time.time()
        print(f"inputs loaded in {inputs_loaded - start}s")
        print(input_1.shape,input_2.shape)
        #split channels
        input_1_L = input_1[0]
        input_1_R = input_1[1]
        input_2_L = input_2[0]
        input_2_R = input_2[1]
        
        #merge stereo channels
        inputs_L = np.stack([input_1_L, input_2_L], axis=1)
        inputs_R = np.stack([input_1_R, input_2_R], axis=1)

        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"temp")
        sf.write(f"{temp_dir}/temp_L.wav", inputs_L, samplerate, 'float')            
        sf.write(f"{temp_dir}/temp_R.wav", inputs_R, samplerate, 'float')
        
        #centre isolation
        #separate similarities
        os.chdir(temp_dir)
        os.system(f'python "{ZF_infer}" --input_folder "{temp_dir}" --config_path "{model_dir}/{model}.yaml" --start_check_point "{model_dir}/{model}.ckpt" --store_dir "temp" & pause')

        #remove temp files
        os.remove(f"{temp_dir}/temp_L.wav")
        os.remove(f"{temp_dir}/temp_R.wav")

        similarity_L, _ = librosa.load(f"{temp_dir}/temp/temp_L_similarity.wav", 44100, mono=False)
        similarity_R, _ = librosa.load(f"{temp_dir}/temp/temp_R_similarity.wav", 44100, mono=False)

        #remove temp files
        os.remove(f"{temp_dir}/temp/temp_L_similarity.wav")
        os.remove(f"{temp_dir}/temp/temp_R_similarity.wav")
        
        #finalise similarities - the AI models may have different similarities
        similarity_1 = np.stack([similarity_L[0], similarity_R[0]], axis=1)
        similarity_2 = np.stack([similarity_L[1], similarity_R[1]], axis=1)

        #make differences
        difference_1 = np.stack(input_1, axis=1) - similarity_1
        difference_2 = np.stack(input_2, axis=1) - similarity_2
        
        output_folder = os.path.dirname(file_input_1)
        file_1_name = Path(file_input_1).stem
        file_2_name = Path(file_input_2).stem
        
        #output paths
        if output_name is not None:
            outpath_1 = os.path.join(output_folder, output_name)
        else:
            outpath_1 = os.path.join(output_folder, file_1_name)
            outpath_2 = os.path.join(output_folder, file_2_name)

        if difference == True and output_name is None:
            #output differences
            sf.write(f"{outpath_1}-differences.wav", input_1_differences, samplerate, 'float')            
            sf.write(f"{outpath_2}-differences.wav", input_2_differences, samplerate, 'float')
        elif difference == True and output_name is not None:
            sf.write(f"{outpath_1}-differences_1.wav", input_1_differences, samplerate, 'float')            
            sf.write(f"{outpath_1}-differences_2.wav", input_2_differences, samplerate, 'float')
        

        #output similarities
        sf.write(f"{outpath_1}-similarities.wav", similarity_1, samplerate, 'float')
        sf.write(f"{outpath_1}-similarity_2(debug).wav", similarity_2, samplerate, 'float')
        finished = time.time()
        print(f"Processing complete after: {finished - inputs_loaded}s \n Total time: {finished - start}s")
        #for post_process
        return difference_1, difference_2

    except Exception as e:
        print(e)

def mdx23c_post_process(model, file_input_1, file_input_2, difference, output_name, ZF_infer, model_dir):
    try:
        start = time.time()
        #load inputs
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"temp")
        sf.write(f"{temp_dir}/temp_1.wav", file_input_1, 44100, 'float')
        sf.write(f"{temp_dir}/temp_2.wav", file_input_2, 44100, 'float')
        
        #centre isolation
        os.chdir(temp_dir)
        os.system(f'python "{ZF_infer}" --input_folder "{temp_dir}" --config_path "{model_dir}/{model}.yaml" --start_check_point "{model_dir}/{model}.ckpt" --store_dir "temp" --extract_instrumental')

        #remove temp files
        os.remove(f"{temp_dir}/temp_1.wav")
        os.remove(f"{temp_dir}/temp_2.wav")
        
        difference_1_pp, _ = librosa.load(f"{temp_dir}/temp/temp_L_instrumental.wav", 44100, mono=False)
        difference_2_pp, _ = librosa.load(f"{temp_dir}/temp/temp_R_instrumental.wav", 44100, mono=False)
        
        #remove temp files
        os.remove(f"{temp_dir}/temp/temp_1_instrumental.wav")
        os.remove(f"{temp_dir}/temp/temp_2_instrumental.wav")
        
        finished = time.time()
        print(f"Total time: {finished - start}s")
        #for post_process
        return difference_1_pp, difference_2_pp

    except Exception as e:
        print(e)
