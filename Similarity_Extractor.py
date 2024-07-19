from pedalboard import load_plugin
import io
from pedalboard.io import AudioFile
import numpy as np
import librosa
import os
from pathlib import Path
import soundfile as sf


plugin_name = r"Bertom_PhantomCenter.vst3"

def similarity_difference_extractor(file_input_1, file_input_2, difference, output_name, double):
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
    
    #output paths
    if output_name is not None:
        outpath_1 = os.path.join(os.path.dirname(file_input_1), output_name)
    else:
        outpath_1 = os.path.join(os.path.dirname(file_input_1), Path(file_input_1).stem)
        outpath_2 = os.path.join(os.path.dirname(file_input_1), Path(file_input_2).stem)

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
    else:
        sf.write(f"{outpath_1}-differences_1.wav", input_1_differences, samplerate, 'float')            
        sf.write(f"{outpath_1}-differences_2.wav", input_2_differences, samplerate, 'float')
    

    #output similarities
    sf.write(f"{outpath_1}-similarities.wav", similarity, samplerate, 'float')

