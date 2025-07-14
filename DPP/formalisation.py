"""
Roger X. Lera-Leri
2024/01/16
"""

"""
In this script there are all the functions that will create the matrices and vectors
for our ILP formalisation
"""
import numpy as np
import os
from definitions import Variable,Constraint


def decision_variables(I):
    """
    This function returns a dictionary with all the keys of the decision variables
    """
    
    i=0
    U = I.course.units
    L = I.course.semesters
    mdl = I.model
    # x variables
    x_vars = []
    for u_id,u in U.items():
        for l in L:
            var = Variable(id=i,category='x')
            var.elements = [u,l]
            I.variables.update({i:var})
            I.var_keys.update({(u.id,l.id):i})
            x_vars.append(i)
            i += 1


    # defining variables
    x = mdl.binary_var_dict(x_vars,name='x')

    M = I.course.majors
    v_vars = []
    # v auxiliary variables
    for m_id,m in M.items():
        var = Variable(id=i,category='v')
        var.elements = [m]
        I.variables.update({i:var})
        I.var_keys.update({('v',m.id):i})
        v_vars.append(i)
        i += 1

    # defining variables
    v = mdl.binary_var_dict(v_vars,name='v')

    S = I.job.skills
    max_lev = I.max_level
    y_vars = []
    # y auxiliary variables
    for s_id,s in S.items():
        for lev in range(1, s.level+1):
            var = Variable(id=i,category='y')
            var.elements = [s,lev]
            I.variables.update({i:var})
            I.var_keys.update({('y',s.id,lev):i})
            y_vars.append(i)
            i += 1

    # defining variables
    y = mdl.binary_var_dict(y_vars,name='y')

    return None

def get_var_keys(variables:dict):

    x_vars = []
    v_vars = []
    y_vars = []
    
    for key,var in variables.items():
        if var.category == 'x':
            x_vars.append(key)
        elif var.category == 'v':
            v_vars.append(key)
        elif var.category == 'y':
            y_vars.append(key)
        

    return x_vars,v_vars,y_vars,0,0

def get_variables(model,name: str, keys:list):
    x = {}
    for i in keys:
        x.update({i:model.get_var_by_name(f'{name}_{i}')})
    return x

def completion_constraint(I):
    """
    This function builds completion constraint
    sum_{l \in L} x_{ul} <= 1, \\forall u \in U
    """
    U = I.course.units
    L = I.course.semesters
    mdl = I.model
    var = I.variables
    x_vars,_,_,_,_ = get_var_keys(I.variables)
    x = get_variables(mdl,'x',x_vars)

    index = len(list(I.constraints.keys()))
    i=0
    for u_id,u in U.items():
        con = Constraint(id=index,category='completion')
        con.elements.update({'unit':u})
        sum_list = []
        for l in L:
            con.scope.update({i:(u,l)})
            sum_list += [x[i]]
            i += 1
        
        mdl.add_constraint(mdl.sum(sum_list) <= 1)
        I.constraints.update({index:con})
        I.con_keys.update({('completion',u.id):index})
        index += 1

    return None

def offer_constraint(I):
    """
    This function builds offer constraint
    \sum_{l \in L | \gamma_u(l) = \\bot} x_{ul} == 0, \\forall u \in U, 
    """

    U = I.course.units
    L = I.course.semesters
    seasons = I.course.seasons
    mdl = I.model
    var = I.variables
    x_vars,_,_,_,_ = get_var_keys(I.variables)
    x = get_variables(mdl,'x',x_vars)

    index = len(list(I.constraints.keys()))
    for u_id,u in U.items():
        for se in seasons:
            if se not in u.seasons:
                con = Constraint(id=index,category='offer')
                con.elements.update({'unit':u,'season':se})
                sum_list = []
                for l in L:
                    if l.season not in u.seasons:
                        i = I.var_keys[(u.id,l.id)]
                        con.scope.update({i:(u,l)})
                        sum_list += [x[i]]
            
        
                mdl.add_constraint(mdl.sum(sum_list) == 0)
                I.constraints.update({index:con})
                I.con_keys.update({('offer',u.id,se):index})
                index += 1

    return None

