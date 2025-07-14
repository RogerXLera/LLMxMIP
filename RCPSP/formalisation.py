
"""
In this script there are all the functions that will create the matrices and vectors
for our ILP formalisation
"""
import numpy as np
import os


def decision_variables(I):
    """
    This function returns a dictionary with all the keys of the decision variables
    """
    from definitions import Variable
    i=0
    P = I.project
    mdl = I.model
    for a in P.activities:
        for t in range(a.ef_time,a.lf_time+1):
            var = Variable(id=i,category='x')
            var.elements = [a,t]
            I.variables.update({i:var})
            I.var_keys.update({(a.id,t):i})
            i += 1

    keys = list(I.variables.keys())


    # defining variables
    x = mdl.binary_var_dict(keys,name='x')
    return None

def decision_variables_dict(I):
    """
    This function returns a dictionary with all the keys of the decision variables
    """
    from definitions import Variable
    i=0
    P = I.project
    mdl = I.model
    for a in P.activities:
        for t in range(a.ef_time,a.lf_time+1):
            var = Variable(id=i,category='x')
            var.elements = [a,t]
            I.variables.update({i:var})
            I.var_keys.update({(a.id,t):i})
            i += 1

    keys = list(I.variables.keys())
    return None

def decision_variables_lp(I):
    """
    This function returns a dictionary with all the keys of the decision variables
    """
    from definitions import Variable
    
    mdl = I.model_lp
    keys = list(I.variables.keys())

    # defining variables
    x = mdl.continuous_var_dict(keys,lb=0.0, ub=1.0,name='xc')
    return None

def get_variables(model,name: str, keys:list):
    x = {}
    for i in keys:
        x.update({i:model.get_var_by_name(f'{name}_{i}')})
    return x

def completion_contraint(I):
    """
    This function builds completion constraint
    sum_{t=EFj}^{LFj} x_{jt} = 1
    """
    from definitions import Constraint
    P = I.project
    mdl = I.model
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'x',keys)

    index = len(list(I.constraints.keys()))
    i=0
    for a in P.activities:
        con = Constraint(id=index,category='completion')
        con.elements.update({'activity':a})
        sum_list = []
        for t in range(a.ef_time,a.lf_time+1):
            con.scope.update({i:(a,t)})
            sum_list += [x[i]]
            i += 1
        
        mdl.add_constraint(mdl.sum(sum_list) == 1)
        I.constraints.update({index:con})
        I.con_keys.update({('completion',a.id):index})
        index += 1

    return None

def precedence_contraint(I):
    """
    This function builds precedence constraint
    sum_{t=EFh}^{LFh} t*x_{ht} <= sum_{t=EFh}^{LFh} t*x_{jt}
    """
    from definitions import Constraint
    P = I.project
    mdl = I.model
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'x',keys)

    index = len(list(I.constraints.keys()))
    for a in P.activities:
        for p in a.predecessors:
            pred = P.activities[p-1]
            con = Constraint(id=index,category='precedence')
            con.elements.update({'activity':a,'predecessor':pred})
            sum_list_p = []
            for t in range(pred.ef_time,pred.lf_time+1):
                h = I.var_keys[(pred.id,t)]
                con.scope.update({h:(pred,t)})
                sum_list_p += [t*x[h]]

            sum_list_a = []
            for t in range(a.ef_time,a.lf_time+1):
                j = I.var_keys[(a.id,t)]
                con.scope.update({j:(a,t)})
                sum_list_a += [(t-a.duration)*x[j]]
                
        
            mdl.add_constraint(mdl.sum(sum_list_p) <= mdl.sum(sum_list_a))
            I.constraints.update({index:con})
            I.con_keys.update({('precedence',a.id,pred.id):index})
            index += 1

    return None


