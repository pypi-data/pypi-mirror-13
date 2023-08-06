import numpy as np
from . import algebra

def Coding_random(G, noise = 1,sigma = 0.75):
    """
    Randomly computes a k-bits message v, where G's shape is (k,n). And sends it
    through the canal.
    Message v is passed to G: d = v,G. d is a n-vector turned into a BPSK modulated
    vector x. If noise = 1 (default), Additive White Gaussian Noise (AWGN) 
    (standard deviation = sigma, default is 0.75) to x to obtain n-vector y. 

    Remember: 
        1. d = v.G
        2. x = BPSK(d) (or if you prefer the math: x = pow(-1,d)
        3. y = x + AWGN(0,sigma) (if NOISE)

    ----------------------------

    Parameters:

    G: 2D-Array, Coding Matrix obtained from CodingMatrixG function.
    noise: Boolean (default = 1) 
            Adds AWGN(0,sigma) to BPSK coded message x. 
    sigma: Standard deviation of Gaussian noise. 

    -------------------------------

    Returns

    Tuple(v,y) (Returns v to keep track of the random message v)
    """
    k,n = G.shape

    v=np.random.randint(2,size=k)
    d=algebra.BinaryProduct(v,G) 
    x=pow(-1,d)

    if noise:
        e = np.random.normal(0,sigma,size=n)
    else:
        e=0

    y=x+e

    return(v,y)



def Coding(G,v,noise=1,sigma=1):
    """
    Codes a message v with Coding Matrix G, and sends it through a noisy (default)
    channel. 

    G's shape is (k,n). 

    Message v is passed to G: d = v,G. d is a n-vector turned into a BPSK modulated
    vector x. If noise = 1 (default), Additive White Gaussian Noise (AWGN) 
    (standard deviation = sigma, default is 0.75) to x to obtain n-vector y. 

    Remember: 
        1. d = v.G
        2. x = BPSK(d) (or if you prefer the math: x = pow(-1,d)
        3. y = x + AWGN(0,sigma) (if NOISE)

    ----------------------------

    Parameters:

    G: 2D-Array, Coding Matrix obtained from CodingMatrixG function.
    v: 1D-Array, k-vector (binary of course ..) 
    noise: Boolean (default = 1) 
    Adds AWGN(0,sigma) to BPSK coded message x. 
    sigma: Standard deviation of Gaussian noise. 

    -------------------------------

    Returns y

    """
    k,n = G.shape

    if len(v)!= k:
        raise ValueError(" Size of message v must be equal to number of Coding Matrix G's rows " )  

    d=algebra.BinaryProduct(v,G)
    x=pow(-1,d)

    if noise:
        e = np.random.normal(0,sigma,size=n)
    else:
        e=0

    y=x+e

    return y

