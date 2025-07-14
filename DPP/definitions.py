"""
Roger X. Lera-Leri
2025/04/23
"""
import numpy as np
from docplex.mp.model import Model
import pandas as pd
import cplex
import csv

class Skill:
    """
    This class stores the information about skills and its level.
    """

    def __init__(self,id,name,level):
        self.id = id
        self.name = name
        self.level = level

    def __str__(self):
        string_ = f"{self.id}"
        return string_
    
    def __repr__(self) -> str:
        return self.id

    def check_skill(self,skill_list):
        """
            This function checks if a given skill is in a list and returns the skill
            and its level or the self skill and level 0 if it is not found
        """
        for s in skill_list:
            if s.id == self.id: #skill found in list returning level
                return s,s.level
        
        return self,0 # skill not found, returning level 0
    
    def add_skill(self,skill_list):
        """
            This function adds a given skill in a list and updates it's level if it is higher
        """
        s,lev_ = self.check_skill(skill_list)
        if lev_ == 0: #skill not found
            skill_list.append(self)
        else: #skill found, check level and update
            if self.level > s.level: #update
                skill_list.remove(s)
                skill_list.append(self)


class Unit:
    """
    This class stores the information about units and its methods.
    """

    def __init__(self,id,name,credits=10,core=False):
        self.id = id
        self.name = name
        self.skills = {} #skills obtained after completing activity
        self.prerequisites = [] #units required to do the activity
        self.credits = credits #time slots to complete the activity
        self.core = core
        self.seasons = [] #semesters offered
    
    def __str__(self):
        string_ = f"{self.id}"        
        return string_
    
    def __repr__(self) -> str:
        return self.id
    
class Semester:
    """
    This class stores the information about semesters.
    """
    def __init__(self,id,season,credits=40):
        self.id = id
        self.season = season
        self.credits = credits
    
    def __str__(self):
        return f"{self.id}"
    
    def __repr__(self) -> int:
        return self.id

    
    
class Major:
    """
    This class stores the information about a major.
    """
    def __init__(self,id,name):
        self.id = id
        self.name = name
        self.core = []
        self.electives = []
    
    def __str__(self) -> float:
        return f"{self.id}"
    
    def __repr__(self) -> int:
        return self.id
    

class Course:
    """
    This class stores the information about a major.
    """
    def __init__(self,id,name,credits=240):
        self.id = id
        self.name = name
        self.core = []
        self.credits = credits
        self.semesters = []
        self.seasons = []
        self.units = {}
        self.majors = {}
    
    def __str__(self) -> float:
        return f"{self.id}"
    
    def __repr__(self) -> int:
        return self.id


    
class Job:
    """
    This class stores the information about Jobs and its methods.
    """

    def __init__(self,id,name,descriptor=None):
        self.id = id
        self.name = name
        self.descriptor = descriptor
        self.skills = {} #skills needed for obtaining the job

    def __str__(self):
        string_ = f"Job: {self.name} ({self.id})"
        return string_
    
    def __repr__(self) -> int:
        return self.id


class Variable:
    """
    This class stores the information about the variables.
    """
    def __init__(self,id:int,category:str):
        self.id = id
        self.category = category
        self.elements = []
    
    def __str__(self) -> str:
        return f"{self.id}"
    
    def __repr__(self) -> str:
        return self.id

    def solve(self):
        return self.id

class Constraint:
    """
    This class stores the information about the constraints.
    """
    def __init__(self,id:int,category:str):
        self.id = id
        self.category = category
        self.elements = {}
        self.scope = {}
        
    def name(self) -> str:
        if self.category == 'query':
            return 'q'
        elif self.category == 'max':
            return 'm'
        elif self.category == 'completion':
            u = self.elements['unit']
            return f'c:{u.id}'
        elif self.category == 'offer':
            u = self.elements['unit']
            season = self.elements['season']
            return f'o:{u.id}/{season}'
        elif self.category == 'credits':
            l = self.elements['semester']
            return f'cred:{l.id}'
        elif self.category == 'precedence':
            u = self.elements['unit']
            p_list = self.elements['predecessors']
            p_str = ", ".join(p_list)
            return f'p:{u.id}/{p_str}'
        elif self.category == 'core':
            u = self.elements['unit']
            return f'core:{u.id}'
        elif self.category == 'major_completion':
            return f'major'
        elif self.category == 'major_core':
            u = self.elements['unit']
            m = self.elements['major']
            return f'm_c:{u.id}/{m.id}'
        elif self.category == 'major_electives':
            m = self.elements['major']
            e_list = self.elements['electives']['units']
            e_str = ", ".join(e_list)
            return f'm_e:{m.id}/{e_str}'
        elif self.category == 'unit_skill':
            s = self.elements['skill']
            lev = self.elements['level']
            return f'u_s:{s.id}/{lev}'
        elif self.category == 'skill_level':
            s = self.elements['skill']
            return f'skill:{s.id}'
        else:
            return self.id
        
    def translate(self,I,df) -> str: 
        from translate import translate_reason
        
        translation = translate_reason(self,I,df)
        return translation
    
    def __str__(self) -> str:
        return f"{self.id}"
    
    def __repr__(self) -> str:
        return self.id

