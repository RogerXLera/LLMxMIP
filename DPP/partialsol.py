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

    header = ['subjects','semesters','credits','compulsory']
    rows = [header]
    q = IIS.query
    cons = IIS.constraints
    I = IIS.instance
    U = I.course.units
    L = I.course.semesters
    print(iis.id)

    sol = I.solution_values
    var = I.variables

    courses = {} #relevant 
    for el in q.elements:
        u,l = el
        courses.update({u.id:u})

    major = None
    for cid,c in cons.items():
        elem = c.elements
        if 'unit' in elem.keys():
            u = elem['unit']
            courses.update({u.id:u})
        if 'predecessors' in elem.keys():
            pred = elem['predecessors']
            for p in pred:
                if p in U.keys():
                    courses.update({p:U[p]})
            
        if 'major' in elem.keys():
            major = elem['major']
        if 'electives' in elem.keys():
            elec = elem['electives']['units']
            for e in elec:
                if p in U.keys():
                    courses.update({e:U[e]})

        if c.category == 'unit_skill':
            for key,var in c.scope.items():
                if len(var) == 2:
                    u,l = var
                    courses.update({u.id:u})


    seasons_dict = {'au':'Autumn','sp':'Spring'}
    # print partial sol
    for s_id,s in I.solution_values.items():
        
        
        u_id,l_id = s
        u = U[u_id]
        l = L[l_id - 1]
        
        if u.id in courses.keys():

            core_ = 'No'
            if u.core:
                core_ = 'Yes'

            row = [u.name,f"{l.id} ({seasons_dict[l.season]})",u.credits,core_]
            rows += [row]
    
    
    outputpath = os.path.join(os.getcwd(),'partialsol',f'q{q.category}',f"{IIS.id}.csv")
    with open(outputpath,'w') as outcsv:
        wrt = csv.writer(outcsv,delimiter=';')
        wrt.writerows(rows)

    return None


def print_solution(IIS):

    header = ['subjects','semesters','offered','predecessors','compulsory','preferred job skills (level)']
    rows = [header]
    q = IIS.query
    cons = IIS.constraints
    I = IIS.instance
    U = I.course.units
    L = I.course.semesters
    S = I.job.skills
    print(iis.id)
    queries_units = {}
    for el in q.elements:
        queries_units.update({el[0].id:el[0]})

    sol = I.solution_values
    var = I.variables

    courses = {} #relevant 
    for el in q.elements:
        u,l = el
        courses.update({u.id:u})

    major = None
    for cid,c in cons.items():
        elem = c.elements
        if 'unit' in elem.keys():
            u = elem['unit']
            courses.update({u.id:u})
        if 'predecessors' in elem.keys():
            pred = elem['predecessors']
            for p in pred:
                if p in U.keys():
                    courses.update({p:U[p]})
            
        if 'major' in elem.keys():
            major = elem['major']
        if 'electives' in elem.keys():
            elec = elem['electives']['units']
            for e in elec:
                if p in U.keys():
                    courses.update({e:U[e]})

        if c.category == 'unit_skill':
            for key,var in c.scope.items():
                if len(var) == 2:
                    u,l = var
                    courses.update({u.id:u})


    seasons_dict = {'au':'Autumn','sp':'Spring','sua':'Summer','sub':'Summer'}
    # print partial sol
    units_in_sol = []
    for s_id,s in I.solution_values.items():
        
        
        u_id,l_id = s
        u = U[u_id]
        l = L[l_id - 1]
        units_in_sol += [u.id]

        """
        
        if u.id in courses.keys():

            core_ = 'No'
            if u.core:
                core_ = 'Yes'

            row = [u.name,f"{l.id} ({seasons_dict[l.season]})",u.credits,core_]
            rows += [row]
        """
        offer_ = ''
        for sem in u.seasons:
            if len(offer_) > 0:
                offer_ += f', {seasons_dict[sem]}'
            else:
                offer_ += f'{seasons_dict[sem]}'

        precedence_ = ''
        for pred in u.prerequisites:
            for p in pred:
                try:
                    u_pred = U[p]
                except:
                    continue
                if len(precedence_) > 0:
                    precedence_ += f', {u_pred.name}'
                else:
                    precedence_ += f'{u_pred.name}'

        if len(precedence_) == 0:
            precedence_ = '-' 

        core_ = 'No'
        if u.core:
            core_ = 'Yes'

        skills_ = ''
        for s in u.skills.values():
            for s_r in S.values():
                if s.id == s_r.id:
                    if len(skills_) > 0:
                        skills_ += f', {s.name} ({s.level})'
                    else:
                        skills_ += f'{s.name} ({s.level})'

        if len(skills_) == 0:
            skills_ = '-' 

        row = [u.name,f"{l.id} ({seasons_dict[l.season]})",offer_,precedence_,core_,skills_]
        rows += [row]

    for u in queries_units.values():
        if u.id in units_in_sol:
            continue

        offer_ = ''
        for sem in u.seasons:
            if len(offer_) > 0:
                offer_ += f', {seasons_dict[sem]}'
            else:
                offer_ += f'{seasons_dict[sem]}'

        precedence_ = ''
        for pred in u.prerequisites:
            for p in pred:
                try:
                    u_pred = U[p]
                except:
                    continue
                if len(precedence_) > 0:
                    precedence_ += f', {u_pred.name}'
                else:
                    precedence_ += f'{u_pred.name}'

        if len(precedence_) == 0:
            precedence_ = '-' 

        core_ = 'No'
        if u.core:
            core_ = 'Yes'

        skills_ = ''
        for s in u.skills.values():
            for s_r in S.values():
                if s.id == s_r.id:
                    if len(skills_) > 0:
                        skills_ += f', {s.name} ({s.level})'
                    else:
                        skills_ += f'{s.name} ({s.level})'

        if len(skills_) == 0:
            skills_ = '-' 

        row = [u.name,f"-",offer_,precedence_,core_,skills_]
        rows += [row]
    
    outputpath = os.path.join(os.getcwd(),'completesol',f'q{q.category}',f"{IIS.id}.csv")
    with open(outputpath,'w') as outcsv:
        wrt = csv.writer(outcsv,delimiter=';')
        wrt.writerows(rows)

    return None


if __name__ == '__main__':
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
    args, additional = parser.parse_known_args()

    from read_files import read_instance
    import copy
    from definitions import *
    from reasons import job_indixes
    
    J = job_indixes()
    path_to_data = os.path.join(os.getcwd(),'data')
    iis_folder = os.path.join(os.getcwd(),'iis')
    sol_folder = os.path.join(os.getcwd(),'solutions')

    
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
                #print_partial_sol_q(iis)
                print_solution(iis)
                
    
            
