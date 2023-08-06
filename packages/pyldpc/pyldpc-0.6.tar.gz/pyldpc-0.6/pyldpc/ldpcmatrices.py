import numpy as np
from .ldpcalgebra import*

__all__ = ['BinaryProduct', 'InCode', 'BinaryRank','RegularH','CodingMatrix','CodingMatrix_systematic']


def RegularH(n,d_v,d_c):

    """ ------------------------------------------------------------------------------

    Builds a regular Parity-Check Matrix H (n,d_v,d_c) following Callager's algorithm : 

    ----------------------------------------------------------------------------------

    Paramaeters:

     n: Number of columns (Same as number of coding bits)
     d_v: number of ones per column (number of parity-check equations including a certain variable) 
     d_c: number of ones per row (number of variables participating in a certain parity-check equation);  

    ----------------------------------------------------------------------------------

    Errors: 

     The number of ones in the matrix is the same no matter how we calculate it (rows or columns), therefore, if m is 
     the number of rows in the matrix: 

     m*d_c = n*d_v with m < n (because H is a decoding matrix) => Parameters must verify:


     0 - all integer parameters
     1 - d_v < d_v
     2 - d_c divides n 

    ---------------------------------------------------------------------------------------

     Returns: 2D-array (shape = (m,n))

    """


    if  n%d_c:
        raise ValueError('d_c must divide n. Help(RegularH) for more info.')

    if d_c <= d_v: 
        raise ValueError('d_c must be greater than d_v. Help(RegularH) for more info.')

    m = (n*d_v)// d_c

    Set=np.zeros((m//d_v,n),dtype=int)  
    a=m//d_v

    # Filling the first set with consecutive ones in each row of the set 

    for i in range(a):     
        for j in range(i*d_c,(i+1)*d_c): 
            Set[i,j]=1

    #Create list of Sets and append the first reference set
    Sets=[]
    Sets.append(Set.tolist())

    #Create remaining sets by permutations of the first set's columns: 
    i=1
    for i in range(1,d_v):
        newSet = np.transpose(np.random.permutation(np.transpose(Set))).tolist()
        Sets.append(newSet)

    #Returns concatenated list of sest:
    H = np.concatenate(Sets)
    return H



def CodingMatrix(MATRIX):

    """ 
    Function Applies GaussJordan Algorithm on Columns and rows of MATRIX in order
    to permute Basis Change matrix using Matrix Equivalence.

    Let A be the treated Matrix. refAref the double row reduced echelon Matrix.

    refAref has the form:

    (e.g) : |1 0 0 0 0 0 ... 0 0 0 0|  
            |0 1 0 0 0 0 ... 0 0 0 0| 
            |0 0 0 0 0 0 ... 0 0 0 0| 
            |0 0 0 1 0 0 ... 0 0 0 0| 
            |0 0 0 0 0 0 ... 0 0 0 0| 
            |0 0 0 0 0 0 ... 0 0 0 0| 


    First, let P1 Q1 invertible matrices: P1.A.Q1 = refAref

    We would like to calculate:
    P,Q are the square invertible matrices of the appropriate size so that:

    P.A.Q = J.  Where J is the matrix of the form (having MATRIX's shape):

    | I_p O | where p is MATRIX's rank and I_p Identity matrix of size p.
    | 0   0 |

    Therfore, we perform permuations of rows and columns in refAref (same changes
    are applied to Q1 in order to get final Q matrix)


    NOTE: P IS NOT RETURNED BECAUSE WE DO NOT NEED IT TO SOLVE H.G' = 0 
    P IS INVERTIBLE, WE GET SIMPLY RID OF IT. 
    
    Then
    
    solves: inv(P).J.inv(Q).G' = 0 (1) where inv(P) = P^(-1) and 
    P.H.Q = J. Help(PJQ) for more info.
    
    Let Y = inv(Q).G', equation becomes J.Y = 0 (2) whilst:
    
    J = | I_p O | where p is H's rank and I_p Identity matrix of size p.
        | 0   0 |
    
    Knowing that G must have full rank, a solution of (2) is Y = |  0  | Where k = n-p. 
                                                                 | I-k |
    
    Because of rank-nullity theorem. 
    
    -----------------
    parameters:
    
    H: Parity check matrix. 
    
    ---------------
    returns:
    
    G: Coding Matrix. 
    
    """


    H = np.copy(MATRIX)
    m,n = H.shape

    if m > n: 
        raise ValueError('MATRIX must have more rows than columns (a parity check matrix)')


    ##### DOUBLE GAUSS-JORDAN:

    Href_colonnes,tQ = GaussJordan(np.transpose(H),1)

    Href_diag = GaussJordan(np.transpose(Href_colonnes))    

    Q=np.transpose(tQ)
    	
    ##########
    
    k = n - sum(Href_diag.reshape(m*n))

    
    Y = np.zeros(shape=(n,k)).astype(int)
    Y[n-k:,:] = np.identity(k)

    tG = BinaryProduct(Q,Y)

    G = np.transpose(tG)
    return G
    
    
def CodingMatrix_systematic(MATRIX):

    """ 
    Description:

    Solves H.G' = 0 and finds the coding matrix G in the systematic form : [I_k  A] by applying permutations on MATRIX.
    
    CAUTION: RETURNS TUPLE (Hp,GS) WHERE Hp IS A MODIFIED VERSION OF THE GIVEN PARITY CHECK MATRIX, GS THE SYSTEMATIC 
    CODING MATRIX ASSOCIATED TO Hp. YOU MUST USE THE RETURNED TUPLE IN CODING AND DECODING, RATHER THAN THE UNCHANGED 
    PARITY-CHECK MATRIX H. 

    -------------------------------------------------
    Parameters: 

    MATRIX: 2D-Array. Parity-check matrix.

    ------------------------------------------------

    >>> Returns Tuple of 2D-arrays (Hp,GS):
        Hp: Modified H: permutation of columns of H (The code doesn't change)
        GS: Systematic Coding matrix associated to Hp.
        
        YOU MUST USE THE RETURNED TUPLE IN CODING AND DECODING, RATHER THAN THE UNCHANGED 
    PARITY-CHECK MATRIX H. 

    """

    H = np.copy(MATRIX)
    m,n = H.shape
    
    P1 = np.identity(n,dtype=int)
    
    Hrowreduced = GaussJordan(H)
    
    k = n - sum([a.any() for a in Hrowreduced ])

    ## After this loop, Hrowreduced will have the form H_ss : | I_(n-k)  A |
    while(True):
        zeros = [i for i in range(min(m,n)) if not Hrowreduced[i,i]]
        indice_colonne_a = min(zeros)
        list_ones = [j for j in range(indice_colonne_a+1,n) if Hrowreduced[indice_colonne_a,j]]
        if not len(list_ones):
            break

        indice_colonne_b = min(list_ones)
        
        aux = np.copy(Hrowreduced[:,indice_colonne_a])
        Hrowreduced[:,indice_colonne_a] = Hrowreduced[:,indice_colonne_b]
        Hrowreduced[:,indice_colonne_b] = aux 
        
        permut = np.array(list(range(n)))
        permut[indice_colonne_a] = indice_colonne_b
        permut[indice_colonne_b] = indice_colonne_a
        
        matrix_permut = np.zeros(shape=(n,n),dtype=int)
        matrix_permut[list(range(n)),permut] = np.ones(n)
        
        P1 = BinaryProduct(matrix_permut,P1)
    
    ############ NOW, Hrowreduced has the form: | I_(n-k)  A | , the permutation above makes it look like : 
    ########### |A  I_(n-k)|
    
    
    identity = list(range(n))
    sigma = identity[n-k:]+identity[:n-k]
    
    P2 = np.zeros(shape=(n,n),dtype=int)
    P2[identity,sigma] = np.ones(n)

    P = BinaryProduct(P2,P1)

    Hp = BinaryProduct(MATRIX,np.transpose(P))

    GS = np.zeros((k,n),dtype=int)
    GS[:,:k] = np.identity(k)
    GS[:,k:] = np.transpose(Hrowreduced[:n-k,n-k:])

    
    return Hp,GS
