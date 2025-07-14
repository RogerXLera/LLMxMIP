
import numpy as np
from docplex.mp.model import Model
import cplex
import csv

class Resource:
    """
    This class stores the available information about the resource
    and its availability.
    """

    def __init__(self,id:int,units:int,renewable:bool=True,nonrenewable:bool=False):
        self.id = id
        self.units = units
        self.renewable = renewable
        self.nonrenewable = nonrenewable

    def __str__(self) -> str:
        return f"{self.id}"
    
    def __repr__(self) -> int:
        return self.id

class Activity:
    """
    This class stores the information about the activities.
    """

    def __init__(self,id:int,duration:int):
        self.id = id
        self.duration = duration
        self.predecessors = []
        self.successors = []
        self.ef_time = 0
        self.lf_time = self.ef_time + self.duration
        self.resources = {}


    def __str__(self) -> str:
        return f"{self.id}"
    
    def __repr__(self) -> int:
        return self.id


class Project:
    """
    This class stores the information about the project in itself.
    """
    def __init__(self,id:int,horizon:int = 100,makespan_ub:int = 100):
        self.id = id
        self.activities = []
        self.resources = []
        self.makespan_ub = makespan_ub
        self.horizon = horizon
        
    
    def __str__(self) -> str:
        return f"{self.id}"
    
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
        self.ind = []
        self.lhs = []
        self.rhs = 0
        self.rel = None
        
    
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
    def __init__(self,id,project = None):
        self.id = id
        self.project = project
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
        
    
    def __str__(self) -> str:
        return f"{self.id}"
    
    def __repr__(self) -> int:
        return self.id

    def build_model(self):
        from formalisation import decision_variables,constraint_generation
        decision_variables(self)
        constraint_generation(self)
        return None
    

    def build_constraints(self):
        from formalisation import decision_variables_dict,constraint_generation_dict
        decision_variables_dict(self)
        constraint_generation_dict(self)
        return None


    def solve(self,solution_time:int = 60,log:bool = False):
        self.build_model()
        from formalisation import objective_generation
        objective_generation(self)
        self.model.parameters.timelimit = solution_time
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

    def solution(self):

        from formalisation import get_variables
        f_ = self.model.objective_value
        var = self.variables
        keys = list(var.keys())
        x = get_variables(self.model,'x',keys)
        x_ = {}
        for key,item in x.items():
            x_.update({key:item.solution_value})
        t_ = self.model.solve_details.time
        return {'objective_value':f_,'x':x_,'solving_time':t_}

    def order_list(self):

        def order_criteria(tuple_):
            return tuple_[1]

        sol = self.solution()
        keys = list(self.variables.keys())
        x = sol['x']
        sol_list = []
        for i in keys:
            if x[i] >= 0.9:
                el = self.variables[i].elements
                sol_list += [[el[0],el[1]]]
        
        #return sol_list.sort(key=order_criteria)
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
            print(f"{i}. Activity: {list_[i][0].id} t: {list_[i][1]} EF: {list_[i][0].ef_time}")

        print(f"Objective value: {sol['objective_value']}")
        print(f"Solving time: {sol['solving_time']:.3f}")

        return None
    
    def read_solution(self,file_path):
        from read_files import read_solution_file
        solution,self.objective_value,self.solving_time = read_solution_file(file_path)
        var_dict = self.var_keys
        for act,elem in solution.items():
            index = var_dict[(act,elem[0])]
            self.solution_values.update({index:[act,elem[0]]})
            
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
        from queries_dict import query_transcription_
        query_transcription_(self,I)
        return None
    
    def read(self,I,filename):

        A = I.project.activities

        with open(filename,'r') as f:
            lines = f.readlines()
        if len(lines) == 0:
            raise f"No query for this instance."
        first_line = lines[0]
        if "Instance" not in first_line:
            raise f"No query for this instance."

        for l in lines[1:]:
            info_type = l.split(':')[0]
            array_ = l.split(':')[1:]
            if info_type == 'Query':
                el = array_[0].strip()
                self.category = int(el)

            elif info_type == 'Query element':
                list_ = array_[0].split(',')
                if self.category == 11:
                    self.elements += [[list_[0],int(list_[1]),int(list_[2])]]
                else:
                    a = A[int(list_[0])-1]
                    self.elements += [[a,int(list_[1])]]
                
        return None


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


    def compute(self,e,time_limit=None,n_threads:int=1):
        """
        This function encodes the queries into the model
        """
        
        from iis import maximality_constraint,compute_IIS
        maximality_constraint(self,e)
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
                    str_ += f'{e},'
            else:
                str_ += f'{elem},'
            print(f"Query element:{str_[:-1]}")
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

