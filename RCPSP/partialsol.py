import argparse as ap
import pandas as pd
import numpy as np
import csv
import json
import os
import copy
from definitions import *
from read_files import *

def print_partial_sol_q(IIS):

    header = ['activity','start_time','completion_time','duration','predecessors','resources']
    rows = [header]
    q = IIS.query
    C = IIS.constraints
    I = IIS.instance
    P = I.project

    sol = I.solution_values
    var = I.variables

    A = {} #relevant activities
    for cid,c in C.items():
        elem = c.elements
        if 'activity' in elem.keys():
            a = elem['activity']
            A.update({a.id:a})
        elif 'predecessor' in elem.keys():
            a = elem['predecessor']
            A.update({a.id:a})
        elif 'activities' in elem.keys():
            a_list = elem['activities']
            A.update({a:P.activities[a-1] for a in a_list})

    # print partial sol
    for s_id,s in sol.items():
        v = var[s_id]
        a,t = v.elements
        if a.id in A.keys():
            pred_str = ", ".join([str(p) for p in a.predecessors])
            resource_list = [f'r{rid}({r})' for rid,r in a.resources.items() if r > 0]
            if len(resource_list) > 0:
                resource_str = ",".join(resource_list)
            else:
                resource_str = "-"
            if a.duration == 0:
                st = t
            else:
                st = t-a.duration +1

            row = [a.id,st,t,a.duration,pred_str,resource_str]
            rows += [row]

    outputpath = os.path.join(os.getcwd(),'partialsol',f'j{args.n}',f"{I.id}-{q.category}.csv")
    with open(outputpath,'w') as outcsv:
        wrt = csv.writer(outcsv,delimiter=';')
        wrt.writerows(rows)

    return None

def print_complete_sol_q(IIS):

    header = ['activity','start_time','completion_time','duration','predecessors','resources']
    rows = [header]
    q = IIS.query
    I = IIS.instance
    P = I.project

    sol = I.solution_values
    var = I.variables

    

    # print partial sol
    for s_id,s in sol.items():
        v = var[s_id]
        a,t = v.elements
        #if a.id in A.keys():
        pred_str = ", ".join([str(p) for p in a.predecessors])
        resource_list = [f'r{rid}({r})' for rid,r in a.resources.items() if r > 0]
        if len(resource_list) > 0:
            resource_str = ",".join(resource_list)
        else:
            resource_str = "-"
        if a.duration == 0:
            st = t
        else:
            st = t-a.duration +1

        row = [a.id,st,t,a.duration,pred_str,resource_str]
        rows += [row]

    outputpath = os.path.join(os.getcwd(),'completesol',f'j{args.n}',f"{I.id}-{q.category}.csv")
    with open(outputpath,'w') as outcsv:
        wrt = csv.writer(outcsv,delimiter=';')
        wrt.writerows(rows)

    return None

def print_partial_sol(filename:str):


    filename_list = filename.split('_')
    n_jobs = int(filename_list[0].strip('j')[:2])

    path = os.getcwd()
    folder = os.path.join(path,'data')
    sub_folder = os.path.join(folder,f"j{n_jobs}")
    folder_sol = os.path.join(path,'solutions')
    sub_folder_sol = os.path.join(folder_sol,f"j{n_jobs}")
    folder_iis = os.path.join(path,'iis')
    sub_folder_iis = os.path.join(folder_iis,f"j{n_jobs}")
    file = os.path.join(sub_folder,f"{filename}")

    P = read_instance(file)

    instance_id = f"{filename}".split('.')[0]
    I = Instance(id=instance_id,project=P)
    I.build_model()
    file_sol = os.path.join(sub_folder_sol,f"{filename}.stdout")
    I.read_solution(file_sol)

    n_queries = 11
    q_types = [i for i in range(1,n_queries+1)]

    for q_ in q_types:
        I_copy = copy.deepcopy(I)
        q = Query(id=q_,category=q_)
        iis = IIS(id=instance_id,instance=I_copy,query=q)
        iis_file = os.path.join(sub_folder_iis,f"iis-{filename}-{q_}.stdout")
        iis.read(iis_file)
        if len(iis.constraints) == 0:
            continue
        print(f"Q{q_}")
        #print_partial_sol_q(iis)
        print_complete_sol_q(iis)
        
    return None


if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('-n', type=int, default=30)
    parser.add_argument('-q', type=int, default=2)
    parser.add_argument('-f', type=str, default='j301_1.sm')
    parser.add_argument('-s', action='store_true',help='s: sequence true, graph false')
    args, additional = parser.parse_known_args()

    print_partial_sol(args.f)
