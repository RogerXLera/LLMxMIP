import numpy as np
import json
import pandas as pd

def translate_to_reasons(IIS,f,n,df_c):

    I = IIS.instance
    con = IIS.constraints
    non_query_con = {c:cob for c,cob in con.items() if cob.category != 'query'}
    q = IIS.query
    
    tranlations = {'query':q.translate(df_c)}
    for c,cob in non_query_con.items():
        tranlations.update({cob.name():cob.translate(df_c)})

    filepath = os.path.join(os.getcwd(),'reasons',f'j{n}',f"{f}-{q.category}")

    with open(f"{filepath}-translation.json",'w') as jsonf:
        json.dump(tranlations,jsonf)

    return None

def translate_query(q,f:str,n:int=30):

    path = os.getcwd()
    folder = os.path.join(path,'queries')
    sub_folder = os.path.join(folder,f"j{n}")
    file_instance = os.path.join(sub_folder,f"{f}-q{q.category}.txt")
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

if __name__ == '__main__':
    
    import argparse as ap
    import os
    parser = ap.ArgumentParser()
    parser.add_argument('-n', type=int, default=30, help='n: Number of activities')
    parser.add_argument('-f', type=str, default = 'j301_1.sm', help='filename of the instance')
    args = parser.parse_args()
    
    J = [30]
    path_to_data = os.path.join(os.getcwd(),'data')
    
    for j in J:
        jdata = os.path.join(path_to_data,f'j{j}')
        counter = 1
        for f in os.listdir(jdata):
            print(counter,f)
            if f[-1] == 'z': #ignore .gz files
                continue             
            write_reasons_iis(f,j)
            counter += 1
    
    
    #write_reasons_iis(args.f,args.n)