

def query_1(q,I):
    """
    Why is activity j completed in time slot t?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    i = var_keys[(a.id,t)]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    con.scope.update({i:(a,t)})
    q.scope.update({i:(a,t)})
    model.add_constraint(x[i] == 0)
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
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    i = var_keys[(a.id,t)]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    con.scope.update({i:(a,t)})
    q.scope.update({i:(a,t)})
    model.add_constraint(x[i] == 1)
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
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    sum_list = []
    for t_ in range(a.ef_time,t):
        i = var_keys[(a.id,t_)]
        con.scope.update({i:(a,t_)})
        q.scope.update({i:(a,t_)})
        sum_list += [x[i]]
    
    model.add_constraint(model.sum(sum_list) == 1)
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
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    sum_list = []
    for t_ in range(t+1,a.lf_time + 1):
        i = var_keys[(a.id,t_)]
        con.scope.update({i:(a,t_)})
        q.scope.update({i:(a,t_)})
        sum_list += [x[i]]
    
    model.add_constraint(model.sum(sum_list) == 1)
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
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))

    con = Constraint(id=index,category='query')
    sum_list = []
    sum_activities = []
    for elem in q.elements:
        a,t = elem
        i = var_keys[(a.id,t)]
        con.scope.update({i:(a,t)})
        q.scope.update({i:(a,t)})
        sum_list += [x[i]]
        sum_activities += [a.id]

    con.elements.update({'activities':sum_activities,'t':t,'query':q_type})
    len_ = len(sum_list)    
    model.add_constraint(model.sum(sum_list) <= len_ - 1)
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
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))

    con = Constraint(id=index,category='query')
    sum_list = []
    sum_activities = []
    t = q.elements[0][1]
    for elem in q.elements:
        a,_ = elem
        i = var_keys[(a.id,t)]
        con.scope.update({i:(a,t)})
        q.scope.update({i:(a,t)})
        sum_list += [x[i]]
        sum_activities += [a.id]

    con.elements.update({'activities':sum_activities,'t':t,'query':q_type})
    len_ = len(sum_list)    
    model.add_constraint(model.sum(sum_list) == len_)
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
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))
    index_var = len(keys)

    
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
        sum_list = []
        for a in sum_activities_ob:
            i = var_keys[(a.id,t)]
            con.scope.update({i:(a,t)})
            q.scope.update({i:(a,t)})
            sum_list += [x[i]]
        len_ = len(sum_list)    
        model.add_constraint(model.sum(sum_list) <= len_ - 1)
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
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))
    index_var = len(keys)

    
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

    l = model.binary_var_dict(keys_l,name='l')

    for t in range(max_ef,min_lf+1):
        j_con = index + t - max_ef
        con = Constraint(id=j_con,category='query')
        con.elements.update({'activities':sum_activities,'t':t,'query':q_type})
        sum_list = []
        for a in sum_activities_ob:
            i = var_keys[(a.id,t)]
            con.scope.update({i:(a,t)})
            q.scope.update({i:(a,t)})
            sum_list += [x[i]]
        
        con.scope.update({j:(t)})
        q.scope.update({j:(t)})  
        len_ = len(sum_list)  
        model.add_constraint(model.sum(sum_list) == len_ * l[t])
        I.constraints.update({j_con:con})
        I.con_keys.update({('query',t,q_type):j_con})

    con = Constraint(id=j_con + 1,category='query')
    con.elements.update({'activities':[],'t':t,'query':q_type})
    model.add_constraint(model.sum(l[t] for t in range(max_ef,min_lf+1)) == 1)

    return None

def query_9(q,I):
    """
    Why is activity j completed in time slot t instead of time slot t'?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    a,t_ = q.elements[1]
    i = var_keys[(a.id,t_)]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'t_':t_,'query':q_type})
    con.scope.update({i:(a,t_)})
    q.scope.update({i:(a,t_)})
    model.add_constraint(x[i] == 1)
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
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))

    a,t = q.elements[0]
    a_,t_ = q.elements[1]
    i = var_keys[(a.id,t)]
    con = Constraint(id=index,category='query')
    con.elements.update({'activity':a,'t':t,'query':q_type})
    con.scope.update({i:(a,t)})
    q.scope.update({i:(a,t)})
    model.add_constraint(x[i] == 0)
    I.constraints.update({index:con})
    I.con_keys.update({('query',a.id,t,q_type):index})

    i = var_keys[(a_.id,t)]
    con = Constraint(id=index+1,category='query')
    con.elements.update({'activity':a_,'t':t,'query':q_type})
    con.scope.update({i:(a_,t)})
    q.scope.update({i:(a_,t)})
    model.add_constraint(x[i] == 1)
    I.constraints.update({index+1:con})
    I.con_keys.update({('query',a_.id,t,q_type):index+1})

    return None

def query_11(q,I):
    """
    Why are not {more, less, equal, not equal} than n_t activities in time slot t?
    """
    from definitions import Constraint
    from formalisation import get_variables
    q_type = q.category
    var = I.variables
    keys = list(var.keys())
    var_keys = I.var_keys
    model = I.model
    x = get_variables(model,'x',keys)
    index = len(list(I.constraints.keys()))

    type_,t,n_t = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'n':n_t,'t':t,'query':q_type})
    sum_list = []
    for a in I.project.activities:
        if a.ef_time <= t and a.lf_time >= t:
            i = var_keys[(a.id,t)]
            con.scope.update({i:(a,t)})
            q.scope.update({i:(a,t)})
            sum_list += [x[i]]
    
    if type_ == 'more':
        model.add_constraint(model.sum(sum_list) <= n_t)
        I.constraints.update({index:con})
        I.con_keys.update({('query',t,n_t,type_,q_type):index})
    elif type_ == 'less':
        model.add_constraint(model.sum(sum_list) >= n_t)
        I.constraints.update({index:con})
        I.con_keys.update({('query',t,n_t,type_,q_type):index})
    elif type_ == 'not equal':
        model.add_constraint(model.sum(sum_list) == n_t)
        I.constraints.update({index:con})
        I.con_keys.update({('query',t,n_t,type_,q_type):index})
    elif type_ == 'equal':
        I.constraints.update({index:con})
        I.con_keys.update({('query',t,n_t,type_,q_type):index})
        con_ = Constraint(id=index+1,category='query')
        con_.elements = con.elements
        con_.scope = con.scope
        I.constraints.update({index+1:con_})
        I.con_keys.update({('query',t,n_t,type_,q_type):index+1})

        l = model.binary_var_dict(['m','l'],name='l')
        con_2 = Constraint(id=index+2,category='query')
        I.constraints.update({index+2:con_2})
        I.con_keys.update({('query',t,n_t,type_,q_type):index+2})
        
        model.add_constraint(model.sum(sum_list) <= (n_t - 1)*l['l'])
        model.add_constraint(model.sum(sum_list) >= (n_t + 1)*l['m'])
        model.add_constraint(l['l'] + l['m'] == 1)
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

    