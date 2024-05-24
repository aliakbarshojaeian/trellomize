import uuid
import hashlib
import json
import re
import bisect
import os
from enum import Enum
from datetime import datetime , timedelta
from rich import print as rprint

def generate_unique_id():
    return str(uuid.uuid4())

def load_projectIDs(filename = "projectsID.json"):
    #
    if not os.path.exists(filename):
        return set()
    
    with open(filename, 'r') as file:
        pIDs = json.load(file)
    return set(pIDs)

def save_projectID(pID , filename = "projectsID.json"):
    #
    project_ids = load_projectIDs(filename)
    project_ids.add(pID)
    
    with open(filename, 'w') as file:
        json.dump(list(project_ids) , file , indent=4)

def projectID_availability(projectID , filename = "projectsID.json"):
    #
    project_ids = load_projectIDs(filename)
    return projectID not in project_ids

class Priority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Status(Enum):
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"
    ARCHIVED = "ARCHIVED"

#*********************************************************************************


#**************************************************************************************************
class User():

    def __init__(self , username , email , hashedPassword):
        self.username = username
        self.email = email
        self.hapassword = hashedPassword
        #self.isManager = isManager
        self.projects = {}
        self.assignedProjects = []
        self.activityStatus = "Active"
        self.loginStatus = "logged in"
        #self.isAdmin = isAdmin
    def saveUser(self):
        filename = "users/"+ self.username + ".json"
        userData = {
            "Username" : self.username ,
            "Email" : self.email ,
            "Password" : self.hapassword ,
            "activityStatus" : self.activityStatus, 
            "loginStatus" : self.loginStatus ,
            "Projects" : self.projects,
            "assignedProjects" : self.assignedProjects
        }
        
        with open(filename, 'w') as jsonFile:
            json.dump(userData, jsonFile , indent=4)

    @staticmethod
    def loadUser(username):
        filename = "users/" + username + ".json"
        #the error handling part will be complete later!!!

        with open(filename, 'r') as jsonFile:
            data = json.load(jsonFile)
        user = User(
            username=data["Username"] , 
            email=data["Email"] , 
            hashedPassword=data["Password"]            
        )
        user.activityStatus=data["activityStatus"]
        user.loginStatus=data["loginStatus"]
        user.projects=data["Projects"]
        user.assignedProjects=data["assignedProjects"]
        return user


    def log_in_out():
        pass

    def createProject(self):
        ID = input("Enter an ID for your project: ") 
        while(True):
            if projectID_availability(ID):
                break
            else:
                ID = input("THis ID is already taken!\nPlease Try again:") 
                     
        PrName = input("Enter a title for the project: ")
        
        project = Project(ID , PrName , self.username)
        #project.saveProject(ID + ".json")
        self.projects[ID] = {
            "ProjectName": PrName,
            "Admin": self.username,
            "Members": [],
            "tasks" : []
        }
        
        self.saveUser()
        save_projectID(ID)
        project.saveProject(ID)
        return project
            

    def add_member_to_project(self, prID, username):
        # adding a member to the chosen pr
           
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if username not in self.projects[prID]["Members"]:
                # load the pr with the ID and add member to it
                #fname = "projects/" + prID + ".json"
                pr = Project.loadProject(prID)
                pr.members.append(username)
                pr.saveProject(prID)
                
                #add member to member part of prj
                
                self.projects[prID]["Members"].append(username)
                self.saveUser()
            #need to fix this later:
                addedMember = User.loadUser(username)
                addedMember.assignedProjects.append(prID)
                addedMember.saveUser()
            #******************************************
                
                print(f"User {username} is now a member of {prID}.")
            else:
                print(f"User {username} is already a member of {prID}.")
        else:
            print("You do not have permission to add members to this project.")
        
    def remove_user_from_project(self , prID, username):

        # some error handlings are yet to get complete
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if username in self.projects[prID]["Members"]:
                
                self.projects[prID]["Members"].remove(username)
                
                self.saveUser()
                print(f"User {username} was removed from project {prID}.")
                
                
                #Some error handling is needed here.!! 
                removed_user = User.loadUser(username)
                removed_user.assignedProjects.remove(prID) 
                removed_user.saveUser()

                #fname = "projects/" + prID + ".json"
                pr = Project.loadProject(prID)
                pr.members.remove(username)
                pr.saveProject(prID)                   
            else:
                print(f"User {username} is not a member of {prID}.")
        else:
            print("You do not have permission to remove members from this project.")

    def delete_project(self , prID):
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            
            answer = input("Are you sure You wanna delete this project?\nYou can't change your decision later!! \n (yes or no)")
            if answer == "yes":
                fpath = "projects/" + prID + ".json"
                del self.projects[prID]
                self.saveUser()
                if os.path.exists(fpath):
                    os.remove(fpath)
                    print(f"you successfuly deleted {prID}.")


            else:
                return None
            
        else:
            print("You do not have permission to delete projects!!")
            
    def Retitle_Pr(self , prID , newTitle):
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            self.projects[prID]["ProjectName"] = newTitle
            self.saveUser()
            pr = Project.loadProject(prID)
            pr.title = newTitle
            pr.saveProject(prID)

    def changePrID(self , prID , newID):
        pass
    
    #@staticmethod
    def createTask(self , prID):

        pr = Project.loadProject(prID)
        taskID = generate_unique_id()
        while(True):
            answer = int(input("1.generate a default task? \n 2.create your own task? \n Enter (1 or 2):"))            
            if answer != 1 and answer != 2:
                print("Invalid input , try Again!")

            else:
                if answer == 1:
                    task = Task(taskID)
                    self.projects[prID]["tasks"].append({"taskID" : taskID , "taskTitle" : task.taskTitle})
                    self.saveUser()
                    pr.add_task(task)
                    #pr.tasks[task.Status][task.Priority].append(task)
                    pr.saveProject(prID)
                    task.saveTask()
                    task.saveHistory(f"The {task.taskID} was created by {self.username}.")
                    return task
                if answer == 2:
                    taskTitle = input("Enter a title for your task or press enter to leave it empty:")
                    taskDescription = input("description to your task or press enter to leave it empty:")
                    createdDT = input("Enter the starting date and time or ptess enter for the current time.\n example: (YYYY-MM-DD HH:MM:SS)")
                    deadlineDT = input("Enter the deadline date and time or ptess enter for 24H after the starting time.\n example: (YYYY-MM-DD HH:MM:SS)")
                    priority = Task.get_priority()
                    status = Task.get_status()

                    task = Task(taskID , taskTitle , taskDescription , priority , status , createdDT , deadlineDT)
                    self.projects[prID]["tasks"].append({"taskID" : taskID , "taskTitle" : task.taskTitle})
                    self.saveUser()
                    pr.add_task(task)
                    pr.saveProject(prID)
                    task.saveTask()
                    task.saveHistory(f"The {task.taskID} was created by {self.username}.")
                    return task
                    
                
                break
        
        
            

    def change_priority(self , prID , taskID):
        project = Project.loadProject(prID)
        task = Task.loadTask(taskID)
        curPriority = task.Priority.value

        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            project.remv_task(task)
            task.Priority = task.get_priority().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
            task.saveHistory(f" {self.username} changed this task's priority from {curPriority} to {task.Priority.value}.")
        elif self.username in task.Assignees:
            project.tasks[task.Status.value][task.Priority.value].remove({"taskID" : task.taskID , "taskTitle" : task.taskTitle})
            task.Priority = task.get_priority().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
            task.saveHistory(f" {self.username} changed this task's priority from {curPriority} to {task.Priority.value}.")
        else:
            print("You don't have the ability to do so")

    def change_status(self , prID , taskID):
        project = Project.loadProject(prID)
        task = Task.loadTask(taskID)
        curStatus = task.Status.value

        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            project.remv_task(task)
            task.Status = task.get_status().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
            task.saveHistory(f" {self.username} changed this task's priority from {curStatus} to {task.Priority.value}.")
        elif self.username in task.Assignees:
            project.remv_task(task)
            task.Status = task.get_status().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
            task.saveHistory(f" {self.username} changed this task's priority from {curStatus} to {task.Priority.value}.")
        else:
            print("You don't have the ability to do so")
        

    def add_assignee_to_task(self , prID , taskId , username):
        #project = Project.loadProject(prID)
        task = Task.loadTask(taskId)
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if username in self.projects[prID]["Members"]:
                if username not in task.Assignees:
                    task.Assignees.append(username)
                    task.saveTask()
                    #project.tasks[task.Status][task.Priority][index] = task
                    #project.saveProject(prID)
                    print(f"the task was assigned to {username}")
                    task.saveHistory(f"the task was assigned to {username}")
                else:
                    print("This user has already been assigned with the task")
            else:
                print("Only the members of the project can be assigned to task!!")
        else:
            print("Only admin of a project could do this!")

    def remove_assignee_from_task(self , prID , taskID , username):
        
        task = Task.loadTask(taskID)
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if username in self.projects[prID]["Members"]:
                if username in task.Assignees:

                    task.Assignees.remove(username)
                    task.saveTask()

                    print(f"{username} is not an assignee of the {task.taskTitle} anymore.")
                    task.saveHistory(f"{username} was removed from this task's assignees.")
                else:
                    print(f"{task.taskTitle} was not assigned to {username}")
            else:
                print("Can't do that.the user is not a member of this project!!")
        else:
            print("Only admin of a project could do this!")


        
    def delTask(self , prID , taskID):
        prj = Project.loadProject(prID)
        task = Task.loadTask(taskID)
        d = 0
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            #if taskID in prj.tasks:
                #pass
            for i in range(len(prj.tasks[task.Status][task.Priority])):
                if prj.tasks[task.Status][task.Priority][i]["taskID"] == task.taskID:
                    d += 1
                    self.projects[prID]["tasks"].remove({"taskID" : taskID , "taskTitle" : task.taskTitle})
                    del prj.tasks[task.Status][task.Priority][i]
                    self.saveUser()
                    prj.saveProject(prj.projectID)
                    if os.path.exists("tasks/" + task.taskID + ".json"):
                        os.remove("tasks/" + task.taskID + ".json")
                    else:
                        print("task file does not exist!!")

            if (d == 0):
                print("the task does not belong to this project!")
        else:
            print("Only admin of a project could do this!")
                
        
    def addComment(self , prID , taskID , newComment):
        task = Task.loadTask(taskID)
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            task.comments.append(newComment)
            task.saveHistory(f"{self.username} added a comment.")
            task.saveTask()
        elif self.username in task.Assignees:
            task.comments.append(newComment)
            task.saveHistory(f"{self.username} added a comment.")
            task.saveTask()
        else:
            print("Only the task's assignees could do that!")

    def clearComments(self , prID , taskID , newComment):
        task = Task.loadTask(taskID)
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            task.comments.clear()
            task.saveHistory(f"{self.username} cleared the comments.")
            task.saveTask()
        elif self.username in task.Assignees:
            task.comments.clear()
            task.saveHistory(f"{self.username} cleared the comments.")
            task.saveTask()
        else:
            print("Only the task's assignees could do that!")
            


    
