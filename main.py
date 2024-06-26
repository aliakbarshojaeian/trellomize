import uuid
import hashlib
import json
import re
import os
import logging
from enum import Enum
from datetime import datetime , timedelta
from rich import print as rprint
from typing import Type
from rich.console import Console
from rich.table import Table

#***********************************************************************************************************************************************************
#***********************************************************************************************************************************************************
def makeTable(newList : list, colName : str) -> None:
    newTable = Table()
        
    newTable.add_column("ROWS", style="cyan3")
    newTable.add_column(colName, style="chartreuse2")
    
    i = 1
    for comment in newList:
        newTable.add_row(str(i), comment)
        i += 1

    console = Console()
    print()
    console.print(newTable)
    print()


#***********************************************************************************************************************************************************
#***********************************************************************************************************************************************************
#Configure logging

class CustomFormatter(logging.Formatter):
    """
    A class to create a custom format for the log file.
    """
    format = "%(levelname)s - %(asctime)s - %(name)s) %(message)s"

    FORMATS = {
        logging.DEBUG:format,
        logging.INFO:format,
        logging.WARNING:format,
        logging.ERROR:format,
        logging.CRITICAL:format
    }

    def format(self, record):
        logFmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(logFmt)
        return formatter.format(record)
    

logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler('logfile.log')
fileHandler.setLevel(logging.DEBUG)

fileHandler.setFormatter(CustomFormatter())

logger.addHandler(fileHandler)


#***********************************************************************************************************************************************************
#***********************************************************************************************************************************************************
#Project related functions

def generate_unique_id() -> str:
    return str(uuid.uuid4())


def load_projectIDs(filename = "projectsID.json") -> set:
    if not os.path.exists(filename):
        return set()
    
    with open(filename, 'r') as file:
        pIDs = json.load(file)
    return set(pIDs)


def save_projectID(pID : str , filename = "projectsID.json") -> None:
    project_ids = load_projectIDs(filename)
    project_ids.add(pID)
    
    with open(filename, 'w') as file:
        json.dump(list(project_ids) , file , indent=4)


def projectID_availability(projectID : str , filename = "projectsID.json") -> bool:
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


