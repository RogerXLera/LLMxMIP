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
 - **Explanation Quality**: *explanation_comparison.xlsx* files within the DPP and RCPSP folders contain the textual explanations and the data of the quantitative analysis. 
 - **Empirical Hardness**: *iis* folder contains files that save the extracted IIS. Within such files, there is saved the runtime to compute the IIS. 

Execution
----------
To solve the optimisation problem, execute [`problem.py`](problem.py) Python script,
```
usage: python3 problem.py [--time TIME] [--threads THREADS] [--file file] [specific problem arguments]

optional arguments:
  -h, --help         show this help message and exit
  --time TIME        time limit (default: 60)
  --threads THREADS  query type (default: 1)
  
```

Our approach must be executed by means of the [`iis.py`](iis.py) Python script to compute an IIS,

```
usage: python3 iis.py [-s S] [-q Q] [--file file] [specific problem arguments]

optional arguments:
  -h, --help  show this help message and exit
  -s S        time limit (default: 60)
  -q Q        query type (default: 1)
  --file FILE instance file
  
```

Execute [`llm.py`](llm.py) Python script to compute a prompt for an LLM,

```
usage: python3 prompt.py [-s S] [-q Q] [--file file] [specific problem arguments]

optional arguments:
  -h, --help  show this help message and exit
  -s S        time limit (default: 60)
  -q Q        query type (default: 1)
  --file FILE instance file
  
```