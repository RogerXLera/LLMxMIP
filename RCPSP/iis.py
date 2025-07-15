
import numpy as np

def maximality_constraint(IIS,e:float = 0.0):
    """
        This function builds the maximality constraint
    """
    from definitions import Constraint
    from formalisation import get_variables
    I = IIS.instance
    P = I.project
    a_J = P.activities[-1]
    f_value = I.objective_value + e
    var = I.variables
    N = len(var)

    index = len(list(I.constraints.keys()))

    array_ = np.zeros(N)
    con = Constraint(id=index,category='max')
    con.elements.update({'f':f_value,'objective':'max'})
    for t in range(a_J.ef_time,a_J.lf_time+1):
        j = I.var_keys[(a_J.id,t)]
        con.scope.update({j:(a_J,t)})
        con.ind += [j]
        con.lhs += [t]


    # we add the maximality constraint
    # since we aim to minimise, sum has to be lower than f^*
    con.rhs = f_value
    con.rel = '<='
    I.constraints.update({index:con})
    I.con_keys.update({('max',f_value):index})
    return None

def compute_IIS(IIS):
    
    from formalisation import get_variables
    from docplex.mp.model import Model
    from cplex.exceptions import CplexSolverError
    import time
    I = IIS.instance
    mdl = Model()
    var = I.variables
    keys = list(var.keys())
    cons = I.constraints
    constraint_keys = cons.keys()
    
    x = mdl.binary_var_dict(keys,name='x')

    for c in constraint_keys:
        
        con = cons[c]
        
        if con.rel == '<=':
            mdl.add_constraint(mdl.sum(con.lhs[i]*x[con.ind[i]] for i in range(len(con.lhs)))
                                  <= con.rhs )
        
        elif con.rel == '>=':
            mdl.add_constraint(mdl.sum(con.lhs[i]*x[con.ind[i]] for i in range(len(con.lhs)))
                                  >= con.rhs )
            
        elif con.rel == '==':
            mdl.add_constraint(mdl.sum(con.lhs[i]*x[con.ind[i]] for i in range(len(con.lhs)))
                                  == con.rhs )

    
    # Extract the IISs
    st_time = time.time()
    cplex_model = mdl.get_cplex()
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
    A = I.project.activities
    
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
            list_ = array_[0].split(',')
            if q.category == 11:
                q.elements += [[list_[0],int(list_[1]),int(list_[2])]]
            else:
                a = A[int(list_[0])-1]
                q.elements += [[a,int(list_[1])]]

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
    parser.add_argument('-n', type=int, default=30, help='n: Number of activities')
    parser.add_argument('--time', type=int, default=60, help='s: Time limit in seconds')
    parser.add_argument('--threads', type=int, default=1, help='threads: number of threads')
    parser.add_argument('-q', type=int, default=1, help='q: Query type')
    parser.add_argument('-e', type=float, default=0.0, help='e: Optimality epsylon')
    parser.add_argument('-f', type=str, default = 'j301_1.sm', help='filename of the instance')
    args = parser.parse_args()
    
    path = os.getcwd()
    folder = os.path.join(path,'data')
    sub_folder = os.path.join(folder,f"j{args.n}")
    file = os.path.join(sub_folder,f"{args.f}")
    
    from read_files import read_instance
    P = read_instance(file)

    from definitions import Instance,IIS,Query
    instance_id = f"{args.f}".split('.')[0]
    I = Instance(id=instance_id,project=P)
    I.build_constraints()
    folder = os.path.join(path,'solutions')
    sub_folder = os.path.join(folder,f"j{args.n}")
    file = os.path.join(sub_folder,f"{args.f}.stdout")
    I.read_solution(file)
    q = Query(id=args.q,category=args.q)
    q_folder = os.path.join(path,'queries',f"j{args.n}")
    q_filename = os.path.join(q_folder,f"q-{args.f}-{args.q}.stdout")
    q.read(I,q_filename)
    q.query_transcription(I)
    iis = IIS(id=instance_id,instance=I,query=q)
    iis.compute(e=args.e,time_limit=args.time,n_threads=args.threads)
    iis.print_iis()
