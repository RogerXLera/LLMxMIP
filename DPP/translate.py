"""
Author: Roger X. Lera Leri
Date: 2024/04/01
"""
import numpy as np
import pandas as pd
import copy
import os

def translate_query_1(q,template):

    u,l = q.elements[0]
    
    template = template.replace('{u}',str(u.name)).replace('{l}',str(l.id))
    return template

def translate_query_2(q,template):

    u,l = q.elements[0]
    
    template = template.replace('{u}',str(u.name)).replace('{l}',str(l.id))
    return template

def translate_query_3(q,template):

    u,l = q.elements[0]
    
    template = template.replace('{u}',str(u.name)).replace('{l}',str(l.id))
    return template

def translate_query_4(q,template):

    u,l = q.elements[0]
    
    template = template.replace('{u}',str(u.name)).replace('{l}',str(l.id))
    return template

def translate_query_5(q,template):

    u,l = q.elements[0]
    
    template = template.replace('{u}',str(u.name))
    return template

def translate_query_6(q,template):

    u,l = q.elements[0]
    
    template = template.replace('{u}',str(u.name))
    return template

def translate_query_7(q,template):

    U_list = [str(elem[0].name) for elem in q.elements]
    U = ", ".join(U_list)
    l = q.elements[0][1]
    template = template.replace('{U}',U).replace('{l}',str(l.id))
    return template

def translate_query_8(q,template):

    U_list = [str(elem[0].name) for elem in q.elements]
    U = ", ".join(U_list)
    l = q.elements[0][1]
    template = template.replace('{U}',U).replace('{l}',str(l.id))
    return template


def translate_query_9(q,template):

    u,l = q.elements[0]
    u_,t_ = q.elements[1]
    
    template = template.replace('{u}',str(u.name)).replace('{l}',str(l.id))
    template = template.replace('{u_}',str(u_.name))
    return template

def translate_query_10(q,template):

    u,l = q.elements[0]
    u_,l_ = q.elements[1]
    
    template = template.replace('{u}',str(u.name)).replace('{u_}',str(u_.name))
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

    n_queries = 10
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

def translate_completion(r,I,template):
    u = r.elements['unit']

    template = template.replace('{u}',str(u.name))
    return template

def translate_offer(r,I,template):
    u = r.elements['unit']
    sea = r.elements['season']

    seasons_dict = {'au':'autumn','sp':'spring'}

    template = template.replace('{u}',str(u.name))
    return template.replace('{season}',str(seasons_dict[sea]))

def translate_credits(r,I,template):
    l = r.elements['semester']
    
    template = template.replace('{n_credits}',str(l.credits))
    return template.replace('{l}',str(l.id))


def translate_precedence(r,I,template):
    u = r.elements['unit']
    pred = r.elements['predecessors']
    U = I.course.units
    U_list = []
    for p in pred:
        if p in U.keys():
            U_list += [U[p].name]
    
    U_str = ""
    for i in range(len(U_list)):
        u_str = U_list[i]
        if len(U_list) == 1:
            U_str += u_str
        elif i == len(U_list) - 1:
            U_str += f" or {u_str}"
        else:
            U_str += f"{u_str}, "

    template = template.replace('{u}',str(u.name)).replace('{pred}',str(U_str))
    return template

def translate_core(r,I,template):
    u = r.elements['unit']
    
    template = template.replace('{u}',str(u.name))
    return template

def translate_major_completion(r,I,template):

    return template

def translate_major_core(r,I,template):
    u = r.elements['unit']
    m = r.elements['major']
    
    template = template.replace('{u}',str(u.name))
    return template.replace('{m}',str(m.name))

def translate_major_electives(r,I,template):
    electives = r.elements['electives']
    m = r.elements['major']
    U = I.course.units

    index_ = 0
    U_list = []
    for elec in m.electives:
        bool_ = False #if this electives count
        for u_ in elec['units']:
            if u_ in electives['units']:
                bool_ = True
                if u_ in U.keys():
                    U_list.append(U[u_].name)

        if bool_:
            break

        index_ += 1

    elec_object = m.electives[index_]
    n_courses = elec_object['count']

    U_str = ", ".join(U_list)
    
    template = template.replace('{n_units}',str(n_courses)).replace('{U}',str(U_str))
    return template.replace('{m}',str(m.name))

def translate_unit_skill(r,I,template):
    
    s_ = r.elements['skill']
    lev = r.elements['level']

    U = I.course.units
    S = I.skills
    try:
        s = S[s_.id]
    except:
        s = s_


    
    U_list = []
    for u_id,u in U.items():
        if s.id in u.skills.keys():
            if u.skills[s.id].level >= s.level:
                U_list.append(u.name)
        
    if len(U_list) == 0:
        return f"There is no course that teaches level {lev} of skill {s.name}"
    
    U_str = ""
    for i in range(len(U_list)):
        u_str = U_list[i]
        if len(U_list) == 1:
            U_str += u_str
        elif i == len(U_list) - 1:
            U_str += f" or {u_str}"
        else:
            U_str += f"{u_str}, "
    
    template = template.replace('{s}',str(s.name)).replace('{lev}',str(lev))
    return template.replace('{U}',str(U_str))

def translate_skill_level(r,I,template):

    s_ = r.elements['skill']
    
    S = I.skills
    
    try:
        s = S[s_.id]
    except:
        s = s_


    template = template.replace('{s}',str(s.name)).replace('{lev}',str(s_.level))
    return template.replace('{job}',str(I.job.name))


def translate_max(r,I,template):
    ja = f"{I.job_affinity:.0f}"
    template = template.replace('{job_affinity}',ja)
    return template

def translate_reason(r,I,df_c):
    con_type = r.category
    template = df_c[df_c['constraint'] == con_type]['text'].iloc[0]
    function = globals().get(f"translate_{con_type}")
    translation = function(r,I,template)
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
    