class Project:
    def __init__(self , projectID, title , admin):
        self.projectID = projectID
        self.title = title
        self.description = ""
        self.admin = admin
        self.members = []
        self.tasks = {"BACKLOG" : {"LOW" : [] , "MEDIUM" : [] , "HIGH" : [] , "CRITICAL" : []} ,
                       "TODO" : {"LOW" : [] , "MEDIUM" : [] , "HIGH" : [] , "CRITICAL" : []},
                      "DOING" : {"LOW" : [] , "MEDIUM" : [] , "HIGH" : [] , "CRITICAL" : []} ,
                        "DONE" : {"LOW" : [] , "MEDIUM" : [] , "HIGH" : [] , "CRITICAL" : []} ,
                          "ARCHIVED" : {"LOW" : [] , "MEDIUM" : [] , "HIGH" : [] , "CRITICAL" : []}
                          }
        

    def add_task(self, task):

        self.tasks[task.Status][task.Priority].append({"taskID" : task.taskID , "taskTitle" : task.taskTitle})
    def remv_task(self, task):

        self.tasks[task.Status][task.Priority].remove({"taskID" : task.taskID , "taskTitle" : task.taskTitle})    

    def saveProject(self, prID):
        filename = "projects/" + prID + ".json"
        projectData = {
            "projectID": self.projectID,
            "title": self.title,
            "description": self.description,
            "admin": self.admin,
            "members": self.members,
            "tasks": self.tasks
        }
        with open(filename, 'w') as jsonFile:
            json.dump(projectData, jsonFile, indent=4)

    @staticmethod
    def loadProject(prID):
        filename = "projects/" + prID + ".json"
        if not os.path.exists(filename):
            print("Project not found!")
            return None

        with open(filename, 'r') as jsonFile:
            data = json.load(jsonFile)
            
        project = Project(
            projectID=data["projectID"], 
            title=data["title"], 
            admin=data["admin"]
        )
        project.description = data["description"]
        project.members = data["members"]
        project.tasks = data["tasks"]
        return project
    

    def organize_tasks(self):
        organized_tasks = {status: {priority: [] for priority in Priority} for status in Status}
        
        for status in Status:
            for priority in Priority:
                taskLists = self.tasks[status.value][priority.value]
                for taskList in taskLists:
                    print(taskList["taskID"])
                    task = Task.loadTask(taskList["taskID"])
                    organized_tasks[status][priority].append(task)
        
        return organized_tasks
    


