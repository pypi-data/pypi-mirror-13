import numpy as np
from . import algebra

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



def CodingMatrixG(H):

    """ Solves H.G' = 0 knowing Parity check matrix H by calling PJQ function. 
    Therefore solves: inv(P).J.inv(Q).G' = 0 (1) where inv(P) = P^(-1) and 
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
    m,n = H.shape

    Q = algebra.PJQ(H)

    k = n - np.linalg.matrix_rank(H)

    ## Solve J.Qinv.G' = 0 with Y = Qinv.G'
    ## and so that rank(G) = n - rank(H)

    Y = np.zeros(shape=(n,k)).astype(int)
    Y[list(range(n-k,n)),list(range(0,k))] = np.ones(k)

    tG = algebra.BinaryProduct(Q,Y)

    return np.transpose(tG)
