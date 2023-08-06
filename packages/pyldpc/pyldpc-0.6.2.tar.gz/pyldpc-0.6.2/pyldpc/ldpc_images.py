import numpy as np
from .imagesformat import int2bitarray, bitarray2int, Bin2Gray, Gray2Bin, RGB2Bin, Bin2RGB
from .codingfunctions import Coding
from .decodingfunctions import Decoding_BP, Decoding_logBP, DecodedMessage

__all__=['ImageCoding','ImageDecoding','int2bitarray','bitarray2int','Bin2Gray',
		'Gray2Bin','RGB2Bin','Bin2RGB','BER']
		
def ImageCoding(G,img_bin,snr,show=1):
    
    """ 
    
    Codes a binary image (Therefore must be a 3D-array). Each pixel (k bits-array, k=8 if grayscale, k=24 if colorful) 
    is considered a k-bits message. If the original binary image is shaped (X,Y,k). The coded image will be shaped (X,Y,n)
    Where n is the length of a codeword. Then a gaussian noise N(0,snr) is added to the codeword.
    
    Remember SNR: Signal-Noise Ratio: SNR = 10log(1/variance) in decibels of the AWGN used in coding.

    Of course, showing an image with n-bits array is impossible, that's why if the optional argument show is set to 1, 
    and if Coding Matrix G is systematic, showing the noisy image can be possible by gathering the k first bits of each 
    n-bits codeword to the left, and the redundant bits to the right. Then the noisy image is changed from bin to uint8. 
    Remember that in this case, ImageCoding returns  a tuple: the (X,Y,n) coded image, and the noisy image (X,Y*(n//k)).
    
    Parameters:

    G: Coding Matrix G - must be systematic if you want to see what the noisy image looks like. See CodingMatrix_systematic.
    img_bin: 3D-array of a binary image.
    SNR: Signal-Noise Ratio, SNR = 10log(1/variance) in decibels of the AWGN used in coding.
    show: (optional, default = 1) if True, returns a second array of a noisy uint8 image. 
    
    
    Returns:
    (default): Tuple: noisy_img, coded_img 
    (if show = False) : coded_img. 3D-array of a coded image. Each "element" is a codeword (in BPSK) + AWGN
    
    """
    k,n = G.shape
    height,width,depth = img_bin.shape 
    
    if k!=8 and k!= 24:
        raise ValueError('Coding matrix must have 8 xor 24 rows ( grayscale images xor rgb images)')
        
    redundant_pixels = width*(n-k)//k

    coded_img = np.zeros(shape=(height,width,n))
    
    if show:
        noisy_img = np.zeros(shape=(height,width+redundant_pixels,k),dtype=int)
    
    for i in range(height):
        redundant_i = np.array([],dtype=int)
        for j in range(width):
            coded_byte_ij = Coding(G,img_bin[i,j,:],snr)
            coded_img[i,j,:] = coded_byte_ij
            if show:
                systematic_part_ij = (coded_byte_ij[:k]<0).astype(int)
                redundant_part_ij = (coded_byte_ij[k:]<0).astype(int)

                redundant_i = np.concatenate((redundant_i,redundant_part_ij))

                noisy_img[i,j,:] = systematic_part_ij        
        
        if show:
            redundant_i = redundant_i[:redundant_pixels*k].reshape(redundant_pixels,k)

            noisy_img[i,width:,:] = redundant_i 

        
        
    if show:
        if k==8:
            noisy_img = Bin2Gray(noisy_img)
        else:
            noisy_img = Bin2RGB(noisy_img)
                               
        return coded_img,noisy_img
    
    return coded_img
    
    
def ImageDecoding(G,H,img_coded,snr,max_iter=1,log=1):
    
    """ 
    Image Decoding Function. Taked the 3-D binary coded image where each element is a codeword n-bits array and decodes 
    every one of them. Needs H to decode and G to solve v.G = x where x is the codeword element decoded by the function
    itself. When v is found for each codeword, the decoded image can be transformed from binary to uin8 format and shown.
    
    Parameters: 
    
    G: Coding Matrix 
    H: Parity-Check Matrix (Decoding matrix). 
    img_coded: binary coded image returned by the function ImageCoding. Must be shaped (heigth, width, n) where n is a
                the length of a codeword (also the number of H's columns)
    
    snr: Signal-Noise Ratio: SNR = 10log(1/variance) in decibels of the AWGN used in coding.
    
    log: (optional, default = True), if True, Full-log version of BP algorithm is used. 
    max_iter: (optional, default =1), number of iterations of decoding. increase if snr is < 5db. 

    
    """
    
    k,n = G.shape
    height, width, depth = img_coded.shape
    
    img_decoded_bin = np.zeros(shape=(height,width,k),dtype = int)

    if log:
        DecodingFunction = Decoding_logBP
    else:
        DecodingFunction = Decoding_BP
    
    for i in range(height):
        for j in range(width):
            
            decoded_vector = DecodingFunction(H,img_coded[i,j,:],snr,max_iter)
            decoded_byte = DecodedMessage(G,decoded_vector)
            
            img_decoded_bin[i,j,:] = decoded_byte 
    
    if k==8:
        img_decoded = Bin2Gray(img_decoded_bin)
    else:
        img_decoded = Bin2RGB(img_decoded_bin)

    return img_decoded
    
def BER(original_img_bin,decoded_img_bin):
    """ 
    
    Computes Bit-Error-Rate (BER) by comparing 2 binary images.
    The ratio of bit errors over total number of bits is returned.
    
    """
    if not original_img_bin.shape == decoded_img_bin.shape:
        raise ValueError('Original and decoded images\' shapes don\'t match !')
        
    height, width, k = original_img_bin.shape 
    
    
    errors_bits = sum(abs(original_img_bin-decoded_img_bin).reshape(height*width*k))
    total_bits  = np.prod(original_img_bin.shape)
    
    BER = errors_bits/total_bits 
    
    return(BER)

