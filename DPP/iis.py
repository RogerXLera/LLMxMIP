"""
Author: Roger X. Lera Leri
Date: 2025/04/26
"""

def maximality_constraint(IIS,e:float = 0.0):
    """
        This function builds the maximality constraint
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    I = IIS.instance
    mdl = I.model
    #_,_,_,_,w_vars = get_var_keys(I.variables)
    #w = get_variables(mdl,'w',w_vars)
    _,_,y_vars,_,_ = get_var_keys(I.variables)
    y = get_variables(mdl,'y',y_vars)
    
    S = I.job.skills
    #S = I.skills

    f_value = I.objective_value + e

    index = len(list(I.constraints.keys()))

    sum_list = []
    con = Constraint(id=index,category='max')
    con.elements.update({'f':f_value,'objective':'max'})
    for s_id,s in S.items():
        for lev in range(1,s.level+1):
            j = I.var_keys[('y',s.id,lev)]
            con.scope.update({j:('y',s,lev)})
            sum_list += [y[j]]

    # we add the maximality constraint
    # since we aim to maximise, sum has to be bigger than f^*
    mdl.add_constraint(mdl.sum(sum_list) >= f_value)
    I.constraints.update({index:con})
    I.con_keys.update({('max',f_value):index})
    return None

def compute_IIS(IIS):
    
    from formalisation import get_variables
    from cplex.exceptions import CplexSolverError
    import time
    I = IIS.instance
    model = I.model    
    
    # Extract the IISs
    st_time = time.time()
    cplex_model = model.get_cplex()
    try:
        cplex_model.conflict.refine(cplex_model.conflict.linear_constraints())
    except CplexSolverError as e:
        print("Exception raised during IIS extraction:", e)

    # Retrieve and process the IIS
    try:
        iis_constraints = cplex_model.conflict.get()
        IIS.solution_time = time.time() - st_time
        for i in range(len(iis_constraints)):
            value = iis_constraints[i]
            c = I.constraints[i]
            if value > 0.5:
                c = I.constraints[i]
                #print(f"i: {i} ; Value: {value}; Constraint: {c}")
                IIS.constraints.update({i:c})

        return None
    except:
        IIS.solution_time = time.time() - st_time
        return None

def read_iis(IIS,filename):
    """
        This function reads the IIS
    """
    num_str = [str(i) for i in range(10)]
    q = IIS.query
    I = IIS.instance
    U = I.course.units
    L = I.course.semesters
    
    with open(filename,'r') as f:
        lines = f.readlines()
    if len(lines) == 0:
        IIS.computed = False
        IIS.optimality = 'time'
        return None
    first_line = lines[0]
    if "IIS generation" in first_line:
        IIS.computed = True
    elif "query" in first_line or "Query" in first_line:
        IIS.computed = False
        IIS.optimality = 'query'
        return None
    else:
        IIS.computed = False
        IIS.optimality = 'time'
        return None

    for l in lines[1:]:
        info_type = l.split(':')[0]
        array_ = l.split(':')[1:]
        if info_type == 'Query element':
                unit_id = array_[0].split(',')[0].strip(' ')
                u = U[unit_id]
                l_id = array_[0].split(',')[1].strip(' ')
                l = L[int(l_id)-1]
                q.elements += [[u,l]]

        elif info_type == 'IIS optimality':
            index_ = array_[0].strip()
            IIS.optimality = index_
        elif info_type == 'IIS solution time':
            index_ = array_[0].strip()
            IIS.solution_time = float(index_)
        elif info_type == 'IIS Constraint':
            index_ = array_[0].strip().split(';')[0]
            IIS.constraints.update({int(index_):None})

    return None


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
    parser.add_argument('-e', type=float, default=0.0, help='e: epsylon')
    parser.add_argument('--time', type=int, default=60, help='s: Time limit in seconds')
    parser.add_argument('--threads', type=int, default=1, help='threads: number of threads')
    parser.add_argument('--conflict', type=int, default=0, help='conflict: conflict algorithm')
    parser.add_argument('--seed', type=int, default=0, help='seed')
    args = parser.parse_args()
    
    path = os.getcwd()
    folder = os.path.join(path,'solutions')

    from read_files import read_instance
    from definitions import Query,IIS
    I = read_instance(args.n,args.c,args.j,args.s,args.l)
    I.build_model()
    file = os.path.join(folder,f"sol-{args.j}.stdout")
    I.read_solution(file)
    
    qfolder = os.path.join(os.getcwd(),'queries',f'{args.q}')
    qfile = os.path.join(qfolder,f'query-{args.j}-{args.i}.txt')
    q = Query(id=args.i,category=args.q)
    q.read_query(I,qfile)
    
    iis = IIS(id=f"{args.j}-{args.q}-{args.i}",instance=I,query=q)
    iis.compute(e=args.e,time_limit=args.time,conflict_algorithm=args.conflict,n_threads=args.threads)
    iis.print_iis()
