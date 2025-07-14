ExMIP: Experimental Evaluation
===================
This repository contains the implementation of the algorithms and data of the experimental section of the paper
"Constraint Reasoning and Large Language Models Join Forces: Providing Contrastive Explanations for Real-World Optimisation-Based Applications" by Roger X. Lera-Leri, Filippo Bistaffa, Athina Georgara, Juan A. Rodríguez-Aguilar. 


Dependencies
----------
 - [Python 3.10](https://www.python.org/downloads/)
 - [Numpy](https://numpy.org/)
 - [Docplex](https://www.cvxpy.org/)
 - [CPLEX](https://www.ibm.com/es-es/products/ilog-cplex-optimization-studio)


Dataset
----------

 - **RCPSP**: The single-mode RCPSP instances used come from [PSPLIB](https://www.om-db.wi.tum.de/psplib/) library.
 - **DPP**: A real-world instance for the Bachelor's Degree in Information Communication Technologies of the [Western Sydney University](https://www.westernsydney.edu.au/).

Results
----------
 - **Explanation Quality**: [`explanation_comparison.xlsx`](DPP/explanation_comparison.xlsx) files within the DPP and RCPSP folders contain the textual explanations and the data of the quantitative analysis. 
 - **Empirical Hardness**: [`iis.py`](DPP/iis.py) folder contains files that save the extracted IIS. Within such files, there is saved the runtime to compute the IIS. 

Reproducibility
----------

Here, we describe the steps to reproduce the results of the experimental section. 

 1. **Solve an optimisation problem instance**, run [`problem.py`](DPP/problem.py) Python script,
```
usage: python3 problem.py [--time TIME] [--threads THREADS] [--file file] [specific problem arguments]

optional arguments:
  -h, --help         show this help message and exit
  --time TIME        time limit (default: 60)
  --threads THREADS  query type (default: 1)
  
```
We can solve all the problem instances by varying the input arguments (which are specific for each problem). Furthermore, in the folder [`solutions`](DPP/solutions), we store all the optimal solutions and their runtime.  

 2. **Compute an IIS**, run [`iis.py`](DPP/iis.py) Python script,

```
usage: python3 iis.py [-s S] [-q Q] [--file file] [specific problem arguments]

optional arguments:
  -h, --help  show this help message and exit
  -s S        time limit (default: 60)
  -q Q        query type (default: 1)
  --file FILE instance file
  
```
We can extract iis for all the generated queries by varying the input arguments (which are specific for each problem). Furthermore, in the folder [`iis`](DPP/iis), we store all the extracted iis and their runtime.  

 3. **Compute a prompt for an LLM**, run [`llm.py`](DPP/llm.py) Python script,

```
usage: python3 llm.py [-q Q] [specific problem arguments]

optional arguments:
  -h, --help  show this help message and exit
  -q Q        query type (default: 1)
  
```
We can compute a prompt for generating an explanation by varying the input arguments (which are specific for each problem). Furthermore, in the folder [`prompt`](DPP/prompt), we store all the generated prompts for the selection of queries.  