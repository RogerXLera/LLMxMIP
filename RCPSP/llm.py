import argparse as ap
import pandas as pd
import numpy as np
import json
import os
import re

#from openai import OpenAI
#emb_oaclient = OpenAI()
#llm_oaclient = OpenAI()
"""
def load_client(url:str="https://openrouter.ai/api/v1",api_key_var:str='OPENROUTE_API_KEY'):
  return OpenAI(
    base_url=url,
    api_key=os.environ[api_key_var],
    )
"""
def read_query(f:str,n:int=30,q:int=1):
    """
        We read the question to answer:
        INPUT: file
    """
    f = f"{f}-q{q}.txt"
    filepath = os.path.join(os.getcwd(),'queries',f"j{n}",f"{f}")
    query = ''
    with open(filepath,'r') as fileob:
        lines = fileob.readlines()
        for l in lines:
            label = l.split(';')[0]
            if label == 'query':
                query = l.split(';')[1].strip('\n')
                break

    return query

def read_partialsol(f:str,n:int,q:int):
    """
        This function reads the partial solution and build a table
    """
    instance = f.split('.')[0]
    partialsol_dir = os.path.join(os.getcwd(),'partialsol',f'j{n}')
    filepath = os.path.join(partialsol_dir,f'{instance}-{q}.csv')
    df = pd.read_csv(filepath,delimiter=';')

    # hardcoded to this particular problem instances, where n=32 is the final dumb activity
    resource_type = []
    resource_units = []
    for i in range(len(df)):
        act = int(df['activity'].iloc[i])


        res = df['resources'].iloc[i].strip(' ')
        if res == '-':
            res_type = '-'
            res_units = '-'
        else:
            res_type = str(res[1])
            res_units = int(res.split('(')[1].split(')')[0])
        resource_type.append(res_type)
        resource_units.append(res_units)
    
    df['resource_type'] = resource_type
    df['resource_units'] = resource_units
    
    cols = list(df.columns.copy())
    cols.remove('resources')

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

def read_completesol(f:str,n:int,q:int):
    """
        This function reads the complete solution and build a table
    """
    instance = f.split('.')[0]
    completesol_dir = os.path.join(os.getcwd(),'completesol',f'j{n}')
    filepath = os.path.join(completesol_dir,f'{instance}-{q}.csv')
    df = pd.read_csv(filepath,delimiter=';')

    # hardcoded to this particular problem instances, where n=32 is the final dumb activity
    resource_type = []
    resource_units = []
    for i in range(len(df)):
        act = int(df['activity'].iloc[i])


        res = df['resources'].iloc[i].strip(' ')
        if res == '-':
            res_type = '-'
            res_units = '-'
        else:
            res_type = str(res[1])
            res_units = int(res.split('(')[1].split(')')[0])
        resource_type.append(res_type)
        resource_units.append(res_units)
    
    df['resource_type'] = resource_type
    df['resource_units'] = resource_units
    
    cols = list(df.columns.copy())
    cols.remove('resources')

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

def read_reasons(f:str,n:int=30,q:int=1):
    """
        We read the reasons to answer:
        INPUT: file
    """
    f = f"{f}-{q}-translation.json"
    filepath = os.path.join(os.getcwd(),'reasons',f"j{n}",f"{f}")
    try:
        with open(filepath,'r') as fileob:
            reasons = json.load(fileob)
        
    except:
        raise(FileNotFoundError(f"File {filepath} does not exist."))
        
    return reasons

def build_sequence(f:str,n:int=30,q:int=1):

    query = read_query(f,n,q)
    reasons = read_reasons(f,n,q)
    partialsol = read_partialsol(f,n,q)

    prompt = f'Answer the following question about an activity schedule using the reasons bellow. \n'
    prompt = f'The project schedule problem is the problem of finding a schedule of activities that respect some precedence and resource restrictions while minimising the project completion time. In this context, provide an explanation to answer the following question about the solution of 32-activity project schedule problem. To do so, use the reasons below, which are related to the project schedule restrictions. \n'
    prompt += f'Solution: \n'
    for line in partialsol:
        prompt += f'{line} \n'
    prompt += f'Question: {query} \n'
    counter = 0
    prompt += f'Reasons: \n'
    for rid,r in reasons.items():
        prompt += f'{counter}: {r} \n'
        counter += 1

    instructions = 'Answer only with a short explanation, nothing else. Do not refer to the number of the reason. '
    instructions = '\nWrite a brief explanation without listing reasons and do not refer to the number of the reason. \n'

    return prompt+instructions