def credits_constraint(I):
    """
    This function builds credits constraint
    \sum_{u \in U} c_u*x_{ul} == d_l, \\forall l \in L
    """
    
    U = I.course.units
    L = I.course.semesters
    mdl = I.model
    var = I.variables
    x_vars,_,_,_,_ = get_var_keys(I.variables)
    x = get_variables(mdl,'x',x_vars)
    

    index = len(list(I.constraints.keys()))
    for l in L:
        con = Constraint(id=index,category='credits')
        con.elements.update({'semester':l})
        sum_list = []
        for u_id,u in U.items():
            i = I.var_keys[(u.id,l.id)]
            con.scope.update({i:(u,l)})
            sum_list += [u.credits*x[i]]
            
        
        mdl.add_constraint(mdl.sum(sum_list) == l.credits)
        I.constraints.update({index:con})
        I.con_keys.update({('credits',l.id):index})
        index += 1

    return None

def precedence_constraint(I):
    """
    This function builds precedence constraint
    sum_{t=1}^{l-1} x_{pl} >= x_{ul} \\forall u \in U , l=2,...,n
    """

    U = I.course.units
    L = I.course.semesters
    mdl = I.model
    var = I.variables
    x_vars,_,_,_,_ = get_var_keys(I.variables)
    x = get_variables(mdl,'x',x_vars)

    index = len(list(I.constraints.keys()))
    for u_id,u in U.items():
        i_pred = 0
        for pred in u.prerequisites:
            for k in range(len(L)):
                l = L[k]
            
                con = Constraint(id=index,category='precedence')
                con.elements.update({'unit':u,'predecessors':pred,
                                    'semester':l})
                sum_list_p = []
                for p in pred:
                    if p not in U.keys():
                        continue
                    u_pred = U[p]
                    for t in range(0,k):
                        l_p = L[t]
                        h = I.var_keys[(u_pred.id,l_p.id)]
                        con.scope.update({h:(u_pred,l_p)})
                        sum_list_p += [x[h]]

                j = I.var_keys[(u.id,l.id)]
                con.scope.update({j:(u,l)})
                
                mdl.add_constraint(mdl.sum(sum_list_p) >= x[j])
                I.constraints.update({index:con})
                I.con_keys.update({('precedence',u.id,i_pred,l.id):index})
                i_pred += 1 #predecessor count
                index += 1

    return None

def core_constraint(I):
    """
    This function builds core constraint
    sum_{l \in L} x_{ul} == 1 \\forall u \in U_core
    """

    U = I.course.units
    L = I.course.semesters
    mdl = I.model
    var = I.variables
    x_vars,_,_,_,_ = get_var_keys(I.variables)
    x = get_variables(mdl,'x',x_vars)

    index = len(list(I.constraints.keys()))
    for u_id,u in U.items():
        if u.core == False:
            continue

        con = Constraint(id=index,category='core')
        con.elements.update({'unit':u})
        sum_list = []
        for l in L:
            i = I.var_keys[(u.id,l.id)]
            con.scope.update({i:(u,l)})
            sum_list += [x[i]]


        mdl.add_constraint(mdl.sum(sum_list) == 1)
        I.constraints.update({index:con})
        I.con_keys.update({('core',u.id):index})
        index += 1

    return None


def major_constraint(I):
    """
    This function builds core constraint
    sum_{m \in M} v_{m} == 1 
    """

    mdl = I.model
    var = I.variables
    _,v_vars,_,_,_ = get_var_keys(I.variables)
    v = get_variables(mdl,'v',v_vars)

    index = len(list(I.constraints.keys()))
    con = Constraint(id=index,category='major_completion')
    scope_keys = [i for i in v.keys()]
    scope_values = [m for mi,m in I.course.majors.items()]
    con.scope.update({key:m for key,m in zip(scope_keys,scope_values)})
    sum_list = [v[i] for i in v.keys()]
    mdl.add_constraint(mdl.sum(sum_list) == 1)
    I.constraints.update({index:con})
    I.con_keys.update({('major_completion'):index})
    index += 1
    
    return None

