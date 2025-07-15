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
 - **Empirical Hardness**: [`iis`](DPP/iis) directory contains files that save the extracted IIS. Within such files, there is saved the runtime to compute the IIS. To compare the runtime needed to extract an IIS with respect to solve the optimisation problem, we save also the runtime to solve the optimisation problem in the files within the [`solutions`](DPP/solutions) directory, which they contain the solution of the optimisation problems. 

Execution
----------

Here, we describe the commands to run our code. 

 1. **Solve an optimisation problem instance**, run [`problem.py`](DPP/problem.py) Python script,
```
usage: python3 problem.py [--time TIME] [--threads THREADS] [specific problem arguments]

optional arguments:
  -h, --help         show this help message and exit
  --time TIME        time limit (default: 60)
  --threads THREADS  number of threads type (default: 1)
  
DPP specific arguments:
  -n N               number of semesters (default: 6)
  -c C               total number of credits (default: 240 (40 per semester))
  -j J               job index (default: '0')

RCPSP specific arguments:
  -n N               number of activities (default: 30)
  -f F               file name of the instance (default: j301_1.sm)
```


 2. **Compute an IIS**, run [`iis.py`](DPP/iis.py) Python script,

```
usage: python3 iis.py [--time TIME] [--threads THREADS] [-q Q] [specific problem arguments]

optional arguments:
  -h, --help  show this help message and exit
  --time TIME        time limit (default: 60)
  --threads THREADS  number of threads type (default: 1)
  -q Q               query type (default: 1, min: 1, max: 10)  

DPP specific arguments:
  -n N               number of semesters (default: 6)
  -c C               total number of credits (default: 240 (40 per semester))
  -j J               job index (default: '0')
  -i I               query instance (default: 1, min: 0, max: 4)

RCPSP specific arguments:
  -n N               number of activities (default: 30)
  -f F               file name of the instance (default: j301_1.sm)
```

 3. **Compute a prompt for an LLM**, run [`llm.py`](DPP/llm.py) Python script,

```
usage: python3 llm.py [-q Q] [-s] [specific problem arguments]

optional arguments:
  -h, --help  show this help message and exit
  -q Q        query type (default: 1, min: 1, max: 10)
  -s          compute a prompt with only "reasons" (otherwise, compute a prompt with the encoding of the graph of reasons)

DPP specific arguments:
  -j J               job index (default: '104')
  -i I               query instance (default: 3, min: 0, max: 4)

RCPSP specific arguments:
  -n N               number of activities (default: 30)
  -f F               file name of the instance (default: j301_1.sm)
  
```


Reproducibility
----------

Here, we describe the steps to reproduce the results of the experimental section. 

