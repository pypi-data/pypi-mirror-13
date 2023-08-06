PyLDPC  v0.2 - README 

----------------

Simulation of LDPC Codes 
Detailed documentation (English) about any function f can be found using help(f).

Jupyter notebook Tutorial (French) is available on 
https://github.com/janatiH/pyldpc/blob/master/pyLDPC-Presentation.ipynb

-------------------------------------------
version 0.2:

- Coding and decoding matrices Generators.
- Coding function adding Additive White Gaussion Noise.
- Decoding functions using Probabilistic Decoding (Belief propagation algorithm)

----------------

- Functions: 

RegularH: Generating Regular(n,d_v,d_c) Parity Matrix H using Callager's method
CodingMatrixG : Finds Coding Matrix G (solves H.G' = 0 ) 
Coding: Codes a random vector v using Coding matrix G and adds Gaussian Noise. 
Decoding_BP : Decoding function based on Belief Propagation Algorithm 
Decoding_logBP : Decoding based on Logarithmic BP Algorithm 


- Image Transmission functions coming soon. 