def renewable_contraint(I):
    """
    This function builds renewable constraint
    sum_{j=1}^{J} k_{jr} sum_{q=max(t,EFj)}^{min(t+d_j-1,LFj)} x_{jq} <= Kr
    """
    from definitions import Constraint
    P = I.project
    R = P.resources
    T = P.horizon
    mdl = I.model
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'x',keys)

    index = len(list(I.constraints.keys()))
    for r in R:
        if r.renewable:
            av_r = r.units
            for t in range(T):
                con = Constraint(id=index,category='renewable')
                con.elements.update({'resource':r,'t':t})
                sum_list = []

                for a in P.activities:
                    units_ = a.resources[r.id]
                    if units_ == 0:
                        continue
                    min_ = min(t+a.duration-1, a.lf_time)
                    max_ = max(t,a.ef_time)
                    for t_ in range(max_,min_+1):
                        j = I.var_keys[(a.id,t_)]
                        con.scope.update({j:(a,t_)})
                        sum_list += [units_*x[j]]
                
        
                mdl.add_constraint(mdl.sum(sum_list) <= av_r)
                I.constraints.update({index:con})
                I.con_keys.update({('renewable',r.id,t):index})
                index += 1

    return None

def nonrenewable_contraint(I):
    """
    This function builds nonrenewable constraint
    sum_{j=1}^{J} k_{jr} sum_{t=EF}^{LFj} x_{jt} <= Kr
    """
    from definitions import Constraint
    P = I.project
    R = P.resources
    A = P.activities
    mdl = I.model
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'x',keys)

    index = len(list(I.constraints.keys()))
    for r in R:
        if r.nonrenewable:
            av_r = r.units
            con = Constraint(id=index,category='nonrenewable')
            con.elements.update({'resource':r})
            sum_list = []
            for a in P.activities:
                units_ = a.resources[r.id]
                for t in range(a.ef_time,a.lf_time+1):
                    j = I.var_keys[(a.id,t)]
                    con.scope.update({j:(a,t)})
                    sum_list += [units_*x[j]]
            
        
                mdl.add_constraint(mdl.sum(sum_list) <= av_r)
                I.constraints.update({index:con})
                I.con_keys.update({('nonrenewable',r.id):index})
                index += 1

    return None

def constraint_generation(I):
    """
    This function returns a dictionary with all the constraints
    """
    
    completion_contraint(I)
    precedence_contraint(I)
    renewable_contraint(I)
    nonrenewable_contraint(I)

    return None

def completion_contraint_lp(I):
    """
    This function builds completion constraint
    sum_{t=EFj}^{LFj} x_{jt} = 1
    """
    from definitions import Constraint
    P = I.project
    mdl = I.model_lp
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'xc',keys)

    i=0
    for a in P.activities:
        sum_list = []
        for t in range(a.ef_time,a.lf_time+1):
            sum_list += [x[i]]
            i += 1
        
        mdl.add_constraint(mdl.sum(sum_list) == 1)

    return None

def precedence_contraint_lp(I):
    """
    This function builds precedence constraint
    sum_{t=EFh}^{LFh} t*x_{ht} <= sum_{t=EFh}^{LFh} t*x_{jt}
    """
    from definitions import Constraint
    P = I.project
    mdl = I.model_lp
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'xc',keys)

    for a in P.activities:
        for p in a.predecessors:
            pred = P.activities[p-1]
            sum_list_p = []
            for t in range(pred.ef_time,pred.lf_time+1):
                h = I.var_keys[(pred.id,t)]
                sum_list_p += [t*x[h]]

            sum_list_a = []
            for t in range(a.ef_time,a.lf_time+1):
                j = I.var_keys[(a.id,t)]
                sum_list_a += [(t-a.duration)*x[j]]
                
        
            mdl.add_constraint(mdl.sum(sum_list_p) <= mdl.sum(sum_list_a))

    return None