class Objective:
    """
    This class stores the information about the constraints.
    """
    def __init__(self,id:int):
        self.id = id
        self.scope = {}
        
    
    def __str__(self) -> str:
        return f"{self.id}"
    
    def __repr__(self) -> str:
        return self.id


class Instance:
    """
    This class stores the information about the instance.
    """
    def __init__(self,id,course = None, job = None, skills = None, max_level:int = 7):
        self.id = id
        self.course = course
        self.job = job
        self.skills = skills
        self.max_level = max_level
        self.variables = {}
        self.var_keys = {}
        self.constraints = {}
        self.con_keys = {}
        self.objective = None
        self.model = Model()
        self.model_lp = Model()
        self.solution_values = {}
        self.objective_value = None
        self.solving_time = None
        self.job_affinity = None
        
    
    def __str__(self) -> str:
        return f"{self.id}"
    
    def __repr__(self) -> int:
        return self.id

    def build_model(self):
        from formalisation import decision_variables,constraint_generation
        decision_variables(self)
        constraint_generation(self)
        return None


    def solve(self,solution_time:int = 60,log:bool = False,n_threads:int=1):
        self.build_model()
        from formalisation import objective_generation
        objective_generation(self)
        self.model.parameters.timelimit = solution_time
        self.model.parameters.threads = n_threads
        self.model.solve(log_output=log)
        return None

    def solve_lp(self,solution_time:int = 60,log:bool = False):
        from formalisation import objective_generation_lp,decision_variables_lp,constraint_generation_lp
        decision_variables_lp(self)
        constraint_generation_lp(self)
        objective_generation_lp(self)
        self.model_lp.parameters.timelimit = solution_time
        self.model_lp.solve(log_output=log)
        return None
    
    def compute_job_affinity_old(self):
    
        from formalisation import get_variables,get_var_keys
        
        S = self.job.skills
        vark = self.var_keys
    
        _,_,_,z_vars,_ = get_var_keys(self.variables)
        z = get_variables(self.model,'z',z_vars)
        sum = 0
        den = 0
        for s_id,s in S.items():
            
            i = vark[('z',s.id)]
            if s.id in self.job.skills.keys():
                t_s = self.job.skills[s.id].level
            else:
                t_s = 0
            try:
                sum += np.abs(t_s + z[i].solution_value)
            except AttributeError:
                sum += np.abs(t_s + z[i])
            den += np.abs(t_s)
            
        return (sum/den)*100
    
    def compute_job_affinity(self):
    
        from formalisation import get_variables,get_var_keys
        
        S = self.job.skills
        vark = self.var_keys
    
        _,_,y_vars,_,_ = get_var_keys(self.variables)
        y = get_variables(self.model,'y',y_vars)
        sum = 0
        den = 0
        for i in y.keys():
            sum += y[i].solution_value

        for s_id,s in S.items():
            den += s.level
            
        return (sum/den)*100

    def solution(self):

        from formalisation import get_variables,get_var_keys
        f_ = self.model.objective_value
        x_vars,v_vars,_,_,_ = get_var_keys(self.variables)
        x = get_variables(self.model,'x',x_vars)
        v = get_variables(self.model,'v',v_vars)
        
        x_ = {}
        for key,item in x.items():
            x_.update({key:item.solution_value})
        v_ = {}
        for key,item in v.items():
            x_.update({key:item.solution_value})
        t_ = self.model.solve_details.time
        self.job_affinity = self.compute_job_affinity()
        return {'objective_value':f_,'x':x_,'v':v_,'solving_time':t_}

    def order_list(self):

        from formalisation import get_var_keys
        def order_criteria(tuple_):
            return tuple_[1].id

        sol = self.solution()
        x_vars,_,_,_,_ = get_var_keys(self.variables)
        x = sol['x']
        sol_list = []
        for i in x_vars:
            if x[i] >= 0.9:
                el = self.variables[i].elements
                sol_list += [(el[0],el[1])]
        
        sol_list.sort(key=order_criteria)
        return sol_list
                

    def print_solution(self):
        sol = self.solution()
        keys = list(self.variables.keys())
        print("------------------------------------------")
        print("---------------- Solution ----------------")
        print("------------------------------------------")
        x = sol['x']
        list_ = self.order_list()
        for i in range(len(list_)):
            print(f"{i}. Subject: ({list_[i][0].id}) {list_[i][0].name}, Semester: {list_[i][1].id} ")

        alpha = self.compute_job_affinity()
        print(f"Objective value: {sol['objective_value']}")
        print(f"Job affinity: {alpha:.3f}")
        print(f"Solving time: {sol['solving_time']:.3f}")

        return None
    
    def read_solution(self,file_path):
        from read_files import read_solution_file
        solution,self.objective_value,self.solving_time,self.job_affinity = read_solution_file(file_path)
        var_dict = self.var_keys
        for unit,t in solution.items():
            index = var_dict[(unit,t)]
            self.solution_values.update({index:[unit,t]})
            
        return None

