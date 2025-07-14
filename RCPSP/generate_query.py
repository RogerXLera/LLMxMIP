

import random as rd

def generate_query_1(I,Q,n_q=1):
    """
    Why is activity j completed in time slot t?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    len_q = len(Q)
    solutions_c = list(solution.keys()).copy()
    for i in range(n_q):
        len_ = len(solutions_c)
        n = rd.randint(0,len_-1)
        var = variables[solutions_c[n]]
        q = Query(id=len_q + i,category=1)
        q.elements = [var.elements]
        Q += [q]
        solutions_c.pop(n)
    return None

def generate_query_2(I,Q,n_q=1):
    """
    Why is activity j not completed in time slot t?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    not_selected_keys = [k for k in variables.keys() if k not in solution.keys()]
    len_q = len(Q)
    for i in range(n_q):
        len_ = len(not_selected_keys)
        n = rd.randint(0,len_-1)
        var = variables[not_selected_keys[n]]
        q = Query(id=len_q + i,category=2)
        q.elements = [var.elements]
        Q += [q]
        not_selected_keys.pop(n)
    return None

def generate_query_3(I,Q,n_q=1):
    """
    Why is activity j not completed before time slot t?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    len_q = len(Q)
    solutions_feasible = []
    for k in solution.keys():
        a = variables[k].elements[0]
        t = variables[k].elements[1]
        if t > a.ef_time:
            solutions_feasible.append(k)
    if len(solutions_feasible) == 0:
        print(f"Query 3 is not possible to generate.")
        raise ValueError(f"Query 3 cannot be generated because all activities already finished in the earliest time.")
    
    for i in range(n_q):
        len_ = len(solutions_feasible)
        if len_ == 0:
            break
        n = rd.randint(0,len_-1)
        var = variables[solutions_feasible[n]]
        q = Query(id=len_q + i,category=3)
        q.elements = [var.elements]
        Q += [q]
        solutions_feasible.pop(n)
    return None

def generate_query_4(I,Q,n_q=1):
    """
    Why is activity j not completed after time slot t?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    len_q = len(Q)
    solutions_feasible = []
    for k in solution.keys():
        a = variables[k].elements[0]
        t = variables[k].elements[1]
        if t < a.lf_time:
            solutions_feasible.append(k)
    if len(solutions_feasible) == 0:
        print(f"Query 4 is not possible to generate.")
        raise ValueError(f"Query 4 cannot be generated because all activities already finished in the latest time.")
    
    for i in range(n_q):
        len_ = len(solutions_feasible)
        if len_ == 0:
            break
        n = rd.randint(0,len_-1)
        var = variables[solutions_feasible[n]]
        q = Query(id=len_q + i,category=4)
        q.elements = [var.elements]
        Q += [q]
        solutions_feasible.pop(n)
    return None

def generate_query_5(I,Q,n_q=1):
    """
    Why is the subset of activites A completed at time t?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    len_q = len(Q)
    t_dict = {}
    for k in solution.keys():
        a = variables[k].elements[0]
        t = variables[k].elements[1]
        if t in t_dict.keys():
            t_dict[t].append(variables[k])
        else:
            t_dict.update({t:[variables[k]]})
    t_dict_new = {t:t_dict[t] for t in t_dict.keys() if len(t_dict[t]) > 1}
    if len(t_dict_new.keys()) == 0:
        print(f"Query 5 is not possible to generate.")
        raise ValueError(f"Query 5 cannot be generated since all activities finished in different times.")
    for i in range(n_q):
        len_ = len(t_dict_new.keys())
        n_t = rd.randint(0,len_-1)
        time_ = list(t_dict_new.keys())[n_t]
        var_list = t_dict[time_]
        q = Query(id=len_q + i,category=5)
        for var in var_list:
            q.elements += [var.elements]
    
        t_dict_new.pop(time_)
        Q += [q]
    return None

def generate_query_6(I,Q,n_q=1):
    """
    Why is the subset of activites A not completed at time t?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    len_q = len(Q)
    t_dict = {}
    for k in solution.keys():
        a = variables[k].elements[0]
        t = variables[k].elements[1]
        if t in t_dict.keys():
            t_dict[t].append(variables[k])
        else:
            t_dict.update({t:[variables[k]]})
        
    time_list = sorted(list(t_dict.keys()))
    for i in range(n_q):
        len_ = len(t_dict.keys())
        n_t = rd.randint(0,len_-1)
        
        time_ = time_list[n_t]
        len_t = len(list(t_dict.keys()))

        delta_t = 1
        alternative_a = []
        while delta_t < len_t - n_t or delta_t <= n_t:
            if n_t - delta_t >= 0:
                t_min = time_list[n_t - delta_t]
                var_list = t_dict[t_min]
                for var in var_list:
                    a = var.elements[0]
                    if a.ef_time <= time_ and a.lf_time >= time_:
                        alternative_a.append(var)
            if len(alternative_a) > 0:
                break

            if delta_t < len_t - n_t:
                t_max = time_list[n_t + delta_t]
                var_list = t_dict[t_max]
                for var in var_list:
                    a = var.elements[0]
                    if a.ef_time <= time_ and a.lf_time >= time_:
                        alternative_a.append(var)
            if len(alternative_a) > 0:
                break

            delta_t += 1
            
            
        var_list = t_dict[time_]
        q = Query(id=len_q + i,category=6)
        for var in var_list:
            q.elements += [var.elements]
        for var in alternative_a:
            q.elements += [var.elements]
    
        t_dict.pop(time_)
        Q += [q]
    return None