def renewable_contraint_lp(I):
    """
    This function builds renewable constraint
    sum_{j=1}^{J} k_{jr} sum_{q=max(t,EFj)}^{min(t+d_j-1,LFj)} x_{jq} <= Kr
    """
    from definitions import Constraint
    P = I.project
    R = P.resources
    T = P.horizon
    mdl = I.model_lp
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'xc',keys)

    for r in R:
        if r.renewable:
            av_r = r.units
            for t in range(T):
                sum_list = []

                for a in P.activities:
                    units_ = a.resources[r.id]
                    min_ = min(t+a.duration-1, a.lf_time)
                    max_ = max(t,a.ef_time)
                    for t_ in range(max_,min_+1):
                        j = I.var_keys[(a.id,t_)]
                        sum_list += [units_*x[j]]
                
        
                mdl.add_constraint(mdl.sum(sum_list) <= av_r)

    return None

def nonrenewable_contraint_lp(I):
    """
    This function builds nonrenewable constraint
    sum_{j=1}^{J} k_{jr} sum_{t=EF}^{LFj} x_{jt} <= Kr
    """
    from definitions import Constraint
    P = I.project
    R = P.resources
    A = P.activities
    mdl = I.model_lp
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'xc',keys)

    
    for r in R:
        if r.nonrenewable:
            av_r = r.units
            sum_list = []
            for a in P.activities:
                units_ = a.resources[r.id]
                for t in range(a.ef_time,a.lf_time+1):
                    j = I.var_keys[(a.id,t)]
                    sum_list += [units_*x[j]]
            
                mdl.add_constraint(mdl.sum(sum_list) <= av_r)

    return None

def constraint_generation_lp(I):
    """
    This function returns a dictionary with all the constraints
    """
    
    completion_contraint_lp(I)
    precedence_contraint_lp(I)
    renewable_contraint_lp(I)
    nonrenewable_contraint_lp(I)

    return None

def objective_generation(I):
    """
    This function creates the objective function
    """
    from definitions import Objective
    P = I.project
    a_J = P.activities[-1]
    mdl = I.model
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'x',keys)
    
    sum_list = []
    ob = Objective(id=1)
    for t in range(a_J.ef_time,a_J.lf_time+1):
        j = I.var_keys[(a_J.id,t)]
        ob.scope.update({j:(a_J,t)})
        sum_list += [t*x[j]]

    mdl.minimize(mdl.sum(sum_list))
    I.objective = ob

    return None

def objective_generation_lp(I):
    """
    This function creates the objective function
    """
    from definitions import Objective
    P = I.project
    a_J = P.activities[-1]
    mdl = I.model_lp
    var = I.variables
    keys = list(var.keys())
    x = get_variables(mdl,'xc',keys)
    
    sum_list = []
    for t in range(a_J.ef_time,a_J.lf_time+1):
        j = I.var_keys[(a_J.id,t)]
        sum_list += [t*x[j]]

    mdl.minimize(mdl.sum(sum_list))

    return None

def completion_contraint_dict_old(I):
    """
    This function builds completion constraint
    sum_{t=EFj}^{LFj} x_{jt} = 1
    """
    from definitions import Constraint
    P = I.project
    var = I.variables
    N = len(var)

    index = len(list(I.constraints.keys()))
    i=0
    for a in P.activities:
        con = Constraint(id=index,category='completion')
        con.elements.update({'activity':a})
        array_ = np.zeros(N,dtype=np.int8)
        for t in range(a.ef_time,a.lf_time+1):
            con.scope.update({i:(a,t)})
            array_[i] = 1
            i += 1

        con.lhs = array_
        con.rhs = 1
        con.rel = '=='
        I.constraints.update({index:con})
        I.con_keys.update({('completion',a.id):index})
        index += 1

    return None

