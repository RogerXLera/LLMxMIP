"""
Author: Roger X. Lera Leri
Date: 2025/04/24
"""

import cplex as cp
import numpy as np
import argparse as ap
import time
import csv
import os
from docplex.mp.model import Model


if __name__ == '__main__':
    
    parser = ap.ArgumentParser()
    parser.add_argument('-n', type=int, default=6, help='n')
    parser.add_argument('-c', type=int, default=240, help='c')
    parser.add_argument('-l', type=int, default=7, help='l: maximum level. Default: 7')
    parser.add_argument('-j', type=str, default='0', help='Job index')
    parser.add_argument('-s', type=str, default='au', help='Start semester')
    parser.add_argument('--time', type=int, default=60, help='s: Time limit in seconds')
    parser.add_argument('--threads', type=int, default=1, help='threads: number of threads')
    args = parser.parse_args()
    
    
    from read_files import read_instance
    I = read_instance(args.n,args.c,args.j,args.s,args.l)

    I.solve(solution_time=args.time,log=False,n_threads=args.threads)
    I.print_solution()

    