def major_core_constraint(I):
    """
    This function builds major core constraint
    sum_{l \in L} x_{ul} >= v_M \\forall u \in M_core , M \in \mathcal{M}
    """

    U = I.course.units
    L = I.course.semesters
    M = I.course.majors
    mdl = I.model
    var = I.variables
    x_vars,v_vars,_,_,_ = get_var_keys(I.variables)
    x = get_variables(mdl,'x',x_vars)
    v = get_variables(mdl,'v',v_vars)

    index = len(list(I.constraints.keys()))
    for m_id,m in M.items():
        for u_id in m.core:
            u = U[u_id]

            con = Constraint(id=index,category='major_core')
            con.elements.update({'major':m,'unit':u})
            sum_list = []
            for l in L:
                i = I.var_keys[(u.id,l.id)]
                con.scope.update({i:(u,l)})
                sum_list += [x[i]]

            j = I.var_keys[('v',m.id)]
            con.scope.update({j:('v',m)})
            mdl.add_constraint(mdl.sum(sum_list) >= v[j])
            I.constraints.update({index:con})
            I.con_keys.update({('major_core',m.id,u.id):index})
            index += 1

    return None

def major_electives_constraint(I):
    """
    This function builds major electives constraint
    sum_{u \in SM^elig} sum_{l \in L} x_{ul} >= n_{SM^elig}*v_M \\forall u \in M_core , M \in \mathcal{M}
    """

    U = I.course.units
    L = I.course.semesters
    M = I.course.majors
    mdl = I.model
    var = I.variables
    x_vars,v_vars,_,_,_ = get_var_keys(I.variables)
    x = get_variables(mdl,'x',x_vars)
    v = get_variables(mdl,'v',v_vars)

    index = len(list(I.constraints.keys()))
    for m_id,m in M.items():
        elec_index = 0
        for elec in m.electives:

            con = Constraint(id=index,category='major_electives')
            con.elements.update({'major':m,'electives':elec})
            sum_list = []
            for u_id in elec['units']:
                u = U[u_id]
                for l in L:
                    i = I.var_keys[(u.id,l.id)]
                    con.scope.update({i:(u,l)})
                    sum_list += [x[i]]    

            n_count = elec['count']
            j = I.var_keys[('v',m.id)]
            con.scope.update({j:('v',m)})
            mdl.add_constraint(mdl.sum(sum_list) >= n_count*v[j])
            I.constraints.update({index:con})
            I.con_keys.update({('major_electives',m.id,elec_index):index})
            elec_index += 1
            index += 1

    return None

def unit_skill_constraint(I):
    """
    This function builds unit skill constraints
    sum_{u \in U_{s,lev}} sum_{l \in L} x_{ul} <= \Delta * y_{s,lev} 
    sum_{u \in U_{s,lev}} sum_{l \in L} x_{ul} >= \Delta * (y_{s,lev}-1) + 1 
    \\forall s \in S , lev = 1, ..., max_lev
    """

    U = I.course.units
    L = I.course.semesters
    S = I.job.skills
    mdl = I.model
    var = I.variables
    x_vars,_,y_vars,_,_ = get_var_keys(I.variables)
    x = get_variables(mdl,'x',x_vars)
    y = get_variables(mdl,'y',y_vars)
    Delta = len(x) # \Delta constant in the formalisation

    index = len(list(I.constraints.keys()))
    for s_id,s in S.items():
        for lev in range(1,s.level + 1):

            sum_list = []
            con = Constraint(id=index,category='unit_skill')
            con.elements.update({'skill':s,'level':lev})
            con2 = Constraint(id=index+1,category='unit_skill')
            con2.elements.update({'skill':s,'level':lev})

            for u_id,u in U.items():
                if s.id in u.skills.keys():
                    s_u = u.skills[s.id]
                    if s_u.level >= lev:
                        for l in L:
                            i = I.var_keys[(u.id,l.id)]
                            con.scope.update({i:(u,l)})
                            con2.scope.update({i:(u,l)})
                            sum_list += [x[i]]   


            j = I.var_keys[('y',s.id,lev)]
            con.scope.update({j:('y',s,lev)})
            con2.scope.update({j:('y',s,lev)})
            mdl.add_constraint(mdl.sum(sum_list) <= Delta*y[j])
            I.constraints.update({index:con})
            I.con_keys.update({('unit_skill',s.id,lev,1):index})
            mdl.add_constraint(mdl.sum(sum_list) >= Delta*(y[j] - 1) + 1)
            I.constraints.update({index+1:con2})
            I.con_keys.update({('unit_skill',s.id,lev,2):index+1})
            index += 2

    return None

