"""
Author: Roger X. Lera Leri
Date: 2024/04/01
"""
import numpy as np
import pandas as pd
import copy
import os

def translate_query_1(q,template):

    a,t = q.elements[0]
    
    template = template.replace('{a}',str(a.id)).replace('{t}',str(t))
    return template

def translate_query_2(q,template):

    a,t = q.elements[0]
    
    template = template.replace('{a}',str(a.id)).replace('{t}',str(t))
    return template

def translate_query_3(q,template):

    a,t = q.elements[0]
    
    template = template.replace('{a}',str(a.id)).replace('{t}',str(t))
    return template

def translate_query_4(q,template):

    a,t = q.elements[0]
    
    template = template.replace('{a}',str(a.id)).replace('{t}',str(t))
    return template

def translate_query_5(q,template):

    A_list = [str(elem[0].id) for elem in q.elements]
    A = ", ".join(A_list)
    t = q.elements[0][1]
    template = template.replace('{A}',A).replace('{t}',str(t))
    return template

def translate_query_6(q,template):

    A_list = [str(elem[0].id) for elem in q.elements]
    A = ", ".join(A_list)
    t = q.elements[0][1]
    template = template.replace('{A}',A).replace('{t}',str(t))
    return template

def translate_query_7(q,template):

    A_list = [str(elem[0].id) for elem in q.elements]
    A = ", ".join(A_list)

    template = template.replace('{A}',A)
    return template

def translate_query_8(q,template):

    A_list = [str(elem[0].id) for elem in q.elements]
    A = ", ".join(A_list)

    template = template.replace('{A}',A)
    return template

def translate_query_9(q,template):

    a,t = q.elements[0]
    a,t_ = q.elements[1]
    
    template = template.replace('{a}',str(a.id)).replace('{t}',str(t))
    template = template.replace('{t_}',str(t_))
    return template

def translate_query_10(q,template):

    a,t = q.elements[0]
    a_,t_ = q.elements[1]
    
    template = template.replace('{a}',str(a.id)).replace('{t}',str(t))
    template = template.replace('{a_}',str(a_.id))
    return template

def translate_query_11(q,template):

    type_,t,n_t = q.elements[0]
    
    template = template.replace('{type_}',str(type_)).replace('{n_t}',str(n_t))
    template = template.replace('{t}',str(t))
    return template

def translate_query(q,df_q):

    q_type = q.category
    template = df_q[df_q['query'] == q_type]['text'].iloc[0]
    function = globals().get(f"translate_query_{q_type}")
    question = function(q,template)
    return question

def translate_explanations(filename:str,n:int):

    path = os.getcwd()
    folder = os.path.join(path,'data')
    sub_folder = os.path.join(folder,f"j{n}")
    folder_sol = os.path.join(path,'solutions')
    sub_folder_sol = os.path.join(folder_sol,f"j{n}")
    folder_iis = os.path.join(path,'iis')
    sub_folder_iis = os.path.join(folder_iis,f"j{n}")
    file = os.path.join(sub_folder,f"{filename}")

    P = read_instance(file)

    instance_id = f"{filename}".split('.')[0]
    I = Instance(id=instance_id,project=P)
    I.build_model()
    file_sol = os.path.join(sub_folder_sol,f"{filename}.stdout")
    I.read_solution(file_sol)

    n_queries = 11
    q_types = [i for i in range(1,n_queries+1)]
    iis_list = []
    query_templates_url = os.path.join(path,f"query_templates.csv")
    df_q = pd.read_csv(query_templates_url,delimiter=',')
    

    for q_ in q_types:
        q = Query(id=q_,category=q_)
        I_copy = copy.deepcopy(I)
        iis = IIS(id=instance_id,instance=I_copy,query=q)
        iis_file = os.path.join(sub_folder_iis,f"iis-{filename}-{q_}.stdout")
        iis.read(iis_file)
        q.translate(df_q)
        iis_list.append(iis)

    return None

def translate_completion(r,template):
    a = r.elements['activity']

    template = template.replace('{a}',str(a.id))
    return template

def translate_precedence(r,template):
    a = r.elements['activity']
    pred = r.elements['predecessor']

    template = template.replace('{a}',str(a.id)).replace('{pred}',str(pred.id))
    return template

def translate_renewable(r,template):
    res = r.elements['resource']
    t = r.elements['t']
    A = [str(x[0].id) for i,x in r.scope.items()]
    A = np.unique(A)
    A = ", ".join(A)

    template = template.replace('{r}',str(res.id)).replace('{t}',str(t)).replace('{A}',str(A))
    return template

def translate_nonrenewable(r,template):
    res = r.elements['resource']

    template = template.replace('{r}',str(res.id))
    return template

def translate_max(df_c,t):
    template = df_c[df_c['constraint'] == 'max']['text'].iloc[0]
    template = template.replace('{t}',str(t))
    return template

def translate_reason(r,df_c):
    con_type = r.category
    template = df_c[df_c['constraint'] == con_type]['text'].iloc[0]
    function = globals().get(f"translate_{con_type}")
    if con_type == 'max':
        t_max = int(r.elements['f'])
        translation = function(df_c,t_max)
    else:
        translation = function(r,template)
    return translation

def translate_explanation(e,df_c):
    iis = e.iis
    I = iis.instance
    t_max = I.objective_value
    optim = iis.optimality
    q = iis.query
    sentence = translate_query(q,df_c)
    if optim == 'optimal':
        sentence += ', but the contrary can be optimal too.'
        return sentence
    elif optim == 'suboptimal':
        sentence += ' because:\n'
        for r in e.ordered:
            sentence += '\t- ' + translate_reason(r,df_c) + ',\n'

        sentence += 'and the contrary ' + translate_max(df_c,t_max) + '.'
        return sentence
    elif optim == 'infeasible':
        sentence += ' because:\n'
        for r in e.ordered:
            sentence += '\t- ' + translate_reason(r,df_c) + ',\n'

        sentence = sentence[:-2] + '.'
        return sentence
    else:
        return ""



if __name__ == '__main__':
    
    import argparse as ap

    parser = ap.ArgumentParser()
    parser.add_argument('-n', type=int, default=30, help='n: Number of activities')
    parser.add_argument('-q', type=int, default=1, help='q: Query type')
    parser.add_argument('-f', type=str, default = 'j301_1.sm', help='filename of the instance')
    args = parser.parse_args()

    from read_files import read_instance
    from definitions import Instance,IIS,Query,Explanation

    translate_explanations(args.f,args.n)
    