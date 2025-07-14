import argparse as ap
import pandas as pd
import numpy as np
import json
import os
import re


def read_query(job:str,q:int=1,i:int=0):
    """
        We read the question to answer:
        INPUT: file
    """
    file = f"question-{job}-{i}.txt"
    filepath = os.path.join(os.getcwd(),'queries',f"{q}",f"{file}")
    query = ''
    with open(filepath,'r') as fileob:
        lines = fileob.readlines()
        for l in lines:
            label = l.split(';')[0]
            if label == 'query':
                query = l.split(';')[1].strip('\n')
                break

    return query

def read_partialsol(job:str,q:int,i:int):
    """
        This function reads the partial solution and build a table
    """
    instance = f"{job}-{q}-{i}"
    partialsol_dir = os.path.join(os.getcwd(),'partialsol',f'q{q}')
    filepath = os.path.join(partialsol_dir,f'{instance}.csv')
    df = pd.read_csv(filepath,delimiter=';')
    
    cols = list(df.columns.copy())

    max_length_per_col = {col:len(col) for col in cols}
    for i in range(len(df)):
        for col in cols:
            item = str(df[col].iloc[i])
            if len(item) > max_length_per_col[col]:
                max_length_per_col[col] = len(item)

    max_length_per_col = {key:val+2 for key,val in max_length_per_col.items()}
    header = ''
    horizontal_line = ''
    for col in cols:
        header += f'| {col}'
        len_ = len(col)
        extra_spaces = max_length_per_col[col] - len_ - 1
        for i in range(extra_spaces):
            header += ' '
        horizontal_line += '|'
        for i in range(max_length_per_col[col]):
            horizontal_line += '-'
    header += '|'
    horizontal_line += '|'

    lines = [header,horizontal_line]
    for i in range(len(df)):
        line = ''
        for col in cols:
            str_ = str(df[col].iloc[i])
            line += f'| {str_}'
            len_ = len(str_)
            extra_spaces = max_length_per_col[col] - len_ - 1
            for j in range(extra_spaces):
                line += ' '

        line += '|'
        lines += [line]

    return lines

def read_completesol(job:str,q:int,i:int):
    """
        This function reads the complete solution and build a table
    """
    instance = f"{job}-{q}-{i}"
    completesol_dir = os.path.join(os.getcwd(),'completesol',f'q{q}')
    filepath = os.path.join(completesol_dir,f'{instance}.csv')
    df = pd.read_csv(filepath,delimiter=';')
    
    cols = list(df.columns.copy())

    max_length_per_col = {col:len(col) for col in cols}
    for i in range(len(df)):
        for col in cols:
            item = str(df[col].iloc[i])
            if len(item) > max_length_per_col[col]:
                max_length_per_col[col] = len(item)

    max_length_per_col = {key:val+2 for key,val in max_length_per_col.items()}
    header = ''
    horizontal_line = ''
    for col in cols:
        header += f'| {col}'
        len_ = len(col)
        extra_spaces = max_length_per_col[col] - len_ - 1
        for i in range(extra_spaces):
            header += ' '
        horizontal_line += '|'
        for i in range(max_length_per_col[col]):
            horizontal_line += '-'
    header += '|'
    horizontal_line += '|'

    lines = [header,horizontal_line]
    for i in range(len(df)):
        line = ''
        for col in cols:
            str_ = str(df[col].iloc[i])
            line += f'| {str_}'
            len_ = len(str_)
            extra_spaces = max_length_per_col[col] - len_ - 1
            for j in range(extra_spaces):
                line += ' '

        line += '|'
        lines += [line]

    return lines

def read_reasons(job:str,q:int=1,i:int=1):
    """
        We read the reasons to answer:
        INPUT: file
    """
    f = f"reasons-{job}-{q}-{i}.json"
    filepath = os.path.join(os.getcwd(),'reasons',f"q{q}",f"{f}")
    try:
        with open(filepath,'r') as fileob:
            reasons = json.load(fileob)
        
    except:
        raise(FileNotFoundError(f"File {filepath} does not exist."))
        
    return reasons

def build_sequence(job:str,q:int=1,i:int=0):

    query = read_query(job,q,i)
    reasons = read_reasons(job,q,i)
    partialsol = read_partialsol(job,q,i)

    prompt = f'Answer the following question about an activity schedule using the reasons bellow. \n'
    prompt = f"The bachelor's degree planning problem is the problem of finding a planning of university subjects that respect some precedence and university restrictions while maximising the skills learnt. Specifically, the goal is to acquire the required level for the student's desired job role by coursing subjects. In this context, provide an explanation to answer the following question about the solution of 6-semester bachelor's degree planning problem. To do so, use the reasons below, which are related to the bachelor's degree restrictions. \n"
    prompt += f'Partial Solution: \n'
    for line in partialsol:
        prompt += f'{line} \n'
    prompt += f'\nQuestion: {query} \n'
    counter = 0
    prompt += f'Reasons: \n'
    for rid,r in reasons.items():
        prompt += f'{counter}: {r} \n'
        counter += 1

    instructions = 'Answer only with a short explanation, nothing else. Do not refer to the number of the reason. '
    instructions = '\nWrite a brief explanation without listing reasons and do not refer to the number of the reason. \n'

    return prompt+instructions

def read_graph(job:str,q:int=1,i:int=0):
    """
        We read the graph :
        INPUT: file
    """

    filepath = os.path.join(os.getcwd(),'graph',f"q{q}")
    edgesfile = os.path.join(filepath,f'{job}-{q}-{i}-edges.npy')
    orderfile = os.path.join(filepath,f'{job}-{q}-{i}-order.npy')
    labelfile = os.path.join(filepath,f'{job}-{q}-{i}-labels.json')

    edges = np.load(edgesfile)
    order = np.load(orderfile)

    with open(labelfile,'r') as fileob:
        labels = json.load(fileob)

    return edges,order,labels