def read_graph(f:str,n:int=30,q:int=1):
    """
        We read the graph :
        INPUT: file
    """

    filepath = os.path.join(os.getcwd(),'graph',f"j{n}")
    edgesfile = os.path.join(filepath,f'{f}-{q}-edges.npy')
    orderfile = os.path.join(filepath,f'{f}-{q}-order.npy')
    labelfile = os.path.join(filepath,f'{f}-{q}-labels.json')

    edges = np.load(edgesfile)
    order = np.load(orderfile)

    with open(labelfile,'r') as fileob:
        labels = json.load(fileob)

    return edges,order,labels

def build_prompt(f:str,n:int=30,q:int=1):
    """
    We build the graph prompt to the LLMs
    """
    
    query = read_query(f,n,q)
    reasons = read_reasons(f,n,q)
    partialsol = read_partialsol(f,n,q)

    edges,order,labels = read_graph(f,n,q)
    translation = {int(lid):reasons[l] for lid,l in labels.items()}


    prompt = f'Answer the following question about an activity schedule using the reasons bellow. Such reasons are connected to each other like nodes in a graph. Use the reasons and their connections to write an answer. \n'
    prompt = f'The project schedule problem is the problem of finding a schedule of activities that respect some precedence and resource restrictions while minimising the project completion time. In this context, provide an explanation to answer the following question about the solution of 32-activity project schedule problem. To do so, use the reasons below, which are related to the project schedule restrictions. Moreover, such reasons are connected to each other like nodes in a graph. Use the reasons and their connections to write the explanation. \n'
    prompt += f'Solution: \n'
    for line in partialsol:
        prompt += f'{line} \n'
    prompt += f'Question: {query} \n'
    
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

def build_prompt_llm(f:str,n:int=30,q:int=1):
    """
    We build the prompt to using only the LLMs to provide explanations
    """
    
    query = read_query(f,n,q)
    partialsol = read_completesol(f,n,q)

    prompt = f'The project schedule problem is the problem of finding a schedule of activities that respect some precedence and resource restrictions while minimising the project completion time. In this context, provide an explanation to answer the following question about the solution of 32-activity project schedule problem. To do so, reason about the provided solution and the restrictions related to project scheduling. \n'
    prompt += f'Solution: \n'
    for line in partialsol:
        prompt += f'{line} \n'
    prompt += f'Question: {query} \n'
    
    instructions = '\nWrite a brief explanation without listing reasons. \n'
    return prompt+instructions


if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('--description', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'description.txt'))
    parser.add_argument('--llm', type=str, default='gpt-4o', choices=[
        # OpenAI
        'gpt-3.5-turbo',
        'gpt-4o',
        'gpt-4o-mini',
        # Mistral AI
        'open-mistral-7b',
        'open-mixtral-8x7b',
        'open-mixtral-8x22b',
        'mistral-small-latest',
        'mistral-large-latest',
        # DeepSeek
        'deepseek-chat',
        #OpenRoute
        'deepseek/deepseek-chat:free',
        'deepseek/deepseek-r1:free',
        'qwen/qwen-vl-plus:free',
        'google/gemini-2.0-flash-thinking-exp-1219:free',
        'meta-llama/llama-3.3-70b-instruct:free'
    ])
    parser.add_argument('--embeddings', type=str, default='small', choices=['small', 'large'])
    parser.add_argument('--temperature', type=float, default=0) # should be 0 <= t <= 2 for OpenAI, 0 <= t <= 1 for Mistral AI
    parser.add_argument('-n', type=int, default=30)
    parser.add_argument('-q', type=int, default=2)
    parser.add_argument('-f', type=str, default='j301_1.sm')
    parser.add_argument('-s', action='store_true',help='s: sequence true, graph false')
    args, additional = parser.parse_known_args()
    
   
    if args.s:
        prompt = build_sequence(args.f,args.n,args.q)
        
    else:
        prompt = build_prompt(args.f,args.n,args.q)
    
    #prompt = build_prompt_llm(args.f,args.n,args.q)
    print("PROMPT:")
    print(prompt)

    print("OUTPUT:")
    #client = load_client()
    #client = OpenAI()
   
    
    """
    completion = client.chat.completions.create(
            model=args.llm,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                    
                
                }
            ],
        )
    
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": prompt
        }
    ]
)
    
    print(completion.choices[0].message)
    """