#***********************************************************************************************************************************************************
#*********************************************************************************************************************************************************** 
class Task:
    def __init__(self , taskID , taskTitle="noTitle" , description="" , priority=Priority.LOW , status=Status.BACKLOG , createdDT=None , deadlineDT=None):

        self.taskID = taskID
        self.taskTitle = taskTitle
        self.Priority = priority.value
        self.Status = status.value
        self.Description = description
        self.createdDT = createdDT if createdDT else datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.deadlineDT = deadlineDT if deadlineDT else ( datetime.strptime(self.createdDT, "%Y-%m-%dT%H:%M:%S") + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
        self.Assignees = []
        self.History = {}
        self.comments = []


    @staticmethod
    def get_priority():
        while True:
            rprint("[turquoise4]Select priority level:[/turquoise4]")

            for priority in Priority:
                print(f"{priority.value}")
            rprint("[turquoise4]Enter the priority (LOW, MEDIUM, HIGH, CRITICAL) or press enter for defaulting to LOW:[/turquoise4]")
            prio = input().strip().capitalize()
            if prio == "":
                return Priority.LOW
            
            try:
                return Priority[prio.upper()]
            except KeyError:
                rprint("[deep_pink2]Invalid priority. Please try again.[/deep_pink2]")

    @staticmethod    
    def get_status():
        while True:
            rprint("[turquoise4]Select task's status:[/turquoise4]")
            for status in Status:
                print(f"{status.value}")
            rprint("[turquoise4]Enter the status you want (BACKLOG, TODO, DOING , DONE , ARCHIVED) or press enter for defaulting to BACKLOG: [/turquoise4]")
            
            statu = input().strip().capitalize()
            if statu == "":
                return Status.BACKLOG
            
            try:
                return Status[statu.upper()]
            except KeyError:
                rprint("[deep_pink2]Invalid status. Please try again.[/deep_pink2]")
                

    # func to save task to a json file
    def saveTask(self) -> None:
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

    # func to load a task from a json file 
    @staticmethod
    def loadTask(taskID : str):
        filename = "tasks/" + str(taskID) + ".json"
        if not os.path.exists(filename):
            rprint("[deep_pink2]Task not found![/deep_pink2]")
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

    #func to save history in a txt file    
    def saveHistory(self , historyNote : str) -> None:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        note = f"[{current_time}] : {historyNote}\n"
        fpath = "tasks/History/history-" + self.taskID + ".txt"
        
        try:
            with open(fpath, "a") as file:
                file.write(note)

        except FileNotFoundError:
            with open(fpath , "w") as file:
                file.write(note) 


    def getHistory(self) -> None:
        fpath = "tasks/History/history-" + self.taskID + ".txt"

        try:
            with open(fpath, "r") as file:
                for line in file:
                    print(line.strip())
        except FileNotFoundError:
            rprint("[deep_pink2]History file does not exist.[/deep_pink2]")
            


    def clearHistory(self) -> None:
        fpath = "tasks/History/history-" + self.taskID + ".txt"

        try:
            with open(fpath, "w") as file:
                file.write("")
        except FileNotFoundError:
            rprint("[deep_pink2]History file does not exist.[/deep_pink2]")
            
    # func to handle the validity of date and time's format inputed by the user
    @staticmethod
    def get_valid_datetime(kind , startT = ""):
            if kind == "Start":
                s = "to use the current time"
                s1 = "starting"
            else:
                s = "for 24H after the starting time"
                s1 = "deadline"
            while True:
                rprint(f"[turquoise4]Enter the {s1} datetime in the format 'YYYY-MM-DDTHH:MM:SS'\n(or press Enter {s}):[/turquoise4]")
                inp = input()
                if  kind == "Start":   
                    if inp == "":
                        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    try:
                        dt = datetime.strptime(inp , "%Y-%m-%dT%H:%M:%S")
                        return dt.strftime("%Y-%m-%dT%H:%M:%S")
                        
                    except ValueError:
                        rprint("[deep_pink2]Incorrect format.Try again.[/deep_pink2]")
                else:
                    d = datetime.strptime(startT , "%Y-%m-%dT%H:%M:%S")
                    if inp == "":
                        return (d + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")
                    try:
                        dt = datetime.strptime(inp , "%Y-%m-%dT%H:%M:%S")
                        return dt.strftime("%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        rprint("[deep_pink2]Incorrect format.Try again.[/deep_pink2]")

    # func to print the date and time in a sentence
    def printDatetime(self , kind):
        if kind == "Start": 
            datetime_str = self.createdDT
        else:
            datetime_str = self.deadlineDT
        dt = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
        now = datetime.now()
        
        if kind == "Start":       
            if dt > now:
                prefix = "will start at"
            else:
                prefix = "started at"

        else:
            if dt < now:
                prefix = "it ended in"
            else:
                prefix = "it ends in"

        DateNote = dt.strftime(f"{prefix} %A %B %d' at %H:%M:%S")

        day = dt.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]

        DateNote = DateNote.replace(f"{day}'", f"{day}{suffix}'")

        return DateNote


#***********************************************************************************************************************************************************
#***********************************************************************************************************************************************************
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
        
    # func to add task to project
    def add_task(self, task : Type[Task]) -> None:

        self.tasks[task.Status][task.Priority].append({"taskID" : task.taskID , "taskTitle" : task.taskTitle})

    #func to remove task from project
    def remv_task(self, task : Type[Task]) -> None:

        self.tasks[task.Status][task.Priority].remove({"taskID" : task.taskID , "taskTitle" : task.taskTitle})    

    # func to save a project in jason file
    def saveProject(self, prID : str) -> None:
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

    # func to load a project from a json file
    @staticmethod
    def loadProject(prID : str):
        filename = "projects/" + prID + ".json"
        if not os.path.exists(filename):
            rprint("[deep_pink2]Project not found![/deep_pink2]")
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
    

#***********************************************************************************************************************************************************
#***********************************************************************************************************************************************************
class User():
    def __init__(self , username=None , email=None , hashedPassword=None):
        self.username = username
        self.email = email
        self.hapassword = hashedPassword
        self.projects = {}
        self.assignedProjects = []
        self.activityStatus = "Active"
        self.loginStatus = "logged in"
        
    # func to save user in json file
    def saveUser(self) -> None:
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

    # func to load user from a json file
    @staticmethod
    def loadUser(username : str):
        filename = "users/" + username + ".json"
        if os.path.exists(filename):
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
        else:
            rprint(f"[deep_pink2]User {username} does not exist.[/deep_pink2]")
            return None
        

    def createProject(self) -> Type[Project]:
        rprint("[turquoise4]Enter an ID for your project:[/turquoise4]")
        ID = input() 
        while(True):
            if projectID_availability(ID):
                break
            else:
                rprint("[deep_pink2]This ID is already taken, Please Try again:[/deep_pink2]")
                ID = input() 
                     
        rprint("[turquoise4]Enter a title for the project:[/turquoise4]")
        PrName = input()
        
        project = Project(ID , PrName , self.username)

        self.projects[ID] = {
            "ProjectName": PrName,
            "Admin": self.username,
            "Members": [],
            "tasks" : []
        }
        
        self.saveUser()
        save_projectID(ID)
        project.saveProject(ID)
        rprint(f"[spring_green2]Project {ID} was created.[/spring_green2]")
        logger.info(f"Project '{ID}' was created by {self.username}.")
        return project
    
            
    def add_member_to_project(self, prID : str, username : str) -> None:  
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if username != self.username:
                if username not in self.projects[prID]["Members"]:
                    pr = Project.loadProject(prID)
                    pr.members.append(username)
                    pr.saveProject(prID)
                    
                    self.projects[prID]["Members"].append(username)
                    self.saveUser()
                
                    addedMember = User.loadUser(username)
                    addedMember.assignedProjects.append(prID)
                    addedMember.saveUser()
                
                    rprint(f"[spring_green2]User {username} is now a member of {prID}.[/spring_green2]")
                    logger.info(f"'{username}' was added to Project '{prID}' by '{self.username}'.")
                else:
                    rprint(f"[deep_pink2]User {username} is already a member of {prID}.[/deep_pink2]")
            else:
                rprint("[deep_pink2]You are already the admin![/deep_pink2]")
        else:
            rprint("[deep_pink2]You do not have permission to add members to this project.[/deep_pink2]")

        
    def remove_user_from_project(self , prID : str, username : str) -> None:
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if username != self.username:   
                if username in self.projects[prID]["Members"]:
                    
                    self.projects[prID]["Members"].remove(username)
                    
                    self.saveUser()
                    rprint(f"[spring_green2]User {username} was removed from project {prID}.[/spring_green2]")
                    logger.info(f"'{username}' was removed from Project '{prID}' by '{self.username}'.")
                    
                    removed_user = User.loadUser(username)
                    removed_user.assignedProjects.remove(prID) 
                    removed_user.saveUser()

                    pr = Project.loadProject(prID)
                    pr.members.remove(username)
                    pr.saveProject(prID)                   
                else:
                    rprint(f"[deep_pink2]User {username} is not a member of {prID}.[/deep_pink2]")
            else:
                rprint("[deep_pink2]You are the admin! cannot do that.[/deep_pink2]")
        else:
            rprint("[deep_pink2]You do not have permission to remove members from this project.[/deep_pink2]")


    def delete_project(self , prID):
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            rprint("[turquoise4]Are you sure You wanna delete this project? You can't change your decision later!(yes or no)[/turquoise4]")
            answer = input()
            if answer == "yes":
                fpath = "projects/" + prID + ".json"

                task_ids = [task["taskID"] for task in self.projects[prID]["tasks"]]

                del self.projects[prID]
                self.saveUser()
                if os.path.exists(fpath):
                    os.remove(fpath)
                    rprint(f"[spring_green2]you successfuly deleted {prID}.[/spring_green2]")
                else:
                    rprint(f"[deep_pink2]The {prID} file does not exist![/deep_pink2]")
                # deleting the project's tasks in tasks folder
                for task_id in task_ids:
                    taskFpath = "tasks/" + str(task_id) + ".json"
                    if os.path.exists(taskFpath):
                        os.remove(taskFpath)
                    else:
                        continue
            else:
                return None
        else:
            rprint("[deep_pink2]You do not have permission to delete projects!![/deep_pink2]")

            
    def Retitle_Pr(self , prID : str , newTitle : str) -> None:
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            self.projects[prID]["ProjectName"] = newTitle
            self.saveUser()
            pr = Project.loadProject(prID)
            pr.title = newTitle
            pr.saveProject(prID)
            logger.info(f"The title of project '{prID}' was changed to '{newTitle}' by '{self.username}'.")
        else:
            rprint("[deep_pink2]Only the admin of the project could do that![/deep_pink2]")


    def changeDescription(self , prID : str) -> None:
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            pr = Project.loadProject(prID)
            rprint("[turquoise4]Enter the new description or press enter to CLEAR it:[/turquoise4]")
            newDescrp = input()
            pr.description = newDescrp
            pr.saveProject(pr.projectID)

    

    def createTask(self , prID):

        pr = Project.loadProject(prID)
        taskID = generate_unique_id()
        while(True):
            rprint("[turquoise4]1.generate a default task?\n 2.create your own task?\n Enter (1 or 2):[/turquoise4]")
            answer = input()           
            if answer != "1" and answer != "2":
                rprint("[deep_pink2]Invalid input , try Again![/deep_pink2]")

            else:
                #to quickly create a default task
                if answer == "1":
                    task = Task(taskID)
                    self.projects[prID]["tasks"].append({"taskID" : taskID , "taskTitle" : task.taskTitle})
                    self.saveUser()
                    pr.add_task(task)
                    pr.saveProject(prID)
                    task.saveTask()
                    task.saveHistory(f"The {task.taskID} was created by {self.username}.")
                    return task
                # to create a task with user input
                if answer == "2":
                    rprint("[turquoise4]Enter a title for your task or press enter to leave it empty:[/turquoise4]")
                    taskTitle = input()
                    rprint("[turquoise4]description to your task or press enter to leave it empty:[/turquoise4]")
                    taskDescription = input()
                    createdDT = Task.get_valid_datetime("Start")
                    deadlineDT = Task.get_valid_datetime("Deadline" , createdDT)
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
        


    def change_priority(self , prID : str , taskID : str) -> None:
        project = Project.loadProject(prID)
        task = Task.loadTask(taskID)
        curPriority = task.Priority

        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            project.remv_task(task)
            task.Priority = task.get_priority().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
            task.saveHistory(f"{self.username} changed this task's priority from {curPriority} to {task.Priority}.")
            logger.info(f"The priority of '{taskID}' task from the '{prID}' project was changed from '{curPriority}' to '{task.Priority}' by '{self.username}'.")
        elif self.username in task.Assignees:
            project.tasks[task.Status.value][task.Priority.value].remove({"taskID" : task.taskID , "taskTitle" : task.taskTitle})
            task.Priority = task.get_priority().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
            task.saveHistory(f"{self.username} changed this task's priority from {curPriority} to {task.Priority}.")
            logger.info(f"The priority of '{taskID}' task from the '{prID}' project was changed from '{curPriority}' to '{task.Priority}' by '{self.username}'.")
        else:
            rprint("[deep_pink2]You don't have the ability to do so[/deep_pink2]")


    def change_status(self , prID : str , taskID : str) -> None:
        project = Project.loadProject(prID)
        task = Task.loadTask(taskID)
        curStatus = task.Status

        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            project.remv_task(task)
            task.Status = task.get_status().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
            task.saveHistory(f"{self.username} changed this task's priority from {curStatus} to {task.Status}.")
            logger.info(f"The status of '{taskID}' task from the '{prID}' project was changed from '{curStatus}' to '{task.Status}' by '{self.username}'.")
        elif self.username in task.Assignees:
            project.remv_task(task)
            task.Status = task.get_status().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
            task.saveHistory(f"{self.username} changed this task's priority from {curStatus} to {task.Status}.")
            logger.info(f"The status of '{taskID}' task from the '{prID}' project was changed from '{curStatus}' to '{task.Status}' by '{self.username}'.")
        else:
            rprint("[deep_pink2]You don't have the ability to do so.[/deep_pink2]")


    def add_assignee_to_task(self , prID : str , taskId : str , username : str) -> None:
        task = Task.loadTask(taskId)
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if username in self.projects[prID]["Members"] or username == self.username:
                if username not in task.Assignees:
                    task.Assignees.append(username)
                    task.saveTask()
                    rprint(f"[spring_green2]the task was assigned to {username}[/spring_green2]")
                    task.saveHistory(f"the task was assigned to {username}")
                    logger.info(f"'{taskId}' task was assigned to '{username}' by '{self.username}' from '{prID}' project.")
                else:
                    rprint("[deep_pink2]This user has already been assigned with the task[/deep_pink2]")
            else:
                rprint("[deep_pink2]Only the members of the project can be assigned to task!![/deep_pink2]")
        else:
            rprint("[deep_pink2]Only admin of a project could do this![/deep_pink2]")


    def remove_assignee_from_task(self , prID : str , taskID : str , username : str) -> None:
        task = Task.loadTask(taskID)
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if username in self.projects[prID]["Members"] or username == self.username:
                if username in task.Assignees:

                    task.Assignees.remove(username)
                    task.saveTask()

                    rprint(f"[spring_green2]{username} is not an assignee of the {task.taskTitle} anymore.[spring_green2]")
                    task.saveHistory(f"{username} was removed from this task's assignees.")
                    logger.info(f"'{username}' was removed from the task of '{taskID}' in the '{prID}' project by '{self.username}'.")
                else:
                    rprint(f"[deep_pink2]{task.taskTitle} was not assigned to {username}[/deep_pink2]")
            else:
                rprint("[deep_pink2]Can't do that.the user is not a member of this project!![/deep_pink2]")
        else:
            rprint("[deep_pink2]Only admin of a project could do this![/deep_pink2]")

    
    def delTask(self , prID : str , taskID : str) -> None:
        prj = Project.loadProject(prID)
        task = Task.loadTask(taskID)
        d = 0
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            for i in range(len(prj.tasks[task.Status][task.Priority])):
                if prj.tasks[task.Status][task.Priority][i]["taskID"] == task.taskID:
                    d += 1
                    self.projects[prID]["tasks"].remove({"taskID" : taskID , "taskTitle" : task.taskTitle})
                    del prj.tasks[task.Status][task.Priority][i]
                    self.saveUser()
                    prj.saveProject(prj.projectID)
                    if os.path.exists("tasks/" + task.taskID + ".json"):
                        os.remove("tasks/" + task.taskID + ".json")
                        rprint("[deep_pink2]Task was deleted successfully![/deep_pink2]")
                        logger.info(f"'{taskID}' task was removed from the '{prID}' project by '{self.username}'.")
                    else:
                        rprint("[deep_pink2]task file does not exist!![/deep_pink2]")

            if (d == 0):
                rprint("[deep_pink2]the task does not belong to this project![/deep_pink2]")
        else:
            rprint("[deep_pink2]Only admin of a project could do this![/deep_pink2]")
                
    # func to add comments to a task    
    def addComment(self , prID : str , taskID : str) -> None:
        task = Task.loadTask(taskID)
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            rprint("[turquoise4]Enter your comment:[/turquoise4]")
            newComment = input()
            task.comments.append(newComment)
            task.saveHistory(f"{self.username} added a comment.")
            task.saveTask()
            logger.info(f"'{self.username}' added a comment to '{taskID}' task from '{prID}' project.")
        elif self.username in task.Assignees:
            rprint("[turquoise4]Enter your comment:[/turquoise4]")
            newComment = input()
            task.comments.append(newComment)
            task.saveHistory(f"{self.username} added a comment.")
            task.saveTask()
            logger.info(f"'{self.username}' added a comment to '{taskID}' task from '{prID}' project.")
        else:
            rprint("[deep_pink2]Only the task's assignees could do that![/deep_pink2]")

    # fun to clear the comments of a task
    def clearComments(self , prID : str , taskID : str) -> None:
        task = Task.loadTask(taskID)
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            task.comments.clear()
            task.saveHistory(f"{self.username} cleared the comments.")
            task.saveTask()
            logger.info(f"'{self.username}' removed the '{taskID}' task comments from the '{prID}' project.")
        elif self.username in task.Assignees:
            task.comments.clear()
            task.saveHistory(f"{self.username} cleared the comments.")
            task.saveTask()
            logger.info(f"'{self.username}' removed the '{taskID}' task comments from the '{prID}' project.")
        else:
            rprint("[deep_pink2]Only the task's assignees could do that![/deep_pink2]")
            

    def change_task_title(self , prID : str , taskID : str) -> None:
        task = Task.loadTask(taskID)
        project = Project.loadProject(prID)

        oldTaskTitle = task.taskTitle
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            rprint("[turquoise4]Enter a new title:[/turquoise4]")
            newTiltle = input()
            project.remv_task(task)
            task.taskTitle = newTiltle
            task.saveTask()
            project.add_task(task)
            project.saveProject(prID)
            task.saveHistory(f"{self.username} changed the task's title to {newTiltle}.")
            logger.info(f"'{self.username}' changed the title of '{taskID}' task from '{prID}' project from '{oldTaskTitle}' to '{task.taskTitle}'")
        else:
            rprint("[deep_pink2]Only the admin could do that![/deep_pink2]")



    def change_task_deadline(self , prID : str , taskID : str) -> None:
        task = Task.loadTask(taskID)

        oldTaskDeadline = task.deadlineDT
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            newddline = Task.get_valid_datetime("Deadline" , task.createdDT)
            task.deadlineDT = newddline
            task.saveTask()
            task.saveHistory(f"{self.username} changed the task's deadline to {newddline}.")
            logger.info(f"'{self.username}' changed the deadline of '{taskID}' task of '{prID}' project from '{oldTaskDeadline}' to '{task.deadlineDT}'.")
        else:
            rprint("[deep_pink2]Only the admin could do that![/deep_pink2]")

    # func to check the existence of projects assigned to a user. it might have been deleted!
    def refresh(self):
        d = 0
        for i in range(len(self.assignedProjects)):
            prID = self.assignedProjects[i - d]
            fpath = "projects/" + prID + ".json"
            if os.path.exists(fpath):
                continue
            else:
                rprint(f"[spring_green2]The {prID} appear to be deleted by its admin![/spring_green2]")
                self.assignedProjects.remove(self.assignedProjects[i - d])
                d += 1
                rprint("[spring_green2]It was removed from your assigned projects![/spring_green2]")
        self.saveUser()


    def showProject(self , prID : str):
        filename = "projects/" + prID + ".json"

        if not os.path.exists(filename):
            rprint("[deep_pink2]Project not found![/deep_pink2]")
            return None

        with open(filename, 'r') as jsonFile:
            data = json.load(jsonFile)


        if (prID in self.projects and self.projects[prID]["Admin"] == self.username) or (prID in self.assignedProjects):
            self.createTable(prID)
        else:
            rprint("[deep_pink2]You do not have permission to access this project.[/deep_pink2]")


    def listOfCreatedProject(self):
        listOfProj = []

        for item in self.projects:
            listOfProj.append(item)

        makeTable(listOfProj, "PROJECT ID")
    

    def listOfAssignedProject(self):
        listOfProj = self.assignedProjects
        makeTable(listOfProj, "PROJECT ID")


    @staticmethod
    def showTask(taskID : str):
       
        historyFile = "tasks/History/history-" + taskID + ".txt"

        task = Task.loadTask(taskID) 

        if not os.path.exists(historyFile):
            rprint("[deep_pink2]History not found![/deep_pink2]")
            return None

        with open(historyFile, 'r') as f:
            history = f.readlines()


        rprint("[light_coral]************************************************************************************************************************[/light_coral]")
        rprint("[turquoise4]Task information:[/turquoise4]")
        print()
        rprint("[turquoise4]task title: [/turquoise4]", task.taskTitle)
        print()

        rprint("[turquoise4]task description: [/turquoise4]", task.Description)
        print()

        startDate = task.printDatetime("Start")
        rprint("[turquoise4]createdDT: [/turquoise4]", startDate)
        print()
        deadlineDate = task.printDatetime("Deadline") 
        rprint("[turquoise4]deadlineDT: [/turquoise4]", deadlineDate)
        print()

        rprint("[turquoise4]Assignees:[/turquoise4]")
        makeTable(task.Assignees, "ASSIGNEES")
        
        rprint("[turquoise4]Comments:[/turquoise4]")
        makeTable(task.comments, "COMMENTS")

        rprint("[turquoise4]History:[/turquoise4]")
        print()
        for line in history:
            rprint(f"[gold1]{line}[/gold1]")
        
        rprint("[light_coral]************************************************************************************************************************[/light_coral]")




    def createTable(self, prID ) -> None:
        
        project = Project.loadProject(prID)

        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
        main_table = Table(title=projTitle)
        main_table.add_column("BACKLOG", style="orange_red1")
        main_table.add_column("TODO", style="hot_pink3")
        main_table.add_column("DOING", style="orange1")
        main_table.add_column("DONE", style="cyan3")
        main_table.add_column("ARCHIVED", style="spring_green3")


        def create_nested_table(priority, task_list):
            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                
            nested_table.add_column("ROWS")
            nested_table.add_column("TASK ID")
            nested_table.add_column("TASK TITLE")
            
            i = 1
            for task in task_list:
                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                i += 1

            return nested_table

        tasks = project.tasks

        rows_data = {key: [] for key in tasks.keys()}

        for status, priorities in tasks.items():
            for priority, task_list in priorities.items():
                if task_list:
                    nested_table = create_nested_table(priority, task_list)
                    rows_data[status].append(nested_table)

        max_rows = max(len(rows) for rows in rows_data.values())

        for i in range(max_rows):
            row = []
            for status in tasks.keys():
                if i < len(rows_data[status]):
                    nested_table = rows_data[status][i]
                    row.append(nested_table)
                else:
                    row.append("")
            main_table.add_row(*row)

        def getStatusAndPrioAndRow():
            rprint("[turquoise4]Enter the task status:[/turquoise4]")
            s = Task.get_status().value
            rprint("[turquoise4]Enter the priority of the task:[/turquoise4]")
            p = Task.get_priority().value
            rprint("[turquoise4]Enter the desired task row number:[/turquoise4]")
            row = int(input())

            task_id = tasks[s][p][row - 1]["taskID"] 

            return task_id
        

        while True:
            console = Console()
            console.print(main_table)

            rprint("[gold3]What do you want to do?[/gold3]")
            rprint("[bright_white]1)[/bright_white][hot_pink3]View members of this project[/hot_pink3]")
            rprint("[bright_white]2)[/bright_white][hot_pink3]View actions related to tasks[/hot_pink3]")
            rprint("[bright_white]3)[/bright_white][hot_pink3]Back[/hot_pink3]")

            answe = input()

            if answe == "1":
                project = Project.loadProject(prID)
                makeTable(project.members, "MEMBERS")

            elif answe == "2":
                while(True):
                    printTaskActions()

                    inp = input()

                    if inp == "1": 
                        task = self.createTask(prID)
                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                    elif inp == "2":
                        try:
                            task_id = getStatusAndPrioAndRow() 
                            print(task_id)
                            self.showTask(task_id)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")
                    elif inp == "3":
                        try:
                            task_id = getStatusAndPrioAndRow()
        
                            self.change_priority(prID , task_id)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")

                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                    elif inp == "4":

                        try:
                            task_id = getStatusAndPrioAndRow() 
        
                            self.change_status(prID , task_id)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")

                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                    elif inp == "5":
                        try:
                            task_id = getStatusAndPrioAndRow() 
                            rprint("[turquoise4]Enter the username of the desired user: [turquoise4/]")
                            newUser = input()
                            
                            self.add_assignee_to_task(prID , task_id , newUser)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")


                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                    elif inp == "6":

                        try:
                            task_id = getStatusAndPrioAndRow() 
                            rprint("[turquoise4]Enter the username of the desired user: [turquoise4/]")
                            newUser = input() 

                            self.remove_assignee_from_task(prID , task_id , newUser)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")


                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                    elif inp == "7":
                        try:
                            task_id = getStatusAndPrioAndRow() 
                            self.change_task_deadline(prID, task_id)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")


                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                        
                    elif inp == "8":
                        try:
                            task_id = getStatusAndPrioAndRow() 
                            self.change_task_title(prID, task_id)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")


                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                    elif inp == "9":
                        try:
                            task_id = getStatusAndPrioAndRow() 
                            commentTask = Task.loadTask(task_id)

                            self.addComment(prID, commentTask.taskID)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")


                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                       
                    elif inp == "10":
                        try:
                            task_id = getStatusAndPrioAndRow()
                            commentTask = Task.loadTask(task_id)
                            
                            self.clearComments(prID, commentTask.taskID)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")


                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                    elif inp == "11":
                        try:
                            task_id = getStatusAndPrioAndRow() 
                            task = Task.loadTask(task_id)
                            task.getHistory()
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")

                        
                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                    elif inp == "12":

                        try:
                            task_id = getStatusAndPrioAndRow() 
                            
                            self.delTask(prID , task_id)
                        except Exception:
                            rprint("[deep_pink2]Something went wrong, try again.[/deep_pink2]")

                        project = Project.loadProject(prID)

                        projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                        main_table = Table(title=projTitle)
                        main_table.add_column("BACKLOG", style="orange_red1")
                        main_table.add_column("TODO", style="hot_pink3")
                        main_table.add_column("DOING", style="orange1")
                        main_table.add_column("DONE", style="cyan3")
                        main_table.add_column("ARCHIVED", style="spring_green3")


                        def create_nested_table(priority, task_list):
                            nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                                
                            nested_table.add_column("ROWS")
                            nested_table.add_column("TASK ID")
                            nested_table.add_column("TASK TITLE")
                            
                            i = 1
                            for task in task_list:
                                nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                                i += 1

                            return nested_table

                        tasks = project.tasks

                        rows_data = {key: [] for key in tasks.keys()}

                        for status, priorities in tasks.items():
                            for priority, task_list in priorities.items():
                                if task_list:
                                    nested_table = create_nested_table(priority, task_list)
                                    rows_data[status].append(nested_table)

                        max_rows = max(len(rows) for rows in rows_data.values())

                        for i in range(max_rows):
                            row = []
                            for status in tasks.keys():
                                if i < len(rows_data[status]):
                                    nested_table = rows_data[status][i]
                                    row.append(nested_table)
                                else:
                                    row.append("")
                            main_table.add_row(*row)
                    elif inp == "13":
                        break
                    else:
                        rprint("[deep_pink2]Invalid answer, try again.[/deep_pink2]")
            elif answe == "3":
                project = Project.loadProject(prID)

                projTitle = f"project : '{project.projectID}', admin : '{project.admin}'"
                main_table = Table(title=projTitle)
                main_table.add_column("BACKLOG", style="orange_red1")
                main_table.add_column("TODO", style="hot_pink3")
                main_table.add_column("DOING", style="orange1")
                main_table.add_column("DONE", style="cyan3")
                main_table.add_column("ARCHIVED", style="spring_green3")


                def create_nested_table(priority, task_list):
                    nested_table = Table(title=priority, show_header=True, header_style="bright_white")
                        
                    nested_table.add_column("ROWS")
                    nested_table.add_column("TASK ID")
                    nested_table.add_column("TASK TITLE")
                    
                    i = 1
                    for task in task_list:
                        nested_table.add_row(str(i), task["taskID"], task["taskTitle"])
                        i += 1

                    return nested_table

                tasks = project.tasks

                rows_data = {key: [] for key in tasks.keys()}

                for status, priorities in tasks.items():
                    for priority, task_list in priorities.items():
                        if task_list:
                            nested_table = create_nested_table(priority, task_list)
                            rows_data[status].append(nested_table)

                max_rows = max(len(rows) for rows in rows_data.values())

                for i in range(max_rows):
                    row = []
                    for status in tasks.keys():
                        if i < len(rows_data[status]):
                            nested_table = rows_data[status][i]
                            row.append(nested_table)
                        else:
                            row.append("")
                    main_table.add_row(*row)


                if prID in self.projects:
                    self.listOfCreatedProject()
                elif prID in self.assignedProjects:
                    self.listOfAssignedProject()

                break
            else:
                rprint("[deep_pink2]Invalid answer, try again.[/deep_pink2]")
                

#***********************************************************************************************************************************************************
#***********************************************************************************************************************************************************
#Functions related to login

def hashPassword(password : str) -> int:
    """
    A function to hash a password.
    """
    sha256Hash = hashlib.sha256()

    sha256Hash.update(password.encode())

    hashedPassword = sha256Hash.hexdigest()

    return hashedPassword


def checkUsernameValidity(username : str) -> bool:
    """
    A function to check the validity of username.
    """
    usernamePattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(usernamePattern, username):
        return False
    
    return True


def checkPresenceUsername(dictionary : dict, username : str) -> bool:
    """
    A function to check the presence of the username.
    """
    return username in dictionary


def checkEmailValidity(email : str) -> bool:
    """
    A function to check the validity of the email address.
    """
    emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,7}$'
    if(re.fullmatch(emailPattern, email)):
        return True
    else:
        return False


def checkPresenceValue(dictionary : dict, key : str, email : str) -> bool:
    """
    A function to check the presence of email with binary search algorithm.
    """
    sortedItems = sorted(dictionary.items(), key=lambda item: item[1][key])
    values = [item[1][key] for item in sortedItems]
    left = 0
    right = len(values) - 1
    while left <= right:
        mid = (left + right) // 2
        if values[mid] == email:
            return True
        elif values[mid] < email:
            left = mid + 1
        else:
            right = mid - 1
    return False


def createNewUser() -> Type[User]:
    """
    A function to create new users.
    """
    rprint("[turquoise4]Please enter your username:[/turquoise4]")
    username = input()
    rprint("[turquoise4]Please enter your password:[/turquoise4]")
    password = input()
    rprint("[turquoise4]Please enter your Email:[/turquoise4]")
    email = input()

    hashedPassword = hashPassword(password)

    try:
        with open('users.json') as f:
            users = json.load(f)
    except FileNotFoundError:
        with open('users.json', 'w') as f:
            users = {}

    while(True):
        if not checkUsernameValidity(username):
            rprint("[deep_pink2]Invalid username, try again.[/deep_pink2]")
            rprint("[turquoise4]Enter your new username:[/turquoise4]")
            username = input()
        elif checkPresenceUsername(users, username):
            rprint("[deep_pink2]ERROR! Duplicate username, try another username.[/deep_pink2]")
            rprint("[turquoise4]Enter your new username:[/turquoise4]")
            username = input()
        elif not checkEmailValidity(email):
            rprint("[deep_pink2]Invalid email address, try again.[/deep_pink2]")
            rprint("[turquoise4]Enter your new email:[/turquoise4]")
            email = input()
        elif checkPresenceValue(users, "email",email):
            rprint("[deep_pink2]ERROR! The email is duplicate, try another email.[/deep_pink2]")
            rprint("[turquoise4]Enter your new email:[/turquoise4]")
            email = input()
        else:
            break

    newUser = {"username" : username, "password" : hashedPassword, "email" : email, "activityStatus" : "active", "loginStatus" : "logged in"}
    
    users[username] = newUser

    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

    user = User(username, email, hashedPassword)
    user.saveUser()

    logger.info(f"'{username}' has successfully created an account.")

    rprint("[spring_green1]Your account has been created successfully.[/spring_green1]")

    return user


def CheckUserInformation() -> Type[User]:
    """
    A function to check the information of users that already exist in the system.
    """
    rprint("[turquoise4]Please enter your username:[/turquoise4]")
    username = input()
    rprint("[turquoise4]Please enter your password:[/turquoise4]")
    password = input()

    hashedPassword = hashPassword(password)

    try:
        with open('users.json') as f:
            users = json.load(f)
    except FileNotFoundError:
        rprint("[deep_pink2]Failed attempt.[/deep_pink2]")
        exit()
    
    while(True):
        if not checkPresenceUsername(users, username):
            rprint("[deep_pink2]Invalid username, try again.[/deep_pink2]")
            rprint("[turquoise4]Please enter your username correctly or type [yellow2]quit[/yellow2] to exit:[/turquoise4]")
            newInput = input()
            if newInput == "quit":
                exit()
            else:
                username = newInput
        elif users[username]["password"] != hashedPassword:
            rprint("[deep_pink2]Password is wrong, try again.[/deep_pink2]")
            rprint("[turquoise4]Please enter your password correctly or type [yellow2]quit[/yellow2] to exit:[/turquoise4]")
            newInput = input()
            if newInput == "quit":
                exit()
            else:
                password = newInput
                hashedPassword = hashPassword(password)
        elif users[username]["activityStatus"] == "inactive":
            rprint("[deep_pink2]Your account is inactive, login is not possible.[/deep_pink2]")
            exit()
        else:
            break

    users[username]["loginStatus"] = "logged in"

    user = User.loadUser(username)

    logger.info(f"'{username}' has successfully logged in.")

    rprint("[spring_green1]You have successfully logged in.[/spring_green1]")

    return user


def checkAdminInformation() -> None:
    """
    A function to check the information of admin.
    """
    rprint("[turquoise4]Please enter your username:[/turquoise4]")
    username = input()
    rprint("[turquoise4]Please enter your password:[/turquoise4]")
    password = input()

    hashedPassword = hashPassword(password)

    try:
        with open('admin.json') as f:
            admin = json.load(f)
    except FileNotFoundError:
        rprint("[deep_pink2]Failed attempt.[/deep_pink2]")
        exit()

    while(True):
        if not checkPresenceUsername(admin, username):
            rprint("[deep_pink2]Invalid username, try again.[/deep_pink2]")
            rprint("[turquoise4]Please enter your username correctly or type [yellow2]quit[/yellow2] to exit:[/turquoise4]")
            newInput = input()
            if newInput == "quit":
                exit()
            else:
                username = newInput
        elif admin[username]["password"] != hashedPassword:
            rprint("[deep_pink2]Password is wrong, try again.[/deep_pink2]")
            rprint("[turquoise4]Please enter your password correctly or type [yellow2]quit[/yellow2] to exit:[/turquoise4]")
            newInput = input()
            if newInput == "quit":
                exit()
            else:
                password = newInput
                hashedPassword = hashPassword(password)
        else:
            break

    logger.info(f"'{username}' has successfully logged in.")
    
    rprint("[spring_green1]You have successfully logged in.[/spring_green1]")



def printTaskActions():
    rprint("[gold3]What do you want to do?[/gold3]")
    rprint("[bright_white]1)[/bright_white][hot_pink3]Create a new task[/hot_pink3]")
    rprint("[bright_white]2)[/bright_white][hot_pink3]View a task[/hot_pink3]")
    rprint("[bright_white]3)[/bright_white][hot_pink3]Change the priority of a task[/hot_pink3]")
    rprint("[bright_white]4)[/bright_white][hot_pink3]Change the status of a task[/hot_pink3]")
    rprint("[bright_white]5)[/bright_white][hot_pink3]Assigning a task to a member[/hot_pink3]")
    rprint("[bright_white]6)[/bright_white][hot_pink3]Remove a member from a task[/hot_pink3]")
    rprint("[bright_white]7)[/bright_white][hot_pink3]Change task deadline[/hot_pink3]")
    rprint("[bright_white]8)[/bright_white][hot_pink3]Change task title[/hot_pink3]")
    rprint("[bright_white]9)[/bright_white][hot_pink3]Add a comment[/hot_pink3]")
    rprint("[bright_white]10)[/bright_white][hot_pink3]Clear all comments[/hot_pink3]")
    rprint("[bright_white]11)[/bright_white][hot_pink3]History[/hot_pink3]")
    rprint("[bright_white]12)[/bright_white][hot_pink3]Delete a task[/hot_pink3]")
    rprint("[bright_white]13)[/bright_white][hot_pink3]Back[/hot_pink3]")


def printProjectActions():
    rprint("[gold3]What do you want to do?[/gold3]")
    rprint("[bright_white]1)[/bright_white][hot_pink3]View a project[/hot_pink3]")
    rprint("[bright_white]2)[/bright_white][hot_pink3]Changing the title of a project[/hot_pink3]")
    rprint("[bright_white]3)[/bright_white][hot_pink3]Add member to a project[/hot_pink3]")
    rprint("[bright_white]4)[/bright_white][hot_pink3]Remove a member from a project[/hot_pink3]")
    rprint("[bright_white]5)[/bright_white][hot_pink3]Delete a project[/hot_pink3]")
    rprint("[bright_white]6)[/bright_white][hot_pink3]Back[/hot_pink3]")


def projectActions(user):
    printProjectActions()

    answ = input()

    while(True):
        if answ == "1":
            rprint("[turquoise4]Enter the desired project ID:[/turquoise4]")
            prID = input()
            user.showProject(prID)

            printProjectActions()
            answ = input()
        elif answ == "2":
            rprint("[turquoise4]Enter the desired project ID:[/turquoise4]")
            prID = input()
            rprint("[turquoise4]Enter the new title:[/turquoise4]")
            newTitle = input()
            user.Retitle_Pr(prID, newTitle)


            if prID in user.projects:
                user.listOfCreatedProject()
            elif prID in user.assignedProjects:
                user.listOfAssignedProject()

            printProjectActions()
            answ = input()
        elif answ == "3":
            rprint("[turquoise4]Enter the desired project ID:[/turquoise4]")
            prID = input()
            rprint("[turquoise4]Enter the username of the desired user:[/turquoise4]")
            newUser = input()

            user.add_member_to_project(prID, newUser)

            if prID in user.projects:
                user.listOfCreatedProject()
            elif prID in user.assignedProjects:
                user.listOfAssignedProject()

            printProjectActions()
            answ = input()
        elif answ == "4":
            rprint("[turquoise4]Enter the desired project ID:[/turquoise4]")
            prID = input()
            rprint("[turquoise4]Enter the username of the desired user:[/turquoise4]")
            newUser = input()

            user.remove_user_from_project(prID, newUser)

            if prID in user.projects:
                user.listOfCreatedProject()
            elif prID in user.assignedProjects:
                user.listOfAssignedProject()

            printProjectActions()
            answ = input()
        elif answ == "5":
            rprint("[turquoise4]Enter the desired project ID:[/turquoise4]")
            prID = input()

            check = False

            if prID in user.projects:
                check = True
            elif prID in user.assignedProjects:
                check = False

            user.delete_project(prID)

            if check:
                user.listOfCreatedProject()
            else:
                user.listOfAssignedProject()


            printProjectActions()
            answ = input()
        elif answ == "6":
            break
        else:
            rprint("[deep_pink2]The answer is invalid, try again.[/deep_pink2]")
            
            printProjectActions()
            answ = input()



def printOptionOfUser() -> None:
    rprint("[gold3]What do you want to do?[/gold3]")
    rprint("[bright_white]1)[/bright_white][hot_pink3]Create a new project[/hot_pink3]")
    rprint("[bright_white]2)[/bright_white][hot_pink3]View the list of projects created by you[/hot_pink3]")
    rprint("[bright_white]3)[/bright_white][hot_pink3]View the list of projects assigned to you[/hot_pink3]")
    rprint("[bright_white]4)[/bright_white][hot_pink3]Clear the screen[/hot_pink3]")
    rprint("[bright_white]5)[/bright_white][hot_pink3]Quit[/hot_pink3]")



def userOptions(user : Type[User]) -> None:

    printOptionOfUser()

    answ = input()

    while(True):
        if answ == "1":
            project = user.createProject()

            printOptionOfUser()
            answ = input()
        elif answ == "2":
            user.listOfCreatedProject()
            
            projectActions(user)

            printOptionOfUser()
            answ = input()
        elif answ == "3":
            user.listOfAssignedProject()
            
            projectActions(user)

            printOptionOfUser()
            answ = input()
        elif answ == "4":
            os.system('cls')
            printOptionOfUser()
            answ = input()
        elif answ == "5":
            rprint("[orange_red1]Come back soon dear.[/orange_red1]")
            exit()
        else:
            rprint("[deep_pink2]The answer is invalid, try again.[/deep_pink2]")
            
            printOptionOfUser()
            answ = input()



def printOptionOfAdmin() -> None:
    rprint("[gold3]What do you want to do?[/gold3]")
    rprint("[bright_white]1)[/bright_white][hot_pink3]Ban a user[/hot_pink3]")
    rprint("[bright_white]2)[/bright_white][hot_pink3]Unban a user[/hot_pink3]")
    rprint("[bright_white]3)[/bright_white][hot_pink3]Quit[/hot_pink3]")


def adminOptions() -> None:
    printOptionOfAdmin()

    answ = input()

    while(True):
        if answ == "1":
            rprint("[turquoise4]Enter the username:[/turquoise4]")
            username = input()
            try:
                with open('users.json') as f:
                    users = json.load(f)

                if checkPresenceUsername(users, username):
                    users[username]["activityStatus"] = "inactive"
                    with open('users.json', 'w') as f:
                        json.dump(users, f, indent=4)

                    filename = "users/" + username + ".json"
                    with open(filename) as f:
                        newUser = json.load(f)

                    newUser["activityStatus"] = "inactive"

                    with open(filename, 'w') as f:
                        json.dump(newUser, f, indent=4)

                    logger.info(f"'{username}' was banned by the admin.")
                    rprint("[spring_green1]User successfully banned.[/spring_green1]")
                    printOptionOfAdmin()
                    answ = input()
                else:
                    rprint("[deep_pink2]This user does not exist, try again.[/deep_pink2]")    
            except FileNotFoundError:
                rprint("[deep_pink2]This user does not exist.[/deep_pink2]")
                printOptionOfAdmin()
                answ = input()
        elif answ == "2":
            rprint("[turquoise4]Enter the username:[/turquoise4]")
            username = input()
            try:
                with open('users.json') as f:
                    users = json.load(f)

                if checkPresenceUsername(users, username):
                    users[username]["activityStatus"] = "active"
                    with open('users.json', 'w') as f:
                        json.dump(users, f, indent=4)

                    filename = "users/" + username + ".json"
                    with open(filename) as f:
                        newUser = json.load(f)

                    newUser["activityStatus"] = "active"

                    with open(filename, 'w') as f:
                        json.dump(newUser, f, indent=4)

                    logger.info(f"'{username}' was unbanned by the admin.")
                    rprint("[spring_green1]User successfully unbanned.[/spring_green1]")
                    printOptionOfAdmin()
                    answ = input()
                else:
                    rprint("[deep_pink2]This user does not exist, try again.[/deep_pink2]")    
            except FileNotFoundError:
                rprint("[deep_pink2]This user does not exist.[/deep_pink2]")
                printOptionOfAdmin()
                answ = input()
        elif answ == "3":
            rprint("[orange_red1]Come back soon dear.[/orange_red1]")
            exit()
        else:
            rprint("[deep_pink2]The answer is invalid, try again.[/deep_pink2]")
            printOptionOfAdmin()
            answ = input()


def start() -> None:
    rprint("[pale_violet_red1]Login as:[/pale_violet_red1]")
    rprint("[bright_white]1)[/bright_white][navy_blue]Admin[/navy_blue]")
    rprint("[bright_white]2)[/bright_white][navy_blue]Normal user[/navy_blue]")
    rprint("[bright_white]3)[/bright_white][navy_blue]Quit[/navy_blue]")

    answer = input()

    while(True):
        if answer == "1":
            checkAdminInformation()
            adminOptions()
            break
        elif answer == "2":
            rprint("[deep_pink4]Welcome, you already have an account?(answer [yellow2]yes[/yellow2] or [yellow2]no[/yellow2] or To exit, type [yellow2]quit[/yellow2]):[/deep_pink4]")
            ans = input()

            while(True):
                if ans == "no":
                    user = createNewUser()
                    user.refresh()
                    userOptions(user)
                    break
                elif ans == "yes":
                    user = CheckUserInformation()
                    user.refresh()
                    userOptions(user)
                    break
                elif ans == "quit":
                    exit()
                else:
                    rprint("[deep_pink2]The answer is invalid, try again.[/deep_pink2]")
                    rprint("[deep_pink4]You already have an account?(answer [yellow2]yes[/yellow2] or [yellow2]no[/yellow2] or To exit, type [yellow2]quit[/yellow2]):[/deep_pink4]")
                    ans = input() 
            break
        elif answer == "3":
            exit()
        else:
            rprint("[deep_pink2]The answer is invalid, try again.[/deep_pink2]")
            rprint("[pale_violet_red1]Login as:[/pale_violet_red1]")
            rprint("[bright_white]1)[/bright_white][navy_blue]Admin[/navy_blue]")
            rprint("[bright_white]2)[/bright_white][navy_blue]Normal user[/navy_blue]")
            rprint("[bright_white]3)[/bright_white][navy_blue]Quit[/navy_blue]")
            answer = input()

# func to create the folders and files that the app need in case they don't exist.
def createFilesFolders():
    folders = ['users', 'projects', 'tasks', 'tasks/History']
    file_path = os.path.join('projectsID.json')

    for folder in folders:
        path = os.path.join(folder)
        if not os.path.exists(path):
            os.makedirs(path)
            rprint(f"[spring_green2]Created folder: {path}[/spring_green2]")

    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({}, f) #it creates empty json file


#***********************************************************************************************************************************************************
#***********************************************************************************************************************************************************
if __name__ == "__main__":
    createFilesFolders()
    start()