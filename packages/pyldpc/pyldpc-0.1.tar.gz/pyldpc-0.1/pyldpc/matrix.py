import numpy as np

def CallagerH(n,d_v,d_c):
    import numpy as np

    """Fonction qui construit la matrice de parité H de taille m,n  avec la méthode de Callager : 
    
    argument n: la taille du mot codé 
    argument d_v: nombre de 1 par colonne (v pour variable);
    argument d_c: nombre de 1 par ligne (n pour noeud);  doit diviser n 

    
    """
    
    
    
    if  n%d_c:
        raise ValueError('d_c doit diviser n.')
    
    if d_c < d_v: 
        raise ValueError('d_c doit être plus grand que d_v: H doit avoir plus de colonnes que de lignes')
    
    m = (n*d_v)// d_c
    
    Set=np.zeros((m//d_v,n),dtype=int)  
    a=m//d_v
    
    # Pour le premier set, on remplit les d_c 1 l'un suivi de l'autre comme dans la figure ci-dessus.
    for i in range(a):     
        for j in range(i*d_c,(i+1)*d_c): 
            Set[i,j]=1
    #On crée la liste de sets et on y ajoute le premier set
    Sets=[]
    Sets.append(Set.tolist())
    
    #On permute les colonnes du premier set pour obtenir des nouveaux sets qu'on ajoute à la liste Sets
    #s'ils n'y sont pas déjà : 
    i=1
    for i in range(1,d_v):
        newSet = np.transpose(np.random.permutation(np.transpose(Set))).tolist()
        Sets.append(newSet)
    
    #On renvoie les sets regroupés:
    H = np.concatenate(Sets)
    return H
        
    
# Test de la fonction 
CallagerH_test = 0

if CallagerH_test:
    Htest = CallagerH(12,3,4)
    print("La matrice de parité régulière (12,3,4):\n",Htest )

def BinaryProduct(X,Y):
    
    """ Produit matriciel dans Z/2Z"""
    
    A = np.dot(X,Y)
    
    B = A.reshape((A.size,1))
    for i in range(A.size):
        B[i]=B[i]%2
    return B.reshape(A.shape)


def GaussJordan(MATRICE,passage=0):
    
    """ Fonction qui transforme MATRICE en une matrice échelonnée réduite. 
     
    Si Inverse =1, Elle effectue les même opérations sur la matrice identité pour renvoyer la matrice de
    Passage P telle que: P.H = rowreduced_H
    
    """
    
    A = np.copy(MATRICE)
    m,n = A.shape
    rang = np.linalg.matrix_rank(MATRICE)
    if passage:
        P = np.identity(m).astype(int)
    

    for j in range(min(m,n)):            
            
        listeDePivots_down = [i for i in range(j,m) if A[i,j]]
        if len(listeDePivots_down)>0:
            pivot = np.min(listeDePivots_down)
        else:
            
            continue
           
             
        if pivot!=j:
            
            aux = np.copy(A[j,:])
            A[j,:] = A[pivot,:]
            A[pivot,:] = aux
            if passage:
                aux = np.copy(P[j,:])
                P[j,:] = np.copy(P[pivot,:])
                P[pivot,:] = aux

        
        for i in listeDePivots_down[1:]:
            A[i,:] = abs(A[i,:]-A[j,:])
            if passage:
                P[i,:] = abs(P[i,:]-P[j,:])
        
        listeDePivots_up = [i for i in range(j) if A[i,j]]
    
        for i in listeDePivots_up:
            A[i,:] = abs(A[i,:]-A[j,:])
            if passage:
                P[i,:] = abs(P[i,:]-P[j,:])
    if passage:    
        return A,P 
    return A 


####################### Test de la fonction:


GaussJordan_test = 0

if GaussJordan_test:
    
    Htest=CallagerH(12,2,6)
    Hrowreduced, P = GaussJordan(Htest,1)
    print("\nLa matrice Hrowreduced P.H: \n\n{} \n ".format(Hrowreduced))

    #On vérife Hreducedtest = P.H 
    print("P.H = Hrowreduced ?",(BinaryProduct(P,Htest)==Hrowreduced).all())



def PJQ(MATRICE):
    
    """ Fonction qui renvoie Q en appliquant Gauss-Jordan deux fois 

         """
    
   
    H = np.copy(MATRICE)
    m,n = H.shape
    
    if m > n: 
        raise ValueError('H doit avoir plus de colonnes que de lignes')
        

    ##### DOUBLE GAUSS-JORDAN:
    
    rang = np.linalg.matrix_rank(H)
    Href_colonnes,tQ = GaussJordan(np.transpose(H),1)
        
    Href_diag = GaussJordan(np.transpose(Href_colonnes))    
    
    #### PERMUTATIONS POUR OBTENIR LE BLOC IDENTITE:
    
    zeros = [i for i in range(m) if not Href_diag[i,i]]
    if len(zeros)>0:
        while (min(zeros) < rang):

            indice_de_0 = min(zeros)
            indice_de_1 = min([i for i in range (indice_de_0,m) if Href_diag[i,i]])
            
            Href_diag[indice_de_0,:] = np.copy(Href_diag[indice_de_1,:])
            Href_diag[indice_de_1,:] = np.zeros(n) 

            Href_diag[:,indice_de_0] = np.copy(Href_diag[:,indice_de_1])
            Href_diag[:,indice_de_1] = np.zeros(m) 
            
            aux = np.copy(tQ[indice_de_1,:])
            tQ[indice_de_1,:] = np.copy(tQ[indice_de_0,:])
            tQ[indice_de_0,:] = aux
            
            zeros = [i for i in range(m) if not Href_diag[i,i]]
        

            
    Q=np.transpose(tQ)
    
    return Q 

def CodageMatrix(H):
    m,n = H.shape
     
    Q = PJQ(H)
    
    k = n - np.linalg.matrix_rank(H)
    
    ## On résoud J.Qinv.G' = 0 en posant Y = Qinv.G'
    
    Y = np.zeros(shape=(n,k)).astype(int)
    Y[list(range(n-k,n)),list(range(0,k))] = np.ones(k)
    
    tG = BinaryProduct(Q,Y)
    
    return np.transpose(tG)

