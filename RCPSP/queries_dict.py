
import numpy as np


def query_1(q,I):
    """
    Why is activity j completed in time slot t?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    i = var_keys[(a.id,t)]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    con.scope.update({i:(a,t)})
    q.scope.update({i:(a,t)})

    con.ind += [i]
    con.lhs += [1]
    con.rhs = 0
    con.rel = '=='
    I.constraints.update({index:con})
    I.con_keys.update({('query',a.id,t,q_type):index})

    return None

def query_2(q,I):
    """
    Why is activity j not completed in time slot t?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    i = var_keys[(a.id,t)]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    con.scope.update({i:(a,t)})
    q.scope.update({i:(a,t)})

    con.ind += [i]
    con.lhs += [1]
    con.rhs = 1
    con.rel = '=='
    I.constraints.update({index:con})
    I.con_keys.update({('query',a.id,t,q_type):index})

    return None

def query_3(q,I):
    """
    Why is activity j not completed before time slot t?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    for t_ in range(a.ef_time,t):
        i = var_keys[(a.id,t_)]
        con.scope.update({i:(a,t_)})
        q.scope.update({i:(a,t_)})
        con.ind += [i]
        con.lhs += [1]

    con.rhs = 1
    con.rel = '=='
    I.constraints.update({index:con})
    I.con_keys.update({('query',a.id,t,q_type):index})

    return None

def query_4(q,I):
    """
    Why is activity j not completed after time slot t?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    for t_ in range(t+1,a.lf_time + 1):
        i = var_keys[(a.id,t_)]
        con.scope.update({i:(a,t_)})
        q.scope.update({i:(a,t_)})
        con.ind += [i]
        con.lhs += [1]
    
    con.rhs = 1
    con.rel = '=='
    I.constraints.update({index:con})
    I.con_keys.update({('query',a.id,t,q_type):index})

    return None

def query_5(q,I):
    """
    Why is the subset of activities A completed in time slot t?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))

    con = Constraint(id=index,category='query')
    sum_activities = []
    for elem in q.elements:
        a,t = elem
        i = var_keys[(a.id,t)]
        con.scope.update({i:(a,t)})
        q.scope.update({i:(a,t)})
        con.ind += [i]
        con.lhs += [1]
        sum_activities += [a.id]

    con.elements.update({'activities':sum_activities,'t':t,'query':q_type})
    len_ = np.sum(con.lhs) 
    con.rhs = len_ - 1
    con.rel = '<='
    I.constraints.update({index:con})
    I.con_keys.update({('query',t,q_type):index})

    return None

def query_6(q,I):
    """
    Why is the subset of activities A not completed in time slot t?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))

    con = Constraint(id=index,category='query')
    sum_activities = []
    t = q.elements[0][1]
    for elem in q.elements:
        a,_ = elem
        i = var_keys[(a.id,t)]
        con.scope.update({i:(a,t)})
        q.scope.update({i:(a,t)})
        con.ind += [i]
        con.lhs += [1]
        sum_activities += [a.id]

    con.elements.update({'activities':sum_activities,'t':t,'query':q_type})
    len_ = np.sum(con.lhs) 
    con.rhs = len_
    con.rel = '=='
    I.constraints.update({index:con})
    I.con_keys.update({('query',t,q_type):index})

    return None

def query_7(q,I):
    """
    Why is the subset of activities A completed in the same time slot?
    """
    from definitions import Constraint,Variable
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))

    
    sum_activities = []
    sum_activities_ob = []
    max_ef = 0
    min_lf = I.project.horizon
    for elem in q.elements:
        a , t = elem
        sum_activities += [a.id]
        sum_activities_ob += [a]
        if a.ef_time > max_ef:
            max_ef = a.ef_time
        if a.lf_time < min_lf:
            min_lf = a.lf_time


    for t in range(max_ef,min_lf+1):
        j_con = index + t - max_ef
        con = Constraint(id=j_con,category='query')
        con.elements.update({'activities':sum_activities,'t':t,'query':q_type})
        for a in sum_activities_ob:
            i = var_keys[(a.id,t)]
            con.scope.update({i:(a,t)})
            q.scope.update({i:(a,t)})
            con.ind += [i]
            con.lhs += [1]
        len_ = np.sum(con.lhs) 
        
        con.rhs = len_ - 1
        con.rel = '<='  
        I.constraints.update({j_con:con})
        I.con_keys.update({('query',t,q_type):j_con})

    return None

