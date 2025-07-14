"""
Roger X. Lera-Leri
2024/04/23
"""
import json
import os
import numpy as np
import argparse as ap
from definitions import *


def read_json(filepath):
    """
    This function reads a json file and return the contents in a dictionary.
    """
    with open(filepath,'r',encoding="utf8") as inputfile:
        data = json.loads(inputfile.read())
    return data

def read_docs(files):
    """
    Read all the files extracting all the dictionaries
    """
    
    file1 = files[0]
    file2 = files[1]
    file3 = files[2]
    file4 = files[3]
    
    
    courses = read_json(file1)
    jobs = read_json(file2)
    sfia = read_json(file3)
    units = read_json(file4)
    
    return courses,jobs,sfia,units

def core_dict(course):
    
    majors = {}
    core = {}
    for elem in course['core']:
        core.update({elem['id']:elem['semester']})
    for elem in course['majors']:
        element_dict = {'name':elem['name'],
                        'core':elem['core'],
                        'electives':elem['electives']}
        majors.update({elem['id']:element_dict})
        
    return core,majors
    
def units_dict(units,U_core,M_a,credits_ = 10):
    """
    Organise all the information of the units: id, name, 
    prerequisites, skills, offer and credits
    """
    units_dict = {}
    i = 1
    for unit in units:
        
        core_ = False
        if unit['id'] in U_core.keys():
            core_ = True

        unit_el = Unit(id=unit['id'],name=unit['name'],credits=credits_,core=core_)
        for s in unit['sfiaSkills']:
            skill = Skill(id=s['id'],name=s['id'],level=s['level'])
            unit_el.skills.update({s['id']:skill})

        #unit_el.prerequisites = unit['prerequisites']
        prereq_list = []
        for prereq in unit['prerequisites']:
            if isinstance(prereq,list):
                prereq_list.append(prereq)
            else:
                prereq_list.append([prereq])

        unit_el.prerequisites = prereq_list
        unit_el.seasons = unit['offer']


        units_dict.update({unit['id']:unit_el})
        
    return units_dict

def course_dict(M_a,U_core):
    """
    This function return a course element
    """
    course = Course(id="BICT",name="Bachelor of Information and Communication Technology")
    course.core = list(U_core.keys())
    for m in M_a.keys():
        major = Major(id=m,name=M_a[m]['name'])
        major.core = M_a[m]['core']
        major.electives = M_a[m]['electives']
        course.majors.update({m:major})
    return course


def job_dict(jobs_):
    
    jobs = {}
    for j in jobs_:
        job = Job(id=j['id'],name=j['name'])
        for s in j['sfia']:
            skill = Skill(id=s['id'],name=s['id'],level=s['level'])
            job.skills.update({s['id']:skill})
        jobs.update({j['id']:job})
        
    return jobs
    
def skill_dict(skills):
    
    dict_ = {}
    for s in skills:
        skill = Skill(id=s['id'],name=s['name'],level=0)
        dict_.update({s['id']:skill})
        
    return dict_    
    
def data_dict(files):

    courses,jobs,skills,units = read_docs(files)
    U_core, M_a = core_dict(courses[0])
    U = units_dict(units,U_core,M_a,credits_=10)
    S = skill_dict(skills)
    course = course_dict(M_a,U_core)
    J = job_dict(jobs)
    return course,U,S,J

def generate_semesters(course,n:int=6,n_credits:int=40,first_season:str='au'):

    
    index_ = course.seasons.index(first_season)
    for i in range(1,n+1):
        sem = Semester(id=i,season=course.seasons[index_],credits=n_credits)
        course.semesters.append(sem)
        if index_ == len(course.seasons) - 1:
            index_ = 0
        else:
            index_ += 1
    return None

def set_max_level(skills):

    max_lev = 0
    for s_id,s in skills.items():
        if s.level > max_lev:
            max_lev = s.level

    return max_lev

def read_instance(n:int=6,credits:int=240,j:str='0',first_season:str='au',max_level:int=7):

    path = os.getcwd()
    folder = os.path.join(path,'data')
    file1 = os.path.join(folder,"courses.json")
    file2 = os.path.join(folder,"jobs.json")
    file3 = os.path.join(folder,"sfia.json")
    file4 = os.path.join(folder,"units.json")
    
    files = [file1,file2,file3,file4]
    
    course,U,S,J = data_dict(files)
    course.seasons = ['au','sp']
    course.credits = credits

    credits_per_sem = int(credits/n)

    generate_semesters(course,n,credits_per_sem,first_season)
    course.units = U

    max_level = set_max_level(J[j].skills)
    
    I = Instance(id=0,course=course,job=J[j],skills=S,max_level=max_level)

    return I



def read_solution_file(file_path):
    
    solution = {}
    f = 0.0
    t = 0.0
    with open(file_path, 'r') as f:
        data = f.readlines()
        for row in data:
            if "Subject" in row: #process activities
                activity = row.split("Subject: (")[1]
                activity_id = activity.split(")")[0]
                time = row.split("Semester: ")[1]
                time_id = time.split(" ")[0]
                solution.update({str(activity_id):int(time_id)})
            elif "Objective" in row:
                objective = row.split("Objective value: ")[1]
                f = float(objective.split(" ")[0])
            elif "Solving" in row:
                time_ = row.split("Solving time: ")[1]
                t = float(time_.split(" ")[0])
            elif "Job affinity" in row:
                time_ = row.split("Job affinity: ")[1]
                alpha = float(time_.split(" ")[0])

    return solution,f,t,alpha


if __name__ == '__main__':
    
    
    parser = ap.ArgumentParser()
    parser.add_argument('-n', type=int, default=6, help='n')
    parser.add_argument('-c', type=int, default=240, help='c')
    parser.add_argument('-l', type=int, default=7, help='l: maximum level. Default: 7')
    parser.add_argument('-j', type=str, default='0', help='Job index')
    parser.add_argument('-s', type=str, default='au', help='Start semester')
    args = parser.parse_args()


    I = read_instance(args.n,args.c,args.j,args.s,args.l)

    print(I.course,I.course.name)
    for u in I.course.units.values():
        print(u)

    for s in I.skills.values():
        print(s,s.name)

   
    print(I.job,I.job.name)
    
    
    
    
    
    
    
    
    

    