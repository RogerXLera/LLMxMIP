

import cplex as cp
import numpy as np
import argparse as ap
import time
import csv
import os
from docplex.mp.model import Model


if __name__ == '__main__':
    
    parser = ap.ArgumentParser()
    parser.add_argument('-n', type=int, default=30, help='n: Number of activities')
    parser.add_argument('-f', type=str, default = 'j301_1.sm', help='filename of the instance')
    parser.add_argument('-s', type=int, default=60, help='s: Time limit in seconds')
    args = parser.parse_args()
    
    path = os.getcwd()
    folder = os.path.join(path,'data')
    file = os.path.join(folder,f'j{args.n}',args.f)
    
    from read_files import read_instance
    P = read_instance(file)

    from definitions import Instance
    I = Instance(id=0,project=P)
    I.solve(solution_time=args.s,log=True)
    I.print_solution()
        
    