def query_8(q,I):
    """
    Why is the subset of activities A not completed in the same time slot?
    """
    from definitions import Constraint,Variable
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))
    index_var = N

    
    sum_activities = []
    sum_activities_ob = []
    max_ef = 0
    min_lf = I.project.horizon
    for elem in q.elements:
        a , t = elem
        sum_activities += [a.id]
        sum_activities_ob += [a]
        if a.ef_time > max_ef:
            max_ef = a.ef_time
        if a.lf_time < min_lf:
            min_lf = a.lf_time

    keys_l = []
    for t in range(max_ef,min_lf+1):
        j = index_var + t - max_ef
        var_ = Variable(id=j,category='l')
        var_.elements = [t]
        I.variables.update({j:var_})
        I.var_keys.update({(t):j})
        keys_l += [t]

    
    var_keys = I.var_keys


    for t in range(max_ef,min_lf+1):
        j = index_var + t - max_ef
        j_con = index + t - max_ef
        con = Constraint(id=j_con,category='query')
        con.elements.update({'activities':sum_activities,'t':t,'query':q_type})
        for a in sum_activities_ob:
            i = var_keys[(a.id,t)]
            con.scope.update({i:(a,t)})
            q.scope.update({i:(a,t)})
            con.ind += [i]
            con.lhs += [1]
        
        con.scope.update({j:(t)})
        q.scope.update({j:(t)})  
        len_ = np.sum(con.lhs)
        con.ind += [j]
        con.lhs += [-1*len_]
        con.rhs = 0
        con.rel = '=='  
        I.constraints.update({j_con:con})
        I.con_keys.update({('query',t,q_type):j_con})

    con = Constraint(id=j_con + 1,category='query')
    con.elements.update({'activities':[],'t':t,'query':q_type})

    for t in range(max_ef,min_lf+1):
        j = index_var + t - max_ef
        con.ind += [j]
        con.lhs += [1]

    con.rhs = 1
    con.rel = '=='  
    I.constraints.update({j_con+1:con})
    I.con_keys.update({('query',t,q_type):j_con+1})
    return None

def query_9(q,I):
    """
    Why is activity j completed in time slot t instead of time slot t'?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    a,t_ = q.elements[1]
    i = var_keys[(a.id,t_)]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'t_':t_,'query':q_type})
    con.scope.update({i:(a,t_)})
    q.scope.update({i:(a,t_)})
    con.ind += [i]
    con.lhs += [1]
    
    con.rhs = 1
    con.rel = '=='
    
    I.constraints.update({index:con})
    I.con_keys.update({('query',a.id,t,t_,q_type):index})

    return None

def query_10(q,I):
    """
    Why is activity j completed in time slot t instead of activity j'?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    var_keys = I.var_keys
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    a_,t_ = q.elements[1]
    i = var_keys[(a.id,t)]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    con.scope.update({i:(a,t)})
    q.scope.update({i:(a,t)})
    con.ind += [i]
    con.lhs += [1]
    con.rhs = 0
    con.rel = '=='
    I.constraints.update({index:con})
    I.con_keys.update({('query',a.id,t,q_type):index})

    i = var_keys[(a_.id,t)]
    con = Constraint(id=index+1,category='query')
    con.elements.update({'activity':a_,'t':t,'query':q_type})
    con.scope.update({i:(a_,t)})
    q.scope.update({i:(a_,t)})
    con.ind += [i]
    con.lhs += [1]
    con.rhs = 1
    con.rel = '=='
    I.constraints.update({index+1:con})
    I.con_keys.update({('query',a_.id,t,q_type):index+1})

    return None