def generate_query_7(I,Q,n_q=1):
    """
    Why is the subset of activites A completed in the same time slot?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    len_q = len(Q)
    t_dict = {}
    for k in solution.keys():
        a = variables[k].elements[0]
        t = variables[k].elements[1]
        if t in t_dict.keys():
            t_dict[t].append(variables[k])
        else:
            t_dict.update({t:[variables[k]]})
    t_dict_new = {t:t_dict[t] for t in t_dict.keys() if len(t_dict[t]) > 1}
    if len(t_dict_new.keys()) == 0:
        print(f"Query 7 is not possible to generate.")
        raise ValueError(f"Query 7 cannot be generated since all activities finished in different times.")
    for i in range(n_q):
        len_ = len(t_dict_new.keys())
        n_t = rd.randint(0,len_-1)
        time_ = list(t_dict_new.keys())[n_t]
        var_list = t_dict[time_]
        q = Query(id=len_q + i,category=7)
        for var in var_list:
            q.elements += [var.elements]
    
        t_dict_new.pop(time_)
        Q += [q]
    return None

def generate_query_8(I,Q,n_q=1):
    """
    Why is the subset of activites A not completed in the same time slot?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    len_q = len(Q)
    t_dict = {}
    for k in solution.keys():
        a = variables[k].elements[0]
        t = variables[k].elements[1]
        if t in t_dict.keys():
            t_dict[t].append(variables[k])
        else:
            t_dict.update({t:[variables[k]]})
        
    time_list = sorted(list(t_dict.keys()))
    for i in range(n_q):
        len_ = len(t_dict.keys())
        n_t = rd.randint(0,len_-1)
        
        time_ = time_list[n_t]
        len_t = len(list(t_dict.keys()))

        delta_t = 1
        alternative_a = []
        while delta_t < len_t - n_t or delta_t <= n_t:
            if n_t - delta_t >= 0:
                t_min = time_list[n_t - delta_t]
                var_list = t_dict[t_min]
                for var in var_list:
                    a = var.elements[0]
                    if a.ef_time <= time_ and a.lf_time >= time_:
                        alternative_a.append(var)
            if len(alternative_a) > 0:
                break

            if delta_t < len_t - n_t:
                t_max = time_list[n_t + delta_t]
                var_list = t_dict[t_max]
                for var in var_list:
                    a = var.elements[0]
                    if a.ef_time <= time_ and a.lf_time >= time_:
                        alternative_a.append(var)
            if len(alternative_a) > 0:
                break

            delta_t += 1
            
            
        var_list = t_dict[time_]
        q = Query(id=len_q + i,category=8)
        for var in var_list:
            q.elements += [var.elements]
        for var in alternative_a:
            q.elements += [var.elements]
    
        t_dict.pop(time_)
        Q += [q]
    return None