def skill_level_constraint(I):
    """
    This function builds skill level constraints
    z_s <= sum_{lev = 1}^{max_lev} y_{s,lev} - t_s
    z_s <= 0
    -w_s <= z_s
    z_s <= w_s
    \\forall s \in S 
    """

    U = I.course.units
    L = I.course.semesters
    S = I.job.skills
    mdl = I.model
    var = I.variables
    _,_,y_vars,z_vars,_ = get_var_keys(I.variables)
    y = get_variables(mdl,'y',y_vars)
    z = get_variables(mdl,'z',z_vars)
    
    index = len(list(I.constraints.keys()))
    for s_id,s in S.items():
        t_s = s.level
        con = Constraint(id=index,category='skill_level')
        con.elements.update({'skill':s})
        sum_list = []
        for lev in range(1,s.level + 1):
            i = I.var_keys[('y',s.id,lev)]
            con.scope.update({i:('y',s,lev)})
            sum_list += [y[i]]   


        j = I.var_keys[('z',s.id)]
        # \sum_lev y_{s,lev} - t_s <= z_s
        con.scope.update({j:('z',s)})
        mdl.add_constraint(mdl.sum(sum_list) - t_s  <= z[j])
        I.constraints.update({index:con})
        I.con_keys.update({('skill_level',s.id,1):index})
        # -\sum_lev y_{s,lev} + t_s <= z_s
        mdl.add_constraint(t_s - mdl.sum(sum_list) <= z[j])
        con2 = Constraint(id=index+1,category='skill_level')
        con2.elements.update({'skill':s})
        con2.scope.update({j:('z',s)})
        I.constraints.update({index+1:con2})
        I.con_keys.update({('skill_level',s.id,2):index+1})

        index += 2

    return None

def constraint_generation(I):
    """
    This function returns a dictionary with all the constraints
    """
    
    completion_constraint(I)
    offer_constraint(I)
    credits_constraint(I)
    precedence_constraint(I)
    core_constraint(I)
    major_constraint(I)
    major_core_constraint(I)
    major_electives_constraint(I)
    # objective linearisation
    unit_skill_constraint(I)
    #skill_level_constraint(I)

    return None



def constraint_generation_lp(I):
    """
    This function returns a dictionary with all the constraints
    """

    return None

def objective_generation(I):
    """
    This function creates the objective function
    """
    from definitions import Objective
    mdl = I.model
    _,_,y_vars,_,_ = get_var_keys(I.variables)
    y = get_variables(mdl,'y',y_vars)
    
    S = I.job.skills
    sum_list = []
    ob = Objective(id=1)
    for s_id,s in S.items():
        for lev in range(1,s.level+1):
            j = I.var_keys[('y',s.id,lev)]
            ob.scope.update({j:('y',s,lev)})
            sum_list += [y[j]]

    mdl.maximize(mdl.sum(sum_list))
    I.objective = ob

    return None




if __name__ == '__main__':
    
    from read_files import read_instance
    import argparse as ap
    
    parser = ap.ArgumentParser()
    parser.add_argument('-n', type=int, default=6, help='n')
    parser.add_argument('-c', type=int, default=240, help='c')
    parser.add_argument('-l', type=int, default=7, help='l: maximum level. Default: 7')
    parser.add_argument('-j', type=str, default='0', help='Job index')
    parser.add_argument('-s', type=str, default='au', help='Start semester')
    args = parser.parse_args()


    I = read_instance(args.n,args.c,args.j,args.s,args.l)

    
    
   

    