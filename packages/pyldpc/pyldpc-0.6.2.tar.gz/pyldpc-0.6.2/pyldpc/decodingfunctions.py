import numpy as np
from .ldpcalgebra import*

__all__ = ['BinaryProduct', 'InCode', 'BinaryRank','Decoding_logBP','Decoding_BP','DecodedMessage']

def Decoding_BP(H,y,SNR,max_iter=1):

    """ Decoding function using Belief Propagation algorithm.

    -----------------------------------
    Parameters:

    y: n-vector recieved after transmission in the channel. (In general, returned 
    by Coding Function)

    H: Parity check matrix, shape = (m,n)

    Signal-Noise Ratio: SNR = 10log(1/variance) in decibels of the AWGN used in coding.
    
    max_iter: (default = 1) max iterations of the main loop. (for snr > 7db in general).

     """
    m,n=H.shape
    if not len(y)==n:
        raise ValueError('Size of y must be equal to number of parity matrix\'s columns n')

    if m>=n:
        raise ValueError('H must be of shape (m,n) with m < n')

    sigma = 10**(-SNR/20)
    
    p0 = np.zeros(shape=n)
    p0 = f1(y,sigma)/(f1(y,sigma) + fM1(y,sigma))
    p1 = np.zeros(shape=n)
    p1 = fM1(y,sigma)/(f1(y,sigma) + fM1(y,sigma))



    #### ETAPE 0 : Initialization 
    q0 = np.zeros(shape=(m,n))
    q0[:] = p0

    q1 = np.zeros(shape=(m,n))
    q1[:] = p1

    r0 = np.zeros(shape=(m,n))
    r1 = np.zeros(shape=(m,n))

    count=0

    while(True):

        count+=1 #Compteur qui empêche la boucle d'être infinie .. 

        #### ETAPE 1 : Horizontale

        deltaq = q0 - q1
        deltar = r0 - r1 

        for i in range(m):
            Ni=Nimj(H,i,n+1)
            for j in Ni:
                Nij = Nimj(H,i,j)
                deltar[i,j] = np.prod(deltaq[i,Nij])

        r0 = 0.5*(1+deltar)
        r1 = 0.5*(1-deltar)


        #### ETAPE 2 : Verticale

        for j in range(n):
            Mj = Mjmi(H,m+1,j)
            for i in Mj:
                Mji = Mjmi(H,i,j)
                q0[i,j] = p0[j]*np.prod(r0[Mji,j])
                q1[i,j] = p1[j]*np.prod(r1[Mji,j])
                
                if q0[i,j] + q1[i,j]==0:
                    q0[i,j]=0.5
                    q1[i,j]=0.5
              
                else:
                    alpha=1/(q0[i,j]+q1[i,j]) #Constante de normalisation alpha[i,j] 

                    q0[i,j]*= alpha
                    q1[i,j]*= alpha # Maintenant q0[i,j] + q1[i,j] = 1


        #### Calcul des probabilites à posteriori:
        q0_post = np.zeros(n)
        q1_post = np.zeros(n)
        for j in range(n):
            M=Mjmi(H,m+1,j)
            q0_post[j] = p0[j]*np.prod(r0[M,j])
            q1_post[j] = p1[j]*np.prod(r1[M,j])
            
            if q0_post[j] + q1_post[j]==0:
                q0_post[j]=0.5
                q1_post[j]=0.5
                
            alpha = 1/(q0_post[j]+q1_post[j])
            
            q0_post[j]*= alpha
            q1_post[j]*= alpha
        
        
        x = np.array(q1_post > q0_post).astype(int)

        if InCode(H,x) or count > max_iter:  
            break
  
    return x

def Decoding_logBP(H,y,SNR,max_iter=1):
    """ Decoding function using Belief Propagation algorithm (logarithmic version)

    -----------------------------------
    Parameters:

    y: n-vector recieved after transmission in the channel. (In general, returned 
    by Coding Function)

    H: Parity check matrix, shape = (m,n)

    Signal-Noise Ratio: SNR = 10log(1/variance) in decibels of the AWGN used in coding.

    max_iter: (default = 1) max iterations of the main loop. (for snr > 7b 1 is suffiscient in general) 

    """
    m,n=H.shape
    
    if not len(y)==n:
        raise ValueError('La taille de y doit correspondre au nombre de colonnes de H')

    if m>=n:
        raise ValueError('H doit avoir plus de colonnes que de lignes')

    sigma = 10**(-SNR/20)
    
    ### ETAPE 0: initialisation 
    Lc = 2*y/pow(sigma,2)

    Lq=np.zeros(shape=(m,n))
    Lq[:]=Lc

    Lr = np.zeros(shape=(m,n))

    count=0
    while(True):

        count+=1 #Compteur qui empêche la boucle d'être infinie .. 

        #### ETAPE 1 : Horizontale

        for i in range(m):
            Ni=Nimj(H,i,n+1)
            for j in Ni:
                Nij = Nimj(H,i,j)
                X = np.prod(np.tanh(0.5*Lq[i,Nij]))
                num = 1 + X
                denom = 1 - X
                if num == 0: 
                    Lr[i,j] = -1
                elif denom  == 0:
                    Lr[i,j] =  1
                else: 
                    Lr[i,j] = np.log(num/denom)

        #### ETAPE 2 : Verticale

        for j in range(n):
            Mj = Mjmi(H,m+1,j)
            for i in Mj:
                Mji = Mjmi(H,i,j)
                Lq[i,j] = Lc[j]+sum(Lr[Mji,j])

        #### LLR a posteriori:
        L_posteriori = np.zeros(n)
        for j in range(n):
            Mj = Mjmi(H,m+1,j)

            L_posteriori[j] = Lc[j] + sum(Lr[Mj,j])


        x = np.array(L_posteriori <= 0).astype(int)

        if InCode(H,x) or count > max_iter:  
            break
            
    return x



def DecodedMessage(G,x):

    """
    Let G be a coding matrix. x a n-vector received after decoding.
    DecodedMessage Solves the equation on k-bits message v:  x = v.G => G'v'= x' by applying GaussElimination on G'.
    
    -------------------------------------
    
    Parameters:
    
    G: Coding Matrix. Must have more rows than columns to solve the linear system. Must be full rank.
    x: n-array. Must be in the Code (in Ker(H)). 

    """
    k,n = G.shape 
    
    if n < k:
        raise ValueError('Coding matrix G must have more rows than columns to solve the linear system.')
    
    if BinaryRank(G)!=k:
        raise ValueError('Coding matrix G must have full rank.')
                         
    tG=np.transpose(G)
    rtG, rx = GaussElimination(tG,x)

    message=np.zeros(k).astype(int)

    message[k-1]=rx[k-1]
    for i in reversed(range(k-1)):
        message[i]=abs(rx[i]-BinaryProduct(rtG[i,list(range(i+1,k))],message[list(range(i+1,k))]))

    return message