def generate_query_9(I,Q,n_q=1):
    """
    Why is activity j completed in time slot t instead of time slot t'?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    var_keys = I.var_keys
    len_q = len(Q)
    solutions_c = list(solution.keys()).copy()
    for i in range(n_q):
        len_ = len(solutions_c)
        n = rd.randint(0,len_-1)
        var = variables[solutions_c[n]]
        a,t = var.elements
        possible_times = []
        delta_t = 1
        while len(possible_times) == 0 and delta_t < I.project.horizon:
            if a.ef_time <= t - delta_t:
                possible_times.append(t - delta_t)
            elif a.lf_time >= t + delta_t:
                possible_times.append(t + delta_t)
            delta_t += 1
        
        t_ = rd.choice(possible_times)
        q = Query(id=len_q + i,category=9)
        q.elements = [var.elements,[a,t_]]
        Q += [q]
        solutions_c.pop(n)
    return None

def generate_query_10(I,Q,n_q=1):
    """
    Why is activity j completed in time slot t instead of activity j'?
    """
    from definitions import Query
    solution = I.solution_values
    variables = I.variables
    len_q = len(Q)
    t_dict = {}
    for k in solution.keys():
        a = variables[k].elements[0]
        t = variables[k].elements[1]
        if t in t_dict.keys():
            t_dict[t].append(variables[k])
        else:
            t_dict.update({t:[variables[k]]})
        
    time_list = sorted(list(t_dict.keys()))
    for i in range(n_q):
        len_ = len(time_list)
        n_t = rd.randint(0,len_-1)
        var = rd.choice(t_dict[time_list[n_t]])
        a,t = var.elements
        
        possible_activities = []
        delta_t = 1
        while delta_t < len_:
            if delta_t + n_t < len_:
                t_p = time_list[n_t + delta_t]
                for var_ in t_dict[t_p]:
                    a_ = var_.elements[0]
                    if a_.ef_time <= t and a_.lf_time >= t:
                        possible_activities.append(var_)
            if n_t - delta_t >= 0:
                t_m = time_list[n_t - delta_t]
                for var_ in t_dict[t_m]:
                    a_ = var_.elements[0]
                    if a_.ef_time <= t and a_.lf_time >= t:
                        possible_activities.append(var_)
            if len(possible_activities) > 0:
                break
            delta_t += 1
        
        var_ = rd.choice(possible_activities)
        q = Query(id=len_q + i,category=10)
        q.elements = [var.elements,var_.elements]
        Q += [q]
        time_list.pop(n_t)
    return None


def generate_query_11(I,Q,n_q=1):
    """
    Why are {more, less, equal, not equal} than n_t activities finished in time slot t?
    """
    from definitions import Query
    types = ['more', 'less', 'equal', 'not equal']
    solution = I.solution_values
    variables = I.variables
    len_q = len(Q)
    t_dict = {}
    for k in solution.keys():
        a = variables[k].elements[0]
        t = variables[k].elements[1]
        if t in t_dict.keys():
            t_dict[t].append(variables[k])
        else:
            t_dict.update({t:[variables[k]]})

    time_list = sorted(list(t_dict.keys()))
    for i in range(n_q):
        type_ = rd.choice(types)
        t = rd.choice(time_list)
        j = time_list.index(t)
        n_t = len(t_dict[t])
        if type_ == 'equal':
            if j == 0:
                t_ = time_list[j+1]
            elif j == len(time_list) - 1:
                t_ = time_list[j-1]
            else:    
                t_ = rd.choice([time_list[j-1],time_list[j+1]])
            n_t = len(t_dict[t_])
        
        q = Query(id=len_q + i,category=11)
        q.elements = [[type_,t,n_t]]
        Q += [q]
    return None


def query_generation(I,category: int = 1, n_q: int = 1):
    """
    This function encodes the queries into the model
    """

    function = globals().get(f"generate_query_{category}")
    Q = []
    function(I,Q,n_q)
    return Q


if __name__ == '__main__':
    
    import argparse as ap
    import os
    print('Query generation')
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
    Q = query_generation(I,11)
    for q in Q:
        print("Type: ",q.category)
        for i in range(len(q.elements)):
            print(f"a: {q.elements[i][0]}, t: {q.elements[i][1]}")
    