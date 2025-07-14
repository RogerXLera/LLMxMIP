"""
Author: Roger X. Lera Leri
Date: 2024/02/13
"""

import random as rd
import os
import itertools

def generate_query_1(I,Q,n_q=1):
    """
    Why is course u planned in semester l?
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
        q.elements += [var.elements]
        Q += [q]
        solutions_c.pop(n)
    return None

def generate_query_2(I,Q,n_q=1):
    """
    Why is course u not planned in semester l?
    """
    from definitions import Query
    solution = I.solution_values
    L = I.course.semesters
    variables = I.variables
    solutions_c = list(solution.keys()).copy()
    len_q = len(Q)
    for i in range(n_q):
        len_ = len(solutions_c)
        n = rd.randint(0,len_-1)
        var = variables[solutions_c[n]]
        u,l = var.elements
        L_list = L.copy()
        L_list.pop(l.id - 1)
        n_random = rd.randint(0,len(L_list)-1)
        l_new = L_list[n_random]
        q = Query(id=len_q + i,category=2)
        q.elements += [[u,l_new]]
        Q += [q]
        solutions_c.pop(n)
    return None

def generate_query_3(I,Q,n_q=1):
    """
    Why is unit u not planned before semester l?
    """
    from definitions import Query
    solution = I.solution_values
    L = I.course.semesters
    variables = I.variables
    len_q = len(Q)
    solutions_feasible = []
    for k in solution.keys():
        u,l = variables[k].elements
        if l.id > L[0].id: #not first semester
            solutions_feasible.append(k)
    
    for i in range(n_q):
        len_ = len(solutions_feasible)
        n = rd.randint(0,len_-1)
        var = variables[solutions_feasible[n]]
        q = Query(id=len_q + i,category=3)
        q.elements += [var.elements]
        Q += [q]
        solutions_feasible.pop(n)
    return None

def generate_query_4(I,Q,n_q=1):
    """
    Why is unit u not planned after semester l?
    """
    from definitions import Query
    solution = I.solution_values
    L = I.course.semesters
    variables = I.variables
    len_q = len(Q)
    solutions_feasible = []
    for k in solution.keys():
        u,l = variables[k].elements
        if l.id < L[-1].id: # not last semester
            solutions_feasible.append(k)
    
    for i in range(n_q):
        len_ = len(solutions_feasible)
        n = rd.randint(0,len_-1)
        var = variables[solutions_feasible[n]]
        q = Query(id=len_q + i,category=4)
        q.elements += [var.elements]
        Q += [q]
        solutions_feasible.pop(n)
    return None

def generate_query_5(I,Q,n_q=1):
    """
    Why is course u planned?
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
        q = Query(id=len_q + i,category=5)
        q.elements += [var.elements]
        Q += [q]
        solutions_c.pop(n)
    return None

def generate_query_6(I,Q,n_q=1):
    """
    Why is course u not planned?
    """
    from definitions import Query
    solution = I.solution_values
    U = I.course.units
    L = I.course.semesters
    variables = I.variables
    u_in_solution = [variables[i].elements[0].id for i in solution.keys()]
    u_not_in_solution = [u_id for u_id in U.keys() if u_id not in u_in_solution]
    len_q = len(Q)
    for i in range(n_q):
        len_ = len(u_not_in_solution)
        n = rd.randint(0,len_-1)
        u = U[u_not_in_solution[n]]
        q = Query(id=len_q + i,category=6)
        q.elements += [[u,L[0]]]
        Q += [q]
        u_not_in_solution.pop(n)
    return None

def generate_query_7(I,Q,n_q=1):
    """
    Why is the subset of units U planned at semester l?
    """
    from definitions import Query
    solution = I.solution_values
    U = I.course.units
    L = I.course.semesters
    variables = I.variables
    len_q = len(Q)
    t_dict = {l.id:[] for l in L}
    for k in solution.keys():
        u,l = variables[k].elements
        t_dict[l.id].append(variables[k])

    combinations = {l:[] for l in t_dict.keys()}
    for l in t_dict.keys():
        combinations[l] += list(itertools.combinations(t_dict[l], 2))
        
    for i in range(n_q):
        len_ = len(combinations.keys())
        n_pairs = 0
        iter_ = 0
        while n_pairs == 0 and iter_ < 100:
            n_t = rd.randint(0,len_-1)
            l = list(combinations.keys())[n_t]
            n_pairs = len(combinations[l])
            iter_ += 1

        n = rd.randint(0,n_pairs-1)
        pair = combinations[l][n]
        q = Query(id=len_q + i,category=7)
        for var in pair:
            q.elements += [var.elements]
    
        combinations[l].pop(n)
        Q += [q]
    return None

