"""
Author: Roger X. Lera Leri
Date: 2025/04/28
"""


def query_1(q,I):
    """
    Why is course u planned in semester l?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    u,l = q.elements[0]
    i = var_keys[(u.id,l.id)]
    con = Constraint(id=index,category='query')
    con.elements.update({'unit':u,'semester':l,'query':q_type})
    con.scope.update({i:(u,l)})
    q.scope.update({i:(u,l)})
    model.add_constraint(x[i] == 0)
    I.constraints.update({index:con})
    I.con_keys.update({('query',u.id,l.id,q_type):index})

    return None

def query_2(q,I):
    """
    Why is course u not planned in semester l?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    u,l = q.elements[0]
    i = var_keys[(u.id,l.id)]
    con = Constraint(id=index,category='query')
    con.elements.update({'unit':u,'semester':l,'query':q_type})
    con.scope.update({i:(u,l)})
    q.scope.update({i:(u,l)})
    model.add_constraint(x[i] == 1)
    I.constraints.update({index:con})
    I.con_keys.update({('query',u.id,l.id,q_type):index})

    return None

def query_3(q,I):
    """
    Why is unit u not planned before semester l?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    L = I.course.semesters
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    u,l = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'unit':u,'semester':l,'query':q_type})
    sum_list = []
    for j in range(0,l.id - 1):
        l_ = L[j]
        i = var_keys[(u.id,l_.id)]
        con.scope.update({i:(u,l_)})
        q.scope.update({i:(u,l_)})
        sum_list += [x[i]]
    
    model.add_constraint(model.sum(sum_list) == 1)
    I.constraints.update({index:con})
    I.con_keys.update({('query',u.id,l.id,q_type):index})

    return None

def query_4(q,I):
    """
    Why is unit u not planned after semester l?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    L = I.course.semesters
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    u,l = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'unit':u,'semester':l,'query':q_type})
    sum_list = []
    for j in range(l.id,len(L)):
        l_ = L[j]
        i = var_keys[(u.id,l_.id)]
        con.scope.update({i:(u,l_)})
        q.scope.update({i:(u,l_)})
        sum_list += [x[i]]
    
    model.add_constraint(model.sum(sum_list) == 1)
    I.constraints.update({index:con})
    I.con_keys.update({('query',u.id,l.id,q_type):index})

    return None

def query_5(q,I):
    """
    Why is unit u planned?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    L = I.course.semesters
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    u,_ = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'unit':u,'query':q_type})
    sum_list = []
    for l in L:
        i = var_keys[(u.id,l.id)]
        con.scope.update({i:(u,l)})
        q.scope.update({i:(u,l)})
        sum_list += [x[i]]
    
    model.add_constraint(model.sum(sum_list) == 0)
    I.constraints.update({index:con})
    I.con_keys.update({('query',u.id,l.id,q_type):index})

    return None

def query_6(q,I):
    """
    Why is unit u not planned?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    L = I.course.semesters
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    u,_ = q.elements[0]
    con = Constraint(id=index,category='query')
    con.elements.update({'unit':u,'query':q_type})
    sum_list = []
    for l in L:
        i = var_keys[(u.id,l.id)]
        con.scope.update({i:(u,l)})
        q.scope.update({i:(u,l)})
        sum_list += [x[i]]
    
    model.add_constraint(model.sum(sum_list) == 1)
    I.constraints.update({index:con})
    I.con_keys.update({('query',u.id,l.id,q_type):index})

    return None

def query_7(q,I):
    """
    Why is the subset of units U planned at semester l?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    con = Constraint(id=index,category='query')
    sum_list = []
    sum_activities = []
    for elem in q.elements:
        u,l = elem
        i = var_keys[(u.id,l.id)]
        con.scope.update({i:(u,l)})
        q.scope.update({i:(u,l)})
        sum_list += [x[i]]
        sum_activities += [u.id]

    con.elements.update({'units':sum_activities,'semester':l.id,'query':q_type})
    len_ = len(sum_list)    
    model.add_constraint(model.sum(sum_list) <= len_ - 1)
    I.constraints.update({index:con})
    I.con_keys.update({('query',l.id,q_type):index})

    return None

def query_8(q,I):
    """
    Why is the subset of units U not planned at semester l?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    con = Constraint(id=index,category='query')
    sum_list = []
    sum_activities = []
    iter_ = 0
    for elem in q.elements:
        if iter_ == 0:
            u,l = elem
        else:
            u,_ = elem
        iter_ += 1
        i = var_keys[(u.id,l.id)]
        con.scope.update({i:(u,l)})
        q.scope.update({i:(u,l)})
        sum_list += [x[i]]
        sum_activities += [u.id]

    con.elements.update({'units':sum_activities,'semester':l.id,'query':q_type})
    len_ = len(sum_list)    
    model.add_constraint(model.sum(sum_list) == len_)
    I.constraints.update({index:con})
    I.con_keys.update({('query',l.id,q_type):index})

    return None


def query_9(q,I):
    """
    Why is unit u planned in semester l instead of unit u'?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    u,l = q.elements[0]
    u_,_ = q.elements[1]
    i = var_keys[(u.id,l.id)]
    j = var_keys[(u_.id,l.id)]
    con = Constraint(id=index,category='query')
    con.elements.update({'unit':u,'semester':l,'query':q_type})
    con.scope.update({i:(u,l)})
    q.scope.update({i:(u,l)})
    q.scope.update({j:(u_,l)})
    model.add_constraint(x[i] == 0)
    model.add_constraint(x[j] == 1)
    I.constraints.update({index:con})
    I.con_keys.update({('query',u.id,l.id,q_type):index})
    con = Constraint(id=index+1,category='query')
    con.elements.update({'unit':u_,'semester':l,'query':q_type})
    con.scope.update({j:(u_,l)})
    I.constraints.update({index+1:con})
    I.con_keys.update({('query',u_.id,l.id,q_type):index+1})

    return None

def query_10(q,I):
    """
    Why is unit u planned instead of unit u'?
    """
    from definitions import Constraint
    from formalisation import get_variables,get_var_keys
    L = I.course.semesters
    q_type = q.category
    var = I.variables
    var_keys = I.var_keys
    model = I.model
    x_vars,_,_,_,_ = get_var_keys(var)
    x = get_variables(model,'x',x_vars)
    index = len(list(I.constraints.keys()))

    u,_ = q.elements[0]
    u_,_ = q.elements[1]
    con1 = Constraint(id=index,category='query')
    con1.elements.update({'unit':u,'query':q_type})
    con2 = Constraint(id=index+1,category='query')
    con2.elements.update({'unit':u,'query':q_type})
    sum_list_1 = []
    sum_list_2 = []
    for l in L:
        i = var_keys[(u.id,l.id)]
        j = var_keys[(u_.id,l.id)]
        con1.scope.update({i:(u,l)})
        con2.scope.update({j:(u_,l)})
        q.scope.update({i:(u,l)})
        q.scope.update({j:(u_,l)})
        sum_list_1 += [x[i]]
        sum_list_2 += [x[j]]


    model.add_constraint(model.sum(sum_list_1) == 0)
    model.add_constraint(model.sum(sum_list_2) == 1)
    I.constraints.update({index:con1})
    I.con_keys.update({('query',u.id,q_type):index})
    I.constraints.update({index+1:con2})
    I.con_keys.update({('query',u_.id,q_type):index+1})

    return None


def query_transcription_(q,I):
    """
    This function encodes the queries into the model
    """
    function = globals().get(f"query_{q.category}")
    function(q,I)
    return None


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
    
    

    