def precedence_contraint_dict_old(I):
    """
    This function builds precedence constraint
    sum_{t=EFh}^{LFh} t*x_{ht} <= sum_{t=EFh}^{LFh} t*x_{jt}
    """
    from definitions import Constraint
    P = I.project
    var = I.variables
    N = len(var)

    index = len(list(I.constraints.keys()))
    for a in P.activities:
        for p in a.predecessors:
            pred = P.activities[p-1]
            con = Constraint(id=index,category='precedence')
            con.elements.update({'activity':a,'predecessor':pred})
            array_ = np.zeros(N)
            for t in range(pred.ef_time,pred.lf_time+1):
                h = I.var_keys[(pred.id,t)]
                con.scope.update({h:(pred,t)})
                array_[h] = t

            for t in range(a.ef_time,a.lf_time+1):
                j = I.var_keys[(a.id,t)]
                con.scope.update({j:(a,t)})
                array_[j] = -1*(t-a.duration)

            con.lhs = array_
            con.rhs = 0
            con.rel = '<='
            I.constraints.update({index:con})
            I.con_keys.update({('precedence',a.id,pred.id):index})
            index += 1

    return None


def renewable_contraint_dict_old(I):
    """
    This function builds renewable constraint
    sum_{j=1}^{J} k_{jr} sum_{q=max(t,EFj)}^{min(t+d_j-1,LFj)} x_{jq} <= Kr
    """
    from definitions import Constraint
    P = I.project
    R = P.resources
    T = P.horizon
    var = I.variables
    N = len(var)

    index = len(list(I.constraints.keys()))
    for r in R:
        if r.renewable:
            av_r = r.units
            for t in range(T):
                con = Constraint(id=index,category='renewable')
                con.elements.update({'resource':r,'t':t})
                array_ = np.zeros(N)

                for a in P.activities:
                    units_ = a.resources[r.id]
                    if units_ == 0:
                        continue
                    min_ = min(t+a.duration-1, a.lf_time)
                    max_ = max(t,a.ef_time)
                    for t_ in range(max_,min_+1):
                        j = I.var_keys[(a.id,t_)]
                        con.scope.update({j:(a,t_)})
                        array_[j] = units_
                
                con.lhs = array_
                con.rhs = av_r
                con.rel = '<='
                I.constraints.update({index:con})
                I.con_keys.update({('renewable',r.id,t):index})
                index += 1

    return None

def nonrenewable_contraint_dict_old(I):
    """
    This function builds nonrenewable constraint
    sum_{j=1}^{J} k_{jr} sum_{t=EF}^{LFj} x_{jt} <= Kr
    """
    from definitions import Constraint
    P = I.project
    R = P.resources
    A = P.activities
    var = I.variables
    N = len(var)

    index = len(list(I.constraints.keys()))
    for r in R:
        if r.nonrenewable:
            av_r = r.units
            con = Constraint(id=index,category='nonrenewable')
            con.elements.update({'resource':r})
            array_ = np.zeros(N)
            for a in P.activities:
                units_ = a.resources[r.id]
                for t in range(a.ef_time,a.lf_time+1):
                    j = I.var_keys[(a.id,t)]
                    con.scope.update({j:(a,t)})
                    array_[j] = units_
            
                con.lhs = array_
                con.rhs = av_r
                con.rel = '<='
                I.constraints.update({index:con})
                I.con_keys.update({('nonrenewable',r.id):index})
                index += 1

    return None

def completion_contraint_dict(I):
    """
    This function builds completion constraint
    sum_{t=EFj}^{LFj} x_{jt} = 1
    """
    from definitions import Constraint
    P = I.project
    var = I.variables
    N = len(var)

    index = len(list(I.constraints.keys()))
    i=0
    for a in P.activities:
        con = Constraint(id=index,category='completion')
        con.elements.update({'activity':a})
        for t in range(a.ef_time,a.lf_time+1):
            con.scope.update({i:(a,t)})
            con.ind += [i]
            con.lhs += [1]
            i += 1

        con.rhs = 1
        con.rel = '=='
        I.constraints.update({index:con})
        I.con_keys.update({('completion',a.id):index})
        index += 1

    return None

