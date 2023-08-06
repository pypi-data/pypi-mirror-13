import numpy as np
from .soundformat import Audio2Bin, Bin2Audio
from .codingfunctions import Coding
from .decodingfunctions import Decoding_BP, Decoding_logBP, DecodedMessage

__all__=['Audio2Bin','Bin2Audio','SoundCoding','SoundDecoding','BER_audio']

def SoundCoding(G,audio_bin,snr,show=1):
    
    """ 
    
    Codes a binary audio array (Therefore must be a 2D-array shaped (length,17)). Each element (17 bits)
    is considered a k-bits message. If the original binary array is shaped (length,17). The coded image will be shaped 
    (length,n) Where n is the length of a codeword. Then a gaussian noise N(0,snr) is added to the codeword.
    
    Remember SNR: Signal-Noise Ratio: SNR = 10log(1/variance) in decibels of the AWGN used in coding.

    Of course, "listening" to an audio file with n-bits array is impossible, that's why if the optional argument show is set to 1, 
    and if Coding Matrix G is systematic, reading the noisy sound can be possible by gathering the 17 first bits of each 
    n-bits codeword to the left, the redundant bits are dropped. Then the noisy sound is changed from bin to int16. 
    Remember that in this case, SoundCoding returns  a tuple: the (length,n) coded audio, and the noisy one (length).
    
    Parameters:

    G: Coding Matrix G - must be systematic if you want to see what the noisy audio sounds like. See CodingMatrix_systematic.
    audio_bin: 2D-array of a binary audio shaped (length,17).
    SNR: Signal-Noise Ratio, SNR = 10log(1/variance) in decibels of the AWGN used in coding.
    show: (optional, default = True) if True, returns a second array of a noisy int16 sound. 
    
    
    Returns:
    (default): Tuple: noisy_audio, coded_audio
    (if show = False) : coded_audio. 2D-array of a coded audio. Each "element" is a codeword (in BPSK) + AWGN 
    
    
    """
    
    k,n = G.shape
    length = audio_bin.shape[0]
    
    if k!=17:
        raise ValueError('Coding matrix G must have 17 rows (Audio files are written in int16 which is equivalent to uint17)')
        

    coded_audio = np.zeros(shape=(length,n))
    
    if show:
        noisy_audio = np.zeros(shape=(length,k),dtype=int)
    
    for j in range(length):
        coded_number_j = Coding(G,audio_bin[j,:],snr)
        coded_audio[j,:] = coded_number_j
        if show:
            systematic_part_j = (coded_number_j[:k]<0).astype(int)
            noisy_audio[j,:] = systematic_part_j        
                
    if show:
        noisy_audio = Bin2Audio(noisy_audio)
        return coded_audio,noisy_audio
    
    return coded_audio
    
    
def SoundDecoding(G,H,audio_coded,snr,max_iter=1,log=1):
    
    """ 
    Sound Decoding Function. Taked the 2-D binary coded audio array where each element is a codeword n-bits array and decodes 
    every one of them. Needs H to decode and G to solve v.G = x where x is the codeword element decoded by the function
    itself. When v is found for each codeword, the decoded audio can be transformed from binary to int16 format and read.
    
    Parameters: 
    
    G: Coding Matrix 
    H: Parity-Check Matrix (Decoding matrix). 
    audio_coded: binary coded audio returned by the function SoundCoding. Must be shaped (length, n) where n is a
                the length of a codeword (also the number of H's columns)
    
    snr: Signal-Noise Ratio: SNR = 10log(1/variance) in decibels of the AWGN used in coding.
    
    log: (optional, default = True), if True, Full-log version of BP algorithm is used. 
    max_iter: (optional, default =1), number of iterations of decoding. increase if snr is < 5db. 

    
    """
    
    k,n = G.shape
    if k!=17:
        raise ValueError('Coding matrix G must have 17 rows (Audio files are written in int16 which is equivalent to uint17)')
       
    length = audio_coded.shape[0]
    
    audio_decoded_bin = np.zeros(shape=(length,k),dtype = int)

    if log:
        DecodingFunction = Decoding_logBP
    else:
        DecodingFunction = Decoding_BP
    
    for j in range(length):

        decoded_vector = DecodingFunction(H,audio_coded[j,:],snr,max_iter)
        decoded_number = DecodedMessage(G,decoded_vector)

        audio_decoded_bin[j,:] = decoded_number 
    
    audio_decoded = Bin2Audio(audio_decoded_bin)
 
    return audio_decoded
    
def BER_audio(original_audio_bin,decoded_audio_bin):
    """ 
    
    Computes Bit-Error-Rate (BER) by comparing 2 binary audio arrays.
    The ratio of bit errors over total number of bits is returned.
    
    """
    if not original_audio_bin.shape == decoded_audio_bin.shape:
        raise ValueError('Original and decoded audio files\' shapes don\'t match !')
        
    length, k = original_audio_bin.shape 
    
    total_bits  = np.prod(original_audio_bin.shape)

    errors_bits = sum(abs(original_audio_bin-decoded_audio_bin).reshape(length*k))
    
    BER = errors_bits/total_bits 
    
    return(BER)
