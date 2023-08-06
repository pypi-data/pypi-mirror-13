
import numpy as np 

def CODAGE_ALEATOIRE(G,BRUIT=1,sigma=1):
    """
    Fonction qui génère aléatoirement un message de k bits v, le code avec la matrice G et le transmet dans le canal
    après modulation BPSK pour renvoyer le couple (d,y). On renvoie d afin d'être capable de vérifier la qualité
    du décodage.
    
    G: matrice de codage
    BRUIT: booléen, présence de bruit dans le canal.
    
    """
    k,n = G.shape
    
    v=np.random.randint(2,size=k)
    d=BinaryProduct(v,G)
    x=pow(-1,d)

    if BRUIT:
        e = np.random.normal(0,sigma,size=n)
    else:
        e=0

    y=x+e

    return(d,y)



def CODAGE_SPECIFIQUE(G,v,BRUIT=1,sigma=1):
    """
    Fonction qui code un message spécifique  de k bits v, le code avec la matrice G et le transmet dans le canal
    après modulation BPSK pour renvoyer le couple (d,y). On renvoie d afin d'être capable de vérifier la qualité
    du décodage.
    
    G: matrice de codage
    BRUIT: booléen, présence de bruit dans le canal.
    v: message à envoyer (k bits)
    
    
    """
    k,n = G.shape
    
    if len(v)!= k:
        raise ValueError('La taille du message doit être égale au nombre de lignes de G')
    
    d=BinaryProduct(v,G)
    x=pow(-1,d)

    if BRUIT:
        e = np.random.normal(0,sigma,size=n)
    else:
        e=0

    y=x+e

    return(d,y)
   