# TBD    
class Task:
    #self, taskID, taskTitle="", Priority=Priority.LOW, Status=Status.BACKLOG, createdDT=None, deadlineDT=None
    def __init__(self , taskID , taskTitle="" , description="" , priority=Priority.LOW , status=Status.BACKLOG , createdDT=None , deadlineDT=None):

        self.taskID = taskID
        self.taskTitle = taskTitle
        self.Priority = priority.value
        self.Status = status.value
        self.Description = description
        self.createdDT = createdDT if createdDT else datetime.now().isoformat()
        self.deadlineDT = deadlineDT if deadlineDT else (datetime.now() + timedelta(hours=24)).isoformat()
        self.Assignees = []
        self.History = {}
        self.comments = []

    @staticmethod
    def get_priority():
        print("Select priority level:")
        for priority in Priority:
            print(f"{priority.value}")
        
        prio = input("Enter the priority (LOW, MEDIUM, HIGH, CRITICAL) or press enter for defaulting to LOW: ").strip().capitalize()
        try:
            return Priority[prio.upper()]
        except KeyError:
            print("Invalid priority.Defaulting to LOW.")
            return Priority.LOW

    @staticmethod    
    def get_status():
        print("Select task's status:")
        for status in Status:
            print(f"{status.value}")
        statu = input("Enter the status you want (BACKLOG, TODO, DOING , DONE , ARCHIVED ) or press enter for defaulting to BACKLOG: ").strip().capitalize()
        try:
            return Status[statu.upper()]
        except:
            print("Invalid priority.Defaulting to BACKLOG.")
            return Status.BACKLOG

    def saveTask(self):
        taskData = {
            "taskID": self.taskID,
            "taskTitle": self.taskTitle,
            "taskDescription": self.Description,
            "createdDT": self.createdDT,
            "deadlineDT": self.deadlineDT,
            "Priority": self.Priority,
            "Status": self.Status,
            "Assignees": self.Assignees,
            "Comments" : self.comments
        }

        filename = "tasks/" + self.taskID + ".json"
        with open(filename, 'w') as jsonFile:
            json.dump(taskData, jsonFile, indent=4)

    @staticmethod
    def loadTask(taskID):
        filename = "tasks/" + str(taskID) + ".json"
        if not os.path.exists(filename):
            print("Task not found!")
            return None

        with open(filename, 'r') as jsonFile:
            data = json.load(jsonFile)
            
            
        task = Task(
            taskID=data["taskID"], 
            taskTitle=data["taskTitle"],  
            priority=Priority[data["Priority"]], 
            status=Status[data["Status"]],
            createdDT=data["createdDT"],
            deadlineDT=data["deadlineDT"]
        )
        task.Assignees = data["Assignees"]
        task.Description = data["taskDescription"]
        task.comments = data["Comments"]
        return task
    """it'll be done soon. nothing much"""
    def saveHistory(self , historyNote):
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        note = f"[{current_time}] : {historyNote}\n"
        fpath = "tasks/History/history-" + self.taskID + ".txt"
        
        try:
            with open(fpath, "a") as file:
                file.write(note)

        except FileNotFoundError:
            with open(fpath , "w") as file:
                file.write(note) 

    def getHistory(self):
        fpath = "tasks/History/history-" + self.taskID + ".txt"

        try:
            with open(fpath, "r") as file:
                for line in file:
                    print(line.strip())
        except FileNotFoundError:
            print("History file does not exist.")

    def clearHistory(self):
        fpath = "tasks/History/history-" + self.taskID + ".txt"

        try:
            with open(fpath, "w") as file:
                file.write("")
        except FileNotFoundError:
            print("History file does not exist.")

    
        


        
        



    #for now to check if the functions work you could use them as below:

    """برای ساختن یوزر:
    
    user = User(username , email , password)
    user.saveuser() --> یوزر برای استقاده بعد ذخیره میشه

    user = User.loadUser("username") -- > استفاده از یوزر های موجود

    ساختن پروژه:

    project = user.createProject()

    project = Project.loadProject("project ID") --> استفاده از پروژه های موجود


    ساختن تسک:

    task = user.createTask(project.projectID)

    task = Task.loadTask(ایدی تسک) --> استفاده از تسک های موجوئ

    """
    
if __name__ == "__main__":

    pass