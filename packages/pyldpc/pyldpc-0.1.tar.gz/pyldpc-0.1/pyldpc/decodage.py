import math
import numpy as np

pi = math.pi

def f1(y,sigma):
    return(np.exp(-.5*pow((y-1)/sigma,2))/(sigma*math.sqrt(2*pi)))

def fM1(y,sigma):
    
    return(np.exp(-.5*pow((y+1)/sigma,2))/(sigma*math.sqrt(2*pi)))

def Nimj(H,i,j):
    m,n=H.shape
    """Fontion qui renvoie les éléments de N(i)-j:
    bits connectés au noeud de parité i sauf le bit j"""
    return ([a for a in range(n) if H[i,a] and a!=j])

def Mjmi(H,i,j):
    m,n=H.shape
    """Fontion qui renvoie les éléments de M(j)-i:
    noeuds de parités liés à la variable j  sauf le noeud i"""
    return ([a for a in range(m) if H[a,j] and a!=i])

def DansLeCode(H,x):
    """Fonction qui retourne un booléen traduisant l'appartenance de x au code"""
    return(not BinaryProduct(H,x).any())



def DECODAGE_BP(H,y,sigma=1,iterations=10):
    
    """Fonction de décodage BP qui prend en paramètres:
    argument y: message codé reçu après transmission dans le canal; de taille n.
    argument H: Matrice de parité H de taille (m,n)
    argument sigma: écart-type du bruit gaussien du canal
    """
    m,n=H.shape
    if not len(y)==n:
        raise ValueError('La taille de y doit correspondre au nombre de colonnes de H')
    
    if m>=n:
        raise ValueError('H doit avoir plus de colonnes que de lignes')
    
    
    p0 = np.zeros(shape=n)
    p0 = f1(y,sigma)/(f1(y,sigma) + fM1(y,sigma))
    p1 = fM1(y,sigma)/(f1(y,sigma) + fM1(y,sigma))



    #### ETAPE 0 : Initialisation 
    q0 = np.zeros(shape=(m,n))
    q0[:] = p0

    q1 = np.zeros(shape=(m,n))
    q1[:] = p1

    r0 = np.zeros(shape=(m,n))
    r1 = np.zeros(shape=(m,n))
    
    compteur=0
    while(True):
        
        compteur+=1 #Compteur qui empêche la boucle d'être infinie .. 
        
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

                alpha=1/(q0[i,j]+q1[i,j]) #Constante de normalisation alpha[i,j] 

                q0[i,j]*= alpha
                q1[i,j]*= alpha # Maintenant q0[i,j] + q1[i,j] = 1

                
        #### Calcul des probabilités à postériori:
        q0_post = np.zeros(n)
        q1_post = np.zeros(n)

        for j in range(n):
            M=Mjmi(H,m+1,j)
            q0_post[j] = p0[j]*np.prod(r0[M,j])
            q1_post[j] = p1[j]*np.prod(r1[M,j])

            alpha = 1/(q0_post[j]+q1_post[j])

            q0_post[j]*= alpha
            q1_post[j]*= alpha

        x = np.array(q1_post > q0_post).astype(int)
 
        if DansLeCode(H,x) or compteur > iterations:  #Généralement, pour k,n relativement petits (<20)
                                            # un bon décodage ne dépasse pas 10 itérations
            break;

    return x 
  


def DECODAGE_Full_log_BP(H,y,sigma=1,iterations=10):
    """Fonction de décodage full-log BP qui prend en paramètres:
    argument y: message codé reçu après transmission dans le canal; de taille n.
    argument H: Matrice de parité H de taille (m,n)
    argument sigma: écart-type du bruit gaussien du canal
    """
    m,n=H.shape
    if not len(y)==n:
        raise ValueError('La taille de y doit correspondre au nombre de colonnes de H')
    
    if m>=n:
        raise ValueError('H doit avoir plus de colonnes que de lignes')
    
    ### ETAPE 0: initialisation 
    Lc = 2*y/pow(sigma,2)
    
    Lq=np.zeros(shape=(m,n))
    Lq[:]=Lc
    
    Lr = np.zeros(shape=(m,n))
 
    compteur=0
    while(True):
        
        compteur+=1 #Compteur qui empêche la boucle d'être infinie .. 
        
        #### ETAPE 1 : Horizontale

        for i in range(m):
            Ni=Nimj(H,i,n+1)
            for j in Ni:
                Nij = Nimj(H,i,j)
                Lr[i,j] = np.log((1+np.prod(np.tanh(0.5*Lq[i,Nij])))/(1-np.prod(np.tanh(0.5*Lq[i,Nij]))))
                
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
 
        if DansLeCode(H,x) or compteur > iterations:  #Généralement, pour k,n relativement petits (<20)
                                            # un bon décodage ne dépasse pas 10 itérations
            break;

    return x


def Gauss(MATRICE,B):
    
    """ Fonction qui applique l'algorithme du pivot de Gauss. Elle sera appelée par la fonction MessageDecode 
    afin de résoudre l'équation en v:  tG.v = x où x est un vecteur appartenant au code. 
    BinaryGauss sera donc appliquée à tG pour la mettre sous une forme similaire à: 
    
         |1 * * * * * |
         |0 1 * * * * |
         |0 0 1 * * * |
         |0 0 0 1 * * | 
         |0 0 0 0 1 * |
         |0 0 0 0 0 1 |
         |0 0 0 0 0 0 |
         |0 0 0 0 0 0 |
         |0 0 0 0 0 0 |

    Elle applique les mêmes opérations aux lignes de x et renvoie le couple modifié (GausstG,Gaussx)
    
         """
    
    A = np.copy(MATRICE)
    b = np.copy(B)
    n,k = A.shape
    
    
    if n < k:
        raise ValueError('le nombre de lignes de A doit être supérieur ou égal à celui des colonnes.')
    
    for j in range(min(k,n)):
        listeDePivots = [i for i in range(j,n) if A[i,j]]
        if len(listeDePivots)>0:
            pivot = np.min(listeDePivots)
        else:
            continue
        if pivot!=j:
            aux = np.copy(A[j,:])
            A[j,:] = A[pivot,:]
            A[pivot,:] = aux

            aux = np.copy(b[j])
            b[j] = b[pivot]
            b[pivot] = aux
            
        for i in range(j+1,n):
            if A[i,j]:
                A[i,:] = abs(A[i,:]-A[j,:])
                b[i] = abs(b[i]-b[j])

    return A,b




def MessageDecode(G,x):
    
    """
    Fonction qui renvoie le message à k bits à partir du vecteur à n bits appartenant au code. Elle sera
    utilisée dans la transmission d'images afin de pouvoir comparer l'image transmse à l'image reçue. 
    
    argument G : matrice de codage (k,n)
    argument x : vecteur codé (n)
    
    """
    k,n = G.shape 
    
    if x.size != n:
        raise ValueError('la longueur de x doit correspondre au nombre de colonnes de G')

    tG=np.transpose(G)
    rtG, rx = Gauss(tG,x)

    message=np.zeros(k).astype(int)
    
    message[k-1]=rx[k-1]
    for i in reversed(range(k-1)):
        message[i]=abs(rx[i]-myLDPCcodage(rtG[i,list(range(i+1,k))],message[list(range(i+1,k))]))

    return message
   