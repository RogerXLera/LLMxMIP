
import json
import os
import numpy as np


def change_mode(line:str):
    sep_ = "****************************" 
    if line[:len(sep_)] == sep_:
        return True
    else:
        return False

def line_mode(line:str):
    
    modes = ['projects']
    modes += ['PROJECT INFORMATION']
    modes += ['PRECEDENCE RELATIONS']
    modes += ['REQUESTS/DURATIONS']
    modes += ['RESOURCEAVAILABILITIES']
    section_ = line.split(':')[0]
    if section_ in modes:
        return section_
    elif section_.split(' ')[0] == 'projects':
        return 'projects'
    else:
        return ''

def proj(P, line:str):
    trigger = 'horizon'
    if line[:len(trigger)] == trigger:
        horizon = int(line.split(':')[1])
        P.horizon = horizon

def p_info(P, line: str,len_ : int = 6):
    split_ = line.split(' ')
    ints = []
    for el in split_:
        try:
            ints += [int(el)]
        except ValueError:
            continue

    if len(ints) == len_:
        P.makespan_ub = ints[3]
    return None

def prec_rel(A,line: str,len_ : int = 3):
    split_ = line.split(' ')
    ints = []
    for el in split_:
        try:
            ints += [int(el)]
        except ValueError:
            continue

    from definitions import Activity
    if len(ints) >= len_:
        a = Activity(id=ints[0],duration=0)
        n_succ = ints[2]
        a.successors = [ints[3+i] for i in range(n_succ)]
        A += [a]
    return None

def req_dur(A,line: str,len_ : int = 3):
    split_ = line.split(' ')
    ints = []
    str_counter = 0
    for el in split_:
        try:
            ints += [int(el)]
        except ValueError:
            if el != '':
                str_counter += 1

    if len(ints) > len_ and str_counter <= len_:
        
        a = A[ints[0]-1]
        a.duration = ints[2]
        for i in range(len_,len(ints)):
            a.resources.update({i-len_+1:ints[i]})

    return None

def resources(R,line: str):
    split_ = line.split(' ')
    ints = []
    r_counter = 0
    from definitions import Resource
    for el in split_:
        try:
            ints += [int(el)]
        except ValueError:
            if el == 'R':
                r_counter += 1
            continue

    if r_counter == 0:
        R += [Resource(id=i+1,units=ints[i]) for i in range(len(ints))]

    return None

def read_line(P,line:str,mode:str,det_mode:bool):
    
    if change_mode(line):
        mode = ''
        det_mode = True
        return mode,det_mode
    elif det_mode:
        mode = line_mode(line)
        det_mode = False
        return mode,det_mode
    else:
        #print(f'line: {mode} ; {det_mode}')
        if mode == 'projects':
            proj(P, line)
        elif mode == 'PROJECT INFORMATION':
            p_info(P, line)
        elif mode == 'PRECEDENCE RELATIONS':
            prec_rel(P.activities, line)
        elif mode == 'REQUESTS/DURATIONS':
            req_dur(P.activities, line)
        elif mode == 'RESOURCEAVAILABILITIES':
            resources(P.resources, line)

        return mode,det_mode

def add_predecessors(A):
    for a in A:
        for i in a.successors:
            succ = A[i-1]
            succ.predecessors += [a.id]

def add_earliest_finishing(A):
    """
        This function adds the earliest finishing time of the activities
    """
    for a in A:
        latest_predecessor = 0
        for i in a.predecessors:
            pred = A[i-1]
            if pred.ef_time > latest_predecessor:
                latest_predecessor = pred.ef_time
        a.ef_time = latest_predecessor + a.duration
    return None

def add_latest_finishing(A,upper_bound: int):
    """
        This function adds the earliest finishing time of the activities
    """
    for i in range(len(A),0,-1):
        a = A[i-1]
        latest_successor = upper_bound
        for j in a.successors:
            succ = A[j-1]
            if succ.lf_time - succ.duration < latest_successor:
                latest_successor = succ.lf_time - succ.duration
        a.lf_time = latest_successor
    return None


def read_instance(filepath):
    """
    This function reads a generic file containing the info of the instance
    and it stores it in objects. 
    """
    from definitions import Project
    A = []
    R = []
    P = Project(id=1)
    with open(filepath,'r') as inputfile:
        data = inputfile.readlines()
        det_mode = False
        mode = ""
        for line in data:
            mode,det_mode = read_line(P,line[:-1],mode,det_mode)
    
    add_predecessors(P.activities)
    add_earliest_finishing(P.activities)
    add_latest_finishing(P.activities,P.horizon)

    return P

def read_solution_file(file_path):
    
    solution = {}
    f = 0.0
    t = 0.0
    with open(file_path, 'r') as f:
        data = f.readlines()
        for row in data:
            if "Activity" in row: #process activities
                activity = row.split("Activity: ")[1]
                activity_id = activity.split(" ")[0]
                time = row.split("t: ")[1]
                time_id = time.split(" ")[0]
                solution.update({int(activity_id):[int(time_id)]})
            elif "Objective" in row:
                objective = row.split("Objective value: ")[1]
                f = float(objective.split(" ")[0])
            elif "Solving" in row:
                time_ = row.split("Solving time: ")[1]
                t = float(time_.split(" ")[0])

    return solution,f,t


if __name__ == '__main__':
    
    path = os.getcwd()
    folder = os.path.join(path,'data')
    file = os.path.join(folder,'j30','j3016_7.sm')
    
    P = read_instance(file)

    counter = 0
    for a in P.activities:
        counter += a.duration
        print(f"{a}, {a.duration}")
    
    print(f"Total Duration: {counter}")

    
    
    
    
    
    
    
    
    

    