def generate_query_8(I,Q,n_q=1):
    """
    Why is the subset of units U not planned at semester l?
    """
    from definitions import Query
    solution = I.solution_values
    U = I.course.units
    L = I.course.semesters
    variables = I.variables
    len_q = len(Q)
    units_planned = list(solution.keys()).copy()

    t_dict = {l.id:[] for l in L}
    for k in solution.keys():
        u,l = variables[k].elements
        t_dict[l.id].append(variables[k])
    
    for i in range(n_q):
        len_ = len(units_planned)
        n = rd.randint(0,len_-1)
        u,l = variables[units_planned[n]].elements
        units_planned.pop(n)
        L_list = L.copy()
        L_list.pop(l.id - 1)
        n_t = rd.randint(0,len(L_list)-1)
        l_new = L_list[n_t]

        len_t = len(t_dict[l_new.id])
        n_new = rd.randint(0,len_t-1)
        u_new,l_new = t_dict[l_new.id][n_new].elements

        q = Query(id=len_q + i,category=8)
        q.elements += [[u,l],[u_new,l_new]]
        
        Q += [q]
    return None



def generate_query_9(I,Q,n_q=1):
    """
    Why is unit u planned in semester l instead of unit u'?
    """
    from definitions import Query
    solution = I.solution_values
    U = I.course.units
    L = I.course.semesters
    variables = I.variables
    len_q = len(Q)
    units_planned = list(solution.keys()).copy()

    t_dict = {l.id:[] for l in L}
    for k in solution.keys():
        u,l = variables[k].elements
        t_dict[l.id].append(variables[k])
    
    for i in range(n_q):
        len_ = len(units_planned)
        n = rd.randint(0,len_-1)
        u,l = variables[units_planned[n]].elements
        units_planned.pop(n)
        L_list = L.copy()
        L_list.pop(l.id - 1)
        n_t = rd.randint(0,len(L_list)-1)
        l_new = L_list[n_t]

        len_t = len(t_dict[l_new.id])
        n_new = rd.randint(0,len_t-1)
        u_new,l_new = t_dict[l_new.id][n_new].elements

        q = Query(id=len_q + i,category=9)
        q.elements += [[u,l],[u_new,l_new]]
        
        Q += [q]
    return None


def generate_query_10(I,Q,n_q=1):
    """
    Why is unit u planned instead of unit u'?
    """
    from definitions import Query
    solution = I.solution_values
    U = I.course.units
    L = I.course.semesters
    variables = I.variables
    u_in_solution = [variables[i].elements[0].id for i in solution.keys()]
    u_not_in_solution = [u_id for u_id in U.keys() if u_id not in u_in_solution]
    len_q = len(Q)
    for i in range(n_q):
        len_ = len(u_in_solution)
        n = rd.randint(0,len_-1)
        u = U[u_in_solution[n]]
        len_not = len(u_not_in_solution)
        n_not = rd.randint(0,len_not-1)
        u_not = U[u_not_in_solution[n_not]]
        q = Query(id=len_q + i,category=10)
        q.elements += [[u,L[0]],[u_not,L[0]]]
        Q += [q]
        u_in_solution.pop(n)
        u_not_in_solution.pop(n_not)
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
    parser.add_argument('-n', type=int, default=6, help='n')
    parser.add_argument('-c', type=int, default=240, help='c')
    parser.add_argument('-l', type=int, default=7, help='l: maximum level. Default: 7')
    parser.add_argument('-j', type=str, default='0', help='Job index')
    parser.add_argument('-s', type=str, default='au', help='Start semester')
    parser.add_argument('-q', type=int, default=1, help='q: Query type')
    parser.add_argument('--seed', type=int, default=0, help='seed')
    args = parser.parse_args()
    
    rd.seed(args.seed)
    

    from read_files import read_instance
    I = read_instance(args.n,args.c,args.j,args.s,args.l)
    I.build_model()
    folder = os.path.join(os.getcwd(),'solutions')
    file = os.path.join(folder,f"sol-{args.j}.stdout")
    I.read_solution(file)
    Q = query_generation(I,args.q,n_q=5)
    folder = os.path.join(os.getcwd(),'queries',f'{args.q}')
    iter_ = 0
    for q in Q:
        print("Type: ",q.category)
        for i in range(len(q.elements)):
            print(f"subject: {q.elements[i][0].id}, semester: {q.elements[i][1].id}")

        filename = os.path.join(folder,f'query-{args.j}-{iter_}.txt')
        q.save_query(filename)
        iter_ += 1

        
    