def build_prompt(job:str,q:int=1,i:int=0):
    """
    We build the graph prompt to the LLMs
    """
    
    query = read_query(job,q,i)
    reasons = read_reasons(job,q,i)
    partialsol = read_partialsol(job,q,i)

    edges,order,labels = read_graph(job,q,i)
    translation = {int(lid):reasons[l] for lid,l in labels.items()}


    prompt = f'Answer the following question about an activity schedule using the reasons bellow. Such reasons are connected to each other like nodes in a graph. Use the reasons and their connections to write an answer. \n'
    prompt = f"The bachelor's degree planning problem is the problem of finding a planning of university subjects that respect some precedence and university restrictions while maximising the skills learnt. Specifically, the goal is to acquire the required level for the student's desired job role by coursing subjects. In this context, provide an explanation to answer the following question about the solution of 6-semester bachelor's degree planning problem. To do so, use the reasons below, which are related to the bachelor's degree restrictions. Moreover, such reasons are connected to each other like nodes in a graph. Use the reasons and their connections to write the explanation. \n"
    prompt += f'Partial Solution: \n'
    for line in partialsol:
        prompt += f'{line} \n'
    prompt += f'\nQuestion: {query} \n'
    
    prompt += f'Reasons: \n'
    connections = []
    store_edges = []
    for i in range(len(order)):
        index = order[i]
        prompt += f'{i}: {translation[index]} \n'
        for j in range(len(edges)):
            e0,e1 = edges[j][0],edges[j][1]
            if (e0,e1) in store_edges:
                continue
            if e0 == index or e1 == index:
                new_e0 = list(order).index(e0)
                new_e1 = list(order).index(e1)
                if new_e0 < new_e1:
                    connections += [f'({new_e0}-{new_e1}) \n']
                else:
                    connections += [f'({new_e1}-{new_e0}) \n']
                store_edges.append((e0,e1))
                store_edges.append((e1,e0))

    prompt += f'Connections: \n'
    prompt += ''.join(connections)
    instructions = '\nAnswer only with a short explanation, nothing else. Do not refer to the number of the reason. '

    instructions = '\nWrite a brief explanation without listing reasons and do not refer to the number of the reason. \n'
    return prompt+instructions

def build_prompt_llm(job:str,q:int=1,i:int=0):
    """
    We build the graph prompt to the LLMs
    """
    
    query = read_query(job,q,i)
    
    completesol = read_completesol(job,q,i)

    prompt = f"The bachelor's degree planning problem is the problem of finding a bachelor's degree plan of university subjects that respect some precedence and university restrictions (e.g., subjects can only be completed once, subjects are offered in particular semesters, there are compulsory subjects, and not to plan more than 40 credits per semester) while maximising the skills learnt. Specifically, the goal is to acquire the required level for the student's desired job role by coursing subjects. In this context, provide an explanation to answer the following question about the solution of 6-semester bachelor's degree planning problem. To do so, reason about the provided solution and the restrictions of a bachelor's degree. \n"
    prompt += f'Solution: \n'
    for line in completesol:
        prompt += f'{line} \n'
    prompt += f'\nQuestion: {query} \n'
    
    
    instructions = '\nWrite a brief explanation without listing reasons. \n'
    return prompt+instructions

def write_prompt(prompt:str,job:str,q:int=1,i:int=0,seq:bool=False,llm_only:bool=False):

    prompt_dir = os.path.join(os.getcwd(),'chatgpt',f"q{q}")
    prompt_list = prompt.split('\n')
    if seq:
        filename = f'{job}-{q}-{i}-s.txt'
    else:
        filename = f'{job}-{q}-{i}.txt'

    if llm_only:
        filename = f'{job}-{q}-{i}-llm.txt'

    """
    with open(os.path.join(prompt_dir,filename),'w') as f:
        for l in prompt_list:
            f.write(l)
    """
    with open(os.path.join(prompt_dir,filename),'w') as f:
        f.write(prompt)
    
    return None


def loop():

    for q in range(1,args.nq + 1):
        folder_dir = os.path.join(os.getcwd(),'reasons',f"q{q}")
        
        for f in os.listdir(folder_dir):
            file_id = f.split('.')[0].split('-')[1:]
            j = file_id[0]
            i = int(file_id[2])
            #prompt_g = build_prompt(j,q,i)
            #prompt_s = build_sequence(j,q,i)
            #write_prompt(prompt_g,j,q,i)
            #write_prompt(prompt_s,j,q,i,True)
            prompt = build_prompt_llm(j,q,i)
            write_prompt(prompt,j,q,i,llm_only=True)
            
    return None

if __name__ == '__main__':

    
    parser = ap.ArgumentParser()
    parser.add_argument('--description', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'description.txt'))
    parser.add_argument('--embeddings', type=str, default='small', choices=['small', 'large'])
    parser.add_argument('--temperature', type=float, default=0) # should be 0 <= t <= 2 for OpenAI, 0 <= t <= 1 for Mistral AI
    parser.add_argument('-j', type=str, default='104')
    parser.add_argument('-q', type=int, default=1)
    parser.add_argument('-i', type=int, default=3)
    parser.add_argument('--nq', type=int, default=10)
    parser.add_argument('--ni', type=int, default=5)
    parser.add_argument('-s', action='store_true',help='s: sequence true, graph false')
    args, additional = parser.parse_known_args()
    
    
    print(build_prompt(args.j,args.q,args.i))
    