"*Empiricial Hardness*" Results (Section 4.3)

 1. **Solve an optimisation problem instance**, run [`problem.py`](DPP/problem.py) Python script for all the problem instances.

  - DPP: The Bachelor's Degree data does not vary, only varies the target job targeted. Thus, we we need to solve the problem for each desired job to reproduce the results. The indexes of each job is a row in [`job_index.txt`](DPP/data/job_index.txt) file. 

  Example 1: solve the DPP problem targeting job 1:
  ```
  cd DPP/
  python3 problem.py -j 1
  ```
  Result: Optimal Objective Value = 7.0

  - RCPSP: All the problem instances are within [`data`](RCPSP/data) directory. We test our approach with instances of 30, 60, and 90 activities, a total of 1440 instances. 

  Example 2: solve intance j302_1 of the RCPSP problem:
  ```
  cd RCPSP/
  python3 problem.py -n 30 -f j302_3.sm
  ```
  Result: Optimal Objective Value = 43

  We can solve all the problem instances by varying the input arguments as shown in both examples. However, in the folder [`solutions`](DPP/solutions), we store all the optimal solutions and their runtime for both problems.  

 2. **Compute an IIS**, run [`iis.py`](DPP/iis.py) Python script for all problem instances and generated queries. The queries are already generated (with [`generate_query`](DPP/generate_query.py) file) and stored in [`queries`](DPP/queries) directory.     

 - DPP: For each instance of the DPP (solved in the previous step), we need to compute an IIS for 5 different query instances of each query type (10 types of queries, a total of 50 queries per problem instance). Since there are 118 different target jobs, we compute an IIS for a total of 5900 queries. 

 Example 3: compute an IIS for query instance  the DPP problem targeting job 1:
  ```
  cd DPP/
  python3 iis.py -j 0 -q 2 -i 1
  ```
  Result: 
  ```
  IIS generation
  Instance: 0
  ----------------------------
  Query: 2
  Query element: 300093,2
  Query scope: 67
  ----------------------------
  IIS optimality: infeasible
  IIS solution time: 0.009
  IIS Constraint: 90; offer; {unit:300093,season:sp}
  IIS Constraint: 680; query; {unit:300093,semester:2,query:2}
  ```

 - RCPSP: For each instance of the RCPSP (solved in the previous step), we need to compute an IIS for each query type (10 types of queries). Since there are 1440 different problem instances, we compute an IIS for a total of 14400 queries. 

 Example 4: compute an IIS for query type 3 of problem instance j302_3 of the RCPSP problem:
  ```
  cd RCPSP/
  python3 iis.py -n 30 -q 3 -f j302_3.sm
  ```
  Result: 
  ```
  IIS generation
  Instance: j302_3
  ----------------------------
  Query: 3
  Query element:26,35
  Query scope: 3472
  Query scope: 3473
  Query scope: 3474
  Query scope: 3475
  Query scope: 3476
  ----------------------------
  IIS optimality: suboptimal
  IIS solution time: 2.062
  IIS Constraint: 5; completion; {activity:6}
  IIS Constraint: 6; completion; {activity:7}
  IIS Constraint: 11; completion; {activity:12}
  IIS Constraint: 23; completion; {activity:24}
  IIS Constraint: 25; completion; {activity:26}
  IIS Constraint: 50; precedence; {activity:19,predecessor:6}
  IIS Constraint: 53; precedence; {activity:21,predecessor:12}
  IIS Constraint: 54; precedence; {activity:21,predecessor:19}
  IIS Constraint: 56; precedence; {activity:22,predecessor:21}
  IIS Constraint: 57; precedence; {activity:23,predecessor:7}
  IIS Constraint: 65; precedence; {activity:26,predecessor:24}
  IIS Constraint: 67; precedence; {activity:28,predecessor:23}
  IIS Constraint: 72; precedence; {activity:30,predecessor:22}
  IIS Constraint: 73; precedence; {activity:30,predecessor:28}
  IIS Constraint: 78; precedence; {activity:32,predecessor:30}
  IIS Constraint: 268; renewable; {resource:2,t:13}
  IIS Constraint: 274; renewable; {resource:2,t:19}
  IIS Constraint: 780; query; {activity:26,t:35,query:3}
  IIS Constraint: 781; max; {f:43.0,objective:max}
  ```

  We reproduce the results, one can extract an IIS for all the query instances by varying the input arguments as shown in both examples. However, in the folder [`iis`](DPP/iis), we store all the optimal solutions and their runtime for both problems.  


"*Completeness and Readability*" Results (Section 4.2)

  1. **Compute prompts for an LLM**, run [`llm.py`](DPP/llm.py) Python script that computes a prompt as an input to an LLM. To reproduce the results obtained, generate the prompts of the different query instances. The reasons are already pre-computed (as a result of applying our methodology up until computing the graph of reasons) in directory [`reasons`](DPP/reasons) for both problems. There, we stored the reasons (classified per query type) for each generated query. [`llm.py`](DPP/llm.py) file builds two distinct prompts:

  - A prompt with a textual encoding of the graph of reasons (option by default)

  - A prompt with only the reasons (use argument```-s``` when running [`llm.py`](DPP/llm.py)).

  Example 5: Compute the prompt with a textual encoding of a graph of reasons for the DPP, with target job 0, query type 2, and query instance 1. 

  ```
  cd DPP/
  python3 llm.py -j 0 -q 2 -i 1
  ```

  Example 6: Compute the prompt with the reasons for the RCPSP, for instance j302_2, and query type 3. 

  ```
  cd RCPSP/
  python3 llm.py -n 30 -q 3 -f j302_3.sm -s
  ```

  Notice that in practice, the only difference between both prompts is that the prompt with the encoding of a graph of reasons, contains the relations between reasons. Notice also, that in [`reasons`](DPP/reasons) there aren't the reasons for all query instances. This is because for query instances where the IIS is empty, i.e., the user-desired scenario is as good as the optimal solution, there is not possible to generate a contrastive explanation since the user query is possible to satisfy. Finally, all the prompts needed to reproduce the results can be found in the [`prompt`](DPP/prompt) directory for both of the problems. 

  2. **Compute an explanation using an LLM**. Use both prompts described in the previous step to compute two different explanations. We used gpt-4o model. 

  3. **Analyse the explanations**. Since there are many queries, we analysed a selection of all the generated explanations because counting the reasons mentioned within an explanation is a manual task. In [`explanation_comparison.xlsx`](DPP/explanation_comparison.xlsx) file (for both problems), one can find the generated explanations (with and without a graph of reasons), with the number of reasons counted. 
  