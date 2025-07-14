import numpy as np
import json
import pandas as pd
import os

def translate_to_reasons(IIS,df_c):

    I = IIS.instance
    j = I.job
    con = IIS.constraints
    non_query_con = {c:cob for c,cob in con.items() if cob.category != 'query'}
    q = IIS.query
    
    tranlations = {'query':q.translate(df_c)}
    for c,cob in non_query_con.items():
        tranlations.update({cob.name():cob.translate(I,df_c)})

    filepath = os.path.join(os.getcwd(),'reasons',f'q{q.category}',f"reasons-{IIS.id}")

    with open(f"{filepath}.json",'w') as jsonf:
        json.dump(tranlations,jsonf)

    return None

def translate_query(q,j:str,i:str):

    path = os.getcwd()
    folder = os.path.join(path,'queries')
    sub_folder = os.path.join(folder,f"{q.category}")
    file_instance = os.path.join(sub_folder,f"question-{j}-{i}.txt")
    query_templates = os.path.join(path,f"query_templates.csv")
    df_q = pd.read_csv(query_templates,delimiter=',')

    q.translate(df_q)
    with open(file_instance,'w') as fileob:
        fileob.write(f'query;{q.translation}')
    return None

def write_reasons_iis(f:str,n:int=30):

    path = os.getcwd()
    folder = os.path.join(path,'data')
    sub_folder = os.path.join(folder,f"j{n}")
    file_instance = os.path.join(sub_folder,f"{f}")
    constraint_templates = os.path.join(path,f"constraint_templates.csv")
    df_c = pd.read_csv(constraint_templates,delimiter=',')
    
    from read_files import read_instance
    P = read_instance(file_instance)

    from definitions import Instance,IIS,Query,Features,QueryFeatures
    instance_id = f"{f}".split('.')[0]
    I = Instance(id=instance_id,project=P)
    I.build_model()
    folder_sol = os.path.join(path,'solutions')
    sub_folder_sol = os.path.join(folder_sol,f"j{n}")
    file_sol = os.path.join(sub_folder_sol,f"{f}.stdout")
    I.read_solution(file_sol)
    n_queries = 10
    q_types = [i for i in range(1,n_queries+1)]
    folder_iis = os.path.join(path,'iis')
    sub_folder_iis = os.path.join(folder_iis,f"j{n}")
    import copy

    for q_ in q_types:
        I_copy = copy.deepcopy(I)
        q = Query(id=q_,category=q_)
        iis = IIS(id=instance_id,instance=I_copy,query=q)
        iis_file = os.path.join(sub_folder_iis,f"iis-{f}-{q_}.stdout")
        iis.read(iis_file)
        if iis.optimality == 'query':
            continue
        solving_time = iis.solution_time
        if len(iis.constraints) == 0:
            continue
        print(f"Q{q_}")
        translate_query(q,f,n)
        translate_to_reasons(iis,f,n,df_c)
        
    return None

def job_indixes():

    list_ = []
    with open(os.path.join(os.getcwd(),'data','job_index.txt')) as f:
        lines = f.readlines()
        for l in lines:
            list_.append(str(int(l)))

    return list_

if __name__ == '__main__':
    
    import argparse as ap
    import os
    parser = ap.ArgumentParser()
    parser.add_argument('-n', type=int, default=6, help='n')
    parser.add_argument('-c', type=int, default=240, help='c')
    parser.add_argument('-l', type=int, default=7, help='l: maximum level. Default: 7')
    parser.add_argument('-j', type=str, default='0', help='Job index')
    parser.add_argument('-s', type=str, default='au', help='Start semester')
    parser.add_argument('-q', type=int, default=1, help='q: query category')
    parser.add_argument('-i', type=int, default=1, help='i: query instance')
    parser.add_argument('--nq', type=int, default=10, help='nq: number of queries')
    parser.add_argument('--ni', type=int, default=5, help='ni: number of instances')
    args = parser.parse_args()

    from read_files import read_instance
    import copy
    from definitions import *
    
    J = job_indixes()
    path_to_data = os.path.join(os.getcwd(),'data')
    iis_folder = os.path.join(os.getcwd(),'iis')
    sol_folder = os.path.join(os.getcwd(),'solutions')

    query_templates = os.path.join(os.getcwd(),f"query_templates.csv")
    df_q = pd.read_csv(query_templates,delimiter=',')
    constraint_templates = os.path.join(os.getcwd(),f"constraint_templates.csv")
    df_c = pd.read_csv(constraint_templates,delimiter=',')
    
    for j in J:
        I = read_instance(j=j)
        I.build_model()
        I.read_solution(os.path.join(sol_folder,f"sol-{j}.stdout"))
        print(f"J:{j}")
        
        for q_ in range(1,args.nq + 1):
            for i in range(0,args.ni):
                I_copy = copy.deepcopy(I)
                q = Query(id=q_,category=q_)
                iis = IIS(id=f"{j}-{q_}-{i}",instance=I_copy,query=q)
                iis_file = os.path.join(iis_folder,f'q{q_}',f"iis-{j}-{q_}-{i}.stdout")
                iis.read(iis_file)
                q = iis.query
                if iis.optimality == 'time':
                    continue
                solving_time = iis.solution_time
                if len(iis.constraints) == 0:
                    continue
                #print(f"Q{q_}")
                translate_query(q,j,i)
                translate_to_reasons(iis,df_c)
    
    
    #write_reasons_iis(args.f,args.n)