class Query:
    """
        This class stores the information about the query.
    """
    def __init__(self,id:int,category:int):
        self.id = id
        self.category = category
        self.elements = []
        self.scope = {}
        self.translation = ""
    
    def __str__(self) -> str:
        return f"{self.id}"
    
    def __repr__(self) -> str:
        return self.id

    def query_transcription(self,I):
        """
        This function encodes the queries into the model
        """
        from queries import query_transcription_
        query_transcription_(self,I)
        return None
    
    def print_query(self):
        print(f"Query: {self.category}")
        for el in self.elements:
            print(f"Query element: {el[0].id},{el[1].id}")
        for var in self.scope.keys():
            print(f"Query scope: {var}")

        return None
    
    def save_query(self,filename:str):

        with open(filename,'w') as f:
            f.write(f"Query: {self.category} \n")
            for el in self.elements:
                f.write(f"Query element: {el[0].id},{el[1].id} \n")
            for var in self.scope.keys():
                f.write(f"Query scope: {var} \n")

        return None

    
    def read_query(self,I,filename):
        
        with open(filename,'r') as f:
            lines = f.readlines()

        U = I.course.units
        L = I.course.semesters
        for l in lines[1:]:
            info_type = l.split(':')[0]
            array_ = l.split(':')[1:]
            if info_type == 'Query element':
                unit_id = array_[0].split(',')[0].strip(' ')
                u = U[unit_id]
                l_id = array_[0].split(',')[1].strip(' ')
                l = L[int(l_id)-1]
                self.elements += [[u,l]]
        from queries import query_transcription_
        query_transcription_(self,I)
        return None


    def translate(self,df_q) -> str:
        from translate import translate_query
        try:
            self.translation = translate_query(self,df_q)
        except:
            self.translation = ''
        return self.translation


class IIS:
    """
    This class stores the information about the query.
    """
    def __init__(self,id,instance,query):
        self.id = id
        self.query = query
        self.instance = instance
        self.computed = False
        self.constraints = {}
        self.solution_time = None
        self.optimality = None
    
    def __str__(self) -> str:
        return f"{self.id}"
    
    def __repr__(self) -> str:
        return self.id

    def query_optimality(self):
        """
        This function returns whether the query problem is optimal, suboptimal or infeasible
        """
        if self.computed == False:
            raise AttributeError(f"IIS has not been computed.")

        if len(self.constraints.keys()) == 0:
            self.optimality = 'optimal'
            return None

        for i,con in self.constraints.items():
            if con.category == 'max':
                self.optimality = 'suboptimal'
                return None

        self.optimality = 'infeasible'
        return None

    def compute(self,e,time_limit=None,conflict_algorithm: int = 0,n_threads:int=1):
        """
        This function encodes the queries into the model
        """
        from iis import maximality_constraint,compute_IIS
        maximality_constraint(self,e)
        self.instance.model.parameters.conflict.display = 2
        if time_limit != None:
            self.instance.model.parameters.timelimit = time_limit
            self.instance.model.parameters.threads = n_threads
            self.instance.model.parameters.conflict.algorithm = conflict_algorithm
        compute_IIS(self)
        self.computed = True
        self.query_optimality()
        return None


    def print_iis(self):
        """
        This function print the IIS
        """
        print('IIS generation')
        print(f"Instance: {self.instance.id}")
        print(f"----------------------------")
        print(f"Query: {self.query.category}")
        for elem in self.query.elements:
            str_ = ''
            if isinstance(elem,list):
                for e in elem:
                    str_ += f'{e.id},'
            else:
                str_ += f'{elem},'
            print(f"Query element: {str_[:-1]}")
        for i,el in self.query.scope.items():
            print(f"Query scope: {i}")

        print(f"----------------------------")

        opt_ = self.optimality
        print(f"IIS optimality: {opt_}")
        print(f"IIS solution time: {self.solution_time:.3f}")
        for i,con in self.constraints.items():
            str_ = '{'
            for key,item in con.elements.items():
                if isinstance(item,list):
                    str_ += f'{key}:['
                    for e in item:
                        str_ += f"{e},"
                    str_ = str_[:-1] + '],'
                else:
                    str_ += f"{key}:{item},"
            str_ = str_[:-1] + '}'
            print(f"IIS Constraint: {i}; {con.category}; {str_}")
        
    def read(self,filename):
        from iis import read_iis

        read_iis(self,filename)
        I = self.instance
        q = self.query
        if self.computed == False:
            return None
        q.query_transcription(I)
        from iis import maximality_constraint
        maximality_constraint(self)
        I = self.instance
        con = I.constraints

        for i in self.constraints.keys():
            c = con[i]
            self.constraints.update({i:c})
        
        return None

