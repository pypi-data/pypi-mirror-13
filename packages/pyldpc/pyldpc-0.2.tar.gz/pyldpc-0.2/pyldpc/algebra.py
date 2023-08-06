import math
import numpy as np

pi = math.pi

def BinaryProduct(X,Y):

    """ Binary Matrix or vectors product in Z/2Z"""


    A = np.dot(X,Y)

    B = A.reshape((A.size,1))
    for i in range(A.size):
        B[i]=B[i]%2

    return B.reshape(A.shape)
    

def GaussJordan(MATRIX,change=0):

    """ 
    Description:

    Performs the row reduced echelon form of MATRIX and returns it.

    If change = 1, all changes in the MATRIX's rows are applied to identity matrix P: 

    Let A be our parameter MATRIX. refA the reduced echelon form of A. P is the square invertible matrix:

    P.A = Aref.

    -------------------------------------------------
    Parameters: 

    MATRIX: 2D-Array. 
    change : boolean (default = 0)

    ------------------------------------------------

    change = 0  (default)
     >>> Returns 2D-Array Row Reduced Echelon form of Matrix

    change = 1 
    >>> Returns Tuple of 2D-arrays (refMATRIX, P) where P is described above.

    """

    A = np.copy(MATRIX)
    m,n = A.shape
    rang = np.linalg.matrix_rank(MATRIX)
    if change:
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
            if change:
                aux = np.copy(P[j,:])
                P[j,:] = np.copy(P[pivot,:])
                P[pivot,:] = aux


        for i in listeDePivots_down[1:]:
            A[i,:] = abs(A[i,:]-A[j,:])
            if change:
                P[i,:] = abs(P[i,:]-P[j,:])

        listeDePivots_up = [i for i in range(j) if A[i,j]]

        for i in listeDePivots_up:
            A[i,:] = abs(A[i,:]-A[j,:])
            if change:
                P[i,:] = abs(P[i,:]-P[j,:])
    if change:    
        return A,P 
    return A 

def PJQ(MATRIX):

    """ 
    CAUTION : THIS FUNCTIONS IS NOT MEANT TO BE USED EXCEPT WHEN CALLED BY 
    CODINGMATRIX FUNCTION TO SOLVE H.G' = 0, THAT'S WHY THE CONDITION M < N 
    (more columns than rows) MUST BE CHECKED.


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


    ______________________

    returns: Q 

    NOTE: P IS NOT RETURNED BECAUSE WE DO NOT NEED IT TO SOLVE H.G' = 0 
    P IS INVERTIBLE, WE GET SIMPLY RID OF IT. 

    """


    H = np.copy(MATRIX)
    m,n = H.shape

    if m > n: 
        raise ValueError('MATRIX must have more rows than columns (a parity check matrix)')


    ##### DOUBLE GAUSS-JORDAN:

    rang = np.linalg.matrix_rank(H)
    Href_colonnes,tQ = GaussJordan(np.transpose(H),1)

    Href_diag = GaussJordan(np.transpose(Href_colonnes))    

    #### PERMUTATIONS TO GET THE IDENTITY BLOC:

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
    

def f1(y,sigma):
    """ Normal Density N(1,sigma) """ 
    return(np.exp(-.5*pow((y-1)/sigma,2))/(sigma*math.sqrt(2*pi)))

def fM1(y,sigma):
    """ Normal Density N(-1,sigma) """ 

    return(np.exp(-.5*pow((y+1)/sigma,2))/(sigma*math.sqrt(2*pi)))

def Nimj(H,i,j):
    m,n=H.shape
    """
    Computes list of elements of N(i)-j:
    List of variables (bits) connected to Parity node i, except bit j

    """
    return ([a for a in range(n) if H[i,a] and a!=j])

def Mjmi(H,i,j):
    m,n=H.shape
    """
    Computes list of elements of M(j)-i:
    List of nodes (PC equations) connecting variable j, except node i

    """
    return ([a for a in range(m) if H[a,j] and a!=i])

def InCode(H,x):

    """ Computes Binary Product of H and x. If product is null, x is in the code.

        Returns appartenance boolean. 
    """
    return( (BinaryProduct(H,x)==0).all())


def GaussElimination(MATRIX,B):

    """ Applies Gauss Elimination Algorithm to MATRIX in order to solve a linear system MATRIX.X = B. 
    MATRIX is transformed to row echelon form: 

         |1 * * * * * |
         |0 1 * * * * |
         |0 0 1 * * * |
         |0 0 0 1 * * | 
         |0 0 0 0 1 * |
         |0 0 0 0 0 1 |
         |0 0 0 0 0 0 |
         |0 0 0 0 0 0 |
         |0 0 0 0 0 0 |


    Same row operations are applied on 1-D Array vector B. Both arguments are sent back.
    
    --------------------------------------
    
    Parameters:
    
    MATRIX: 2D-array. 
    B:      1D-array. Size must equal number of rows of MATRIX.
            
    -----------------------------------
    Returns:
    
    Modified arguments MATRIX, B as described above.
    
         """

    A = np.copy(MATRIX)
    b = np.copy(B)
    n,k = A.shape


    if b.size != n:
        raise ValueError('Size of B must match number of rows of MATRIX to solve MATRIX.X = B')

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