def precedence_contraint_dict(I):
    """
    This function builds precedence constraint
    sum_{t=EFh}^{LFh} t*x_{ht} <= sum_{t=EFh}^{LFh} t*x_{jt}
    """
    from definitions import Constraint
    P = I.project
    var = I.variables
    N = len(var)

    index = len(list(I.constraints.keys()))
    for a in P.activities:
        for p in a.predecessors:
            pred = P.activities[p-1]
            con = Constraint(id=index,category='precedence')
            con.elements.update({'activity':a,'predecessor':pred})
            for t in range(pred.ef_time,pred.lf_time+1):
                h = I.var_keys[(pred.id,t)]
                con.scope.update({h:(pred,t)})
                con.ind += [h]
                con.lhs += [t]

            for t in range(a.ef_time,a.lf_time+1):
                j = I.var_keys[(a.id,t)]
                con.scope.update({j:(a,t)})
                con.ind += [j]
                con.lhs += [-1*(t-a.duration)]
                

            con.rhs = 0
            con.rel = '<='
            I.constraints.update({index:con})
            I.con_keys.update({('precedence',a.id,pred.id):index})
            index += 1

    return None


def renewable_contraint_dict(I):
    """
    This function builds renewable constraint
    sum_{j=1}^{J} k_{jr} sum_{q=max(t,EFj)}^{min(t+d_j-1,LFj)} x_{jq} <= Kr
    """
    from definitions import Constraint
    P = I.project
    R = P.resources
    T = P.horizon
    var = I.variables
    N = len(var)

    index = len(list(I.constraints.keys()))
    for r in R:
        if r.renewable:
            av_r = r.units
            for t in range(T):
                con = Constraint(id=index,category='renewable')
                con.elements.update({'resource':r,'t':t})

                for a in P.activities:
                    units_ = a.resources[r.id]
                    if units_ == 0:
                        continue
                    min_ = min(t+a.duration-1, a.lf_time)
                    max_ = max(t,a.ef_time)
                    for t_ in range(max_,min_+1):
                        j = I.var_keys[(a.id,t_)]
                        con.scope.update({j:(a,t_)})
                        con.ind += [j]
                        con.lhs += [units_]
                
                con.rhs = av_r
                con.rel = '<='
                I.constraints.update({index:con})
                I.con_keys.update({('renewable',r.id,t):index})
                index += 1

    return None

def nonrenewable_contraint_dict(I):
    """
    This function builds nonrenewable constraint
    sum_{j=1}^{J} k_{jr} sum_{t=EF}^{LFj} x_{jt} <= Kr
    """
    from definitions import Constraint
    P = I.project
    R = P.resources
    A = P.activities
    var = I.variables
    N = len(var)

    index = len(list(I.constraints.keys()))
    for r in R:
        if r.nonrenewable:
            av_r = r.units
            con = Constraint(id=index,category='nonrenewable')
            con.elements.update({'resource':r})
            for a in P.activities:
                units_ = a.resources[r.id]
                for t in range(a.ef_time,a.lf_time+1):
                    j = I.var_keys[(a.id,t)]
                    con.scope.update({j:(a,t)})
                    con.ind += [j]
                    con.lhs += [units_]
            
                con.rhs = av_r
                con.rel = '<='
                I.constraints.update({index:con})
                I.con_keys.update({('nonrenewable',r.id):index})
                index += 1

    return None

def constraint_generation_dict(I):
    """
    This function returns a dictionary with all the constraints
    """
    
    completion_contraint_dict(I)
    precedence_contraint_dict(I)
    renewable_contraint_dict(I)
    nonrenewable_contraint_dict(I)

    return None

if __name__ == '__main__':
    
    path = os.getcwd()
    folder = os.path.join(path,'data')
    file = os.path.join(folder,'j30','j3016_7.sm')
    
    from read_files import read_instance
    P = read_instance(file)

    
    counter = 0
    for a in P.activities:
        counter += a.duration
        print(f"{a}, {a.duration}")
    
    print(f"Total Duration: {counter}")

    