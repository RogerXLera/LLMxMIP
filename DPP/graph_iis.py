"""
Roger X. Lera Leri
2025/04/29
"""

import numpy as np
import itertools
import networkx as nx
import matplotlib.pyplot as plt
import json


def positions_graph(lev_nodes):

    max_width = max([len(lev_list) for lev,lev_list in lev_nodes.items()])
    n_lev = len(lev_nodes)
    int_y = 5
    int_x = 5
    max_x = max_width*int_x
    max_y = n_lev*int_y
    pos = {}
    for lev,lev_list in lev_nodes.items():
        len_ = len(lev_list)
        int_x_ = max_x/(len_+1)
        for j in range(len_):
            id_ = lev_list[j]
            x = int_x_*(j+1) - max_x/2
            y = max_y - lev*int_y
            pos.update({id_:(x,y)})


    return pos


def graph_iis(IIS):

    I = IIS.instance
    id_i = IIS.id.split('-')[2]
    con = IIS.constraints
    ordered_nodes = [0]
    level = 0
    level_nodes = {level:[0]}
    q = IIS.query
    q_scope = set(q.scope.keys())
    
    constraints_scope = {}
    for c,cob in con.items():
        name_ = cob.name()
        scope_ = cob.scope
        
        if name_ == 'q':
            continue
        if name_ in constraints_scope.keys():
            for var_key,var_val in scope_.items():
                
                constraints_scope[name_].update({var_key:var_val})
        else:
            
            for var_key,var_val in scope_.items():
                
                constraints_scope.update({name_:scope_})

    
    

    constraints_scope_keys = list(constraints_scope.keys())
    len_con = len(constraints_scope)
    
    adjacency = np.zeros((len_con + 1,len_con + 1),dtype=np.bool_) # query position 1
    edges = []
    # save edges of the graph and queries as level 0
    for i in range(1,len_con+1):
        ci = constraints_scope_keys[i-1]
        cvar_i = set(constraints_scope[ci])
        intersec_q = cvar_i.intersection(q_scope) # check scope with query
        if len(intersec_q) > 0:
                adjacency[0,i] = 1
                adjacency[i,0] = 1
                edges += [(0,i)]
        for j in range(i+1,len_con+1):
            cj = constraints_scope_keys[j-1]
            cvar_j = set(constraints_scope[cj])
            intersec = cvar_i.intersection(cvar_j)
            if len(intersec) > 0:
                adjacency[i,j] = 1
                adjacency[j,i] = 1
                edges += [(i,j)]


    iter_ = 0
    constraints_scope_keys_copy = constraints_scope_keys.copy()
    itermax = len_con
    while len(constraints_scope_keys) > 0 and iter_ < itermax:
        iter_ += 1
        lev_list = level_nodes[level]
        level_nodes.update({level+1:[]})
        for i in lev_list:
            con_copy = constraints_scope_keys.copy()
            for j in range(len(con_copy)):
                cj = con_copy[j]
                index_j = constraints_scope_keys_copy.index(cj) + 1
                if adjacency[i,index_j] == 1 and cj in constraints_scope_keys:
                    level_nodes[level+1] += [index_j]
                    ordered_nodes += [index_j]
                    constraints_scope_keys.remove(cj)

        level += 1

    pos = positions_graph(level_nodes)
    filepath = os.path.join(os.getcwd(),'graph',f'q{q.category}',f"{I.job.id}-{q.category}-{id_i}")
    
    np.save(file=f"{filepath}-order.npy",arr=np.array(ordered_nodes,dtype=np.int16))
    np.save(file=f"{filepath}-edges.npy",arr=np.array(edges,dtype=np.int16))

    G = nx.Graph()
    G.add_nodes_from(ordered_nodes)
    G.add_edges_from(edges)
    labels = {0:'query'}
    for i in range(1,len(ordered_nodes)):
        ci = ordered_nodes[i]
        name_ = constraints_scope_keys_copy[ci-1]
        labels.update({ci:name_})

    with open(f"{filepath}-labels.json",'w') as jsonf:
        json.dump(labels,jsonf)

    nx.draw_networkx(G, pos = pos, labels = labels, arrows = False,
                    node_shape = 's', node_color = 'white')
    plt.title('IIS constraint graph.')
    graffile = os.path.join(os.getcwd(),'graph',f'q{q.category}',f"{I.job.id}-{q.category}-{id_i}.jpeg")
    plt.savefig(graffile,dpi = 300)
    plt.clf()
    #plt.show()


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
    parser.add_argument('--nq', type=int, default=10, help='nq: number of queries')
    parser.add_argument('--ni', type=int, default=5, help='ni: number of instances')
    args = parser.parse_args()

    from read_files import read_instance
    import copy
    from definitions import *
    from reasons import job_indixes
    
    J = job_indixes()
    path_to_data = os.path.join(os.getcwd(),'data')
    iis_folder = os.path.join(os.getcwd(),'iis')
    sol_folder = os.path.join(os.getcwd(),'solutions')

    
    for j in J:
        I = read_instance(j=j)
        I.build_model()
        I.read_solution(os.path.join(sol_folder,f"sol-{j}.stdout"))
        print(f"J:{j}")
        
        for q_ in range(1,args.nq + 1):
            for i in range(0,args.ni):
                I_copy = copy.deepcopy(I)
                q = Query(id=q_,category=q_)
                iis = IIS(id=f"{j}-{q_}-{i}",instance=I_copy,query=q)
                iis_file = os.path.join(iis_folder,f'q{q_}',f"iis-{j}-{q_}-{i}.stdout")
                iis.read(iis_file)
                q = iis.query
                if iis.optimality == 'time':
                    continue
                solving_time = iis.solution_time
                if len(iis.constraints) == 0:
                    continue
                #print(f"Q{q_}")
                graph_iis(iis)

            
        