def query_11(q,I):
    """
    Why are not {more, less, equal, not equal} than n_t activities in time slot t?
    """
    from definitions import Constraint,Variable
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    N = len(var)
    index_var = N
    index = len(list(I.constraints.keys()))

    type_,t,n_t = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'n':n_t,'t':t,'query':q_type})

    if type_ == 'equal':
        newvar_1 = Variable(id=index_var,category='l')
        newvar_1.elements = [11,'l']
        I.variables.update({N:newvar_1})
        I.var_keys.update({(11,'l'):N})
        newvar_2 = Variable(id=index_var+1,category='l')
        newvar_2.elements = [11,'m']
        I.variables.update({N+1:newvar_2})
        I.var_keys.update({(11,'m'):N+1})
        

    var_keys = I.var_keys

    for a in I.project.activities:
        if a.ef_time <= t and a.lf_time >= t:
            i = var_keys[(a.id,t)]
            con.scope.update({i:(a,t)})
            q.scope.update({i:(a,t)})
            con.ind += [i]
            con.lhs += [1]
    
    if type_ == 'more':
        con.rhs = n_t
        con.rel = '<='
        I.constraints.update({index:con})
        I.con_keys.update({('query',t,n_t,type_,q_type):index})
    elif type_ == 'less':
        con.rhs = n_t
        con.rel = '>='
        I.constraints.update({index:con})
        I.con_keys.update({('query',t,n_t,type_,q_type):index})
    elif type_ == 'not equal':
        con.rhs = n_t
        con.rel = '=='
        I.constraints.update({index:con})
        I.con_keys.update({('query',t,n_t,type_,q_type):index})
    elif type_ == 'equal':

        con.ind += [index_var]
        con.lhs += [n_t - 1]
        con.rhs = 0
        con.rel = '<='
        I.constraints.update({index:con})
        I.con_keys.update({('query',t,n_t,type_,q_type):index})
        

        con_ = Constraint(id=index+1,category='query')
        con_.elements = con.elements
        con_.scope = con.scope
        con_.ind += [index_var+1]
        con_.lhs += [n_t + 1]
        con_.rhs = 0
        con_.rel = '>='
        I.constraints.update({index+1:con_})
        I.con_keys.update({('query',t,n_t,type_,q_type):index+1})

        con_2 = Constraint(id=index+2,category='query')
        con_2.ind += [index_var,index_var+1]
        con_2.lhs += [1,1]
        con_2.rhs = 1
        con_2.rel = '=='
        I.constraints.update({index+2:con_2})
        I.con_keys.update({('query',t,n_t,type_,q_type):index+2})
    else:
        raise ValueError(f"Type of query {q_type} ({type_}) does not belong to any type.")

    return None



def query_transcription_(q,I):
    """
    This function encodes the queries into the model
    """
    function = globals().get(f"query_{q.category}")
    function(q,I)


if __name__ == '__main__':
    
    import argparse as ap
    import os
    print('Query translation')
    parser = ap.ArgumentParser()
    parser.add_argument('-n', type=int, default=30, help='n: Number of activities')
    parser.add_argument('-s', type=int, default=60, help='s: Time limit in seconds')
    parser.add_argument('-q', type=int, default=1, help='q: Query type')
    parser.add_argument('-f', type=str, default = 'j301_1.sm', help='filename of the instance')
    args = parser.parse_args()
    
    path = os.getcwd()
    folder = os.path.join(path,'data')
    sub_folder = os.path.join(folder,f"j{args.n}")
    file = os.path.join(sub_folder,f"{args.f}")
    
    from read_files import read_instance
    P = read_instance(file)

    from definitions import Instance
    I = Instance(id=0,project=P)
    I.build_model()
    folder = os.path.join(path,'solutions')
    sub_folder = os.path.join(folder,f"j{args.n}")
    file = os.path.join(sub_folder,f"{args.f}.stdout")
    I.read_solution(file)
    from generate_query import query_generation
    Q = query_generation(I,11)
    for q in Q:
        q.query_transcription(I)
        for key,item in q.scope.items():
            print(item[0].id,item[1])

    