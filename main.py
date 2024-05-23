import uuid
import hashlib
import json
import re
import os
from enum import Enum
from datetime import datetime , timedelta
from rich import print as rprint

#************************************************************************************************************************
#Functions related to login

def hashPassword(password):
    """
    A function to hash a password.
    """
    sha256Hash = hashlib.sha256()

    sha256Hash.update(password.encode())

    hashedPassword = sha256Hash.hexdigest()

    return hashedPassword


def checkUsernameValidity(username):
    """
    A function to check the validity of username.
    """
    usernamePattern = r'^[a-zA-Z0-9_]+$'
    if not re.match(usernamePattern, username):
        return False
    
    return True


def checkPresenceUsername(dictionary, username):
    """
    A function to check the presence of the username.
    """
    return username in dictionary


def checkEmailValidity(email):
    """
    A function to check the validity of the email address.
    """
    emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,7}$'
    if(re.fullmatch(emailPattern, email)):
        return True
    else:
        return False


def checkPresenceValue(dictionary, key ,email):
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


def createNewUser():
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

    rprint("[spring_green1]Your account has been created successfully.[/spring_green1]")

    return user


def CheckUserInformation():
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

    rprint("[spring_green1]You have successfully logged in.[/spring_green1]")

    return user


def checkAdminInformation():
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

    rprint("[spring_green1]You have successfully logged in.[/spring_green1]")


def printOptionOfUser():
    rprint("[gold3]What do you want to do?[/gold3]")
    rprint("[bright_white]1)[/bright_white][hot_pink3]Create a new project[/hot_pink3]")
    rprint("[bright_white]2)[/bright_white][hot_pink3]View a project[/hot_pink3]")
    rprint("[bright_white]3)[/bright_white][hot_pink3]Changing the title of a project[/hot_pink3]")
    rprint("[bright_white]4)[/bright_white][hot_pink3]Add member to a project[/hot_pink3]")
    rprint("[bright_white]5)[/bright_white][hot_pink3]Remove a member from a project[/hot_pink3]")
    rprint("[bright_white]6)[/bright_white][hot_pink3]Delete a project[/hot_pink3]")
    rprint("[bright_white]7)[/bright_white][hot_pink3]Create a new task[/hot_pink3]")
    rprint("[bright_white]8)[/bright_white][hot_pink3]View a task[/hot_pink3]")
    rprint("[bright_white]9)[/bright_white][hot_pink3]Change the priority of a task[/hot_pink3]")
    rprint("[bright_white]10)[/bright_white][hot_pink3]Change the status of a task[/hot_pink3]")
    rprint("[bright_white]11)[/bright_white][hot_pink3]Assigning a task to a member[/hot_pink3]")
    rprint("[bright_white]12)[/bright_white][hot_pink3]Remove a member from a task[/hot_pink3]")
    rprint("[bright_white]13)[/bright_white][hot_pink3]Delete a task[/hot_pink3]")
    rprint("[bright_white]14)[/bright_white][hot_pink3]Clear the screen[/hot_pink3]")
    rprint("[bright_white]15)[/bright_white][hot_pink3]Quit[/hot_pink3]")


def userOptions(user):

    printOptionOfUser()

    answ = input()

    while(True):
        if answ == "1":
            project = user.createProject()

            printOptionOfUser()
            answ = input()
        elif answ == "2":
            prID = input("Enter the desired project ID: ")
            project = Project.loadProject(prID)
            #project.showProject()

            printOptionOfUser()
            answ = input()
        elif answ == "3":
            prID = input("Enter the desired project ID: ")
            newTitle = input("Enter the new title: ")
            user.Retitle_Pr(prID, newTitle)

            printOptionOfUser()
            answ = input()
        elif answ == "4":
            prID = input("Enter the desired project ID: ")
            newUser = input("Enter the username of the desired user: ")

            user.add_member_to_project(prID, newUser)

            printOptionOfUser()
            answ = input()
        elif answ == "5":
            prID = input("Enter the desired project ID: ")
            newUser = input("Enter the username of the desired user: ")

            user.remove_user_from_project(prID, newUser)

            printOptionOfUser()
            answ = input()
        elif answ == "6":
            prID = input("Enter the desired project ID: ")

            user.delete_project(prID)

            printOptionOfUser()
            answ = input()
        elif answ == "7":
            prID = input("Enter the desired project ID: ")

            task = user.createTask(prID)

            printOptionOfUser()
            answ = input()
        elif answ == "8":
            taskID = input("Enter the desired task ID: ")
            task = Task.loadTask(taskID)

            #task.showTask()

            printOptionOfUser()
            answ = input()
        elif answ == "9":
            prID = input("Enter the desired project ID: ")
            taskID = input("Enter the desired task ID: ")

            user.change_priority(prID , taskID)

            printOptionOfUser()
            answ = input()
        elif answ == "10":
            prID = input("Enter the desired project ID: ")
            taskID = input("Enter the desired task ID: ")

            user.change_status(prID , taskID)

            printOptionOfUser()
            answ = input()
        elif answ == "11":
            prID = input("Enter the desired project ID: ")
            taskID = input("Enter the desired task ID: ")
            newUser = input("Enter the username of the desired user: ")

            user.add_assignee_to_task(prID , taskID , newUser)

            printOptionOfUser()
            answ = input()
        elif answ == "12":
            prID = input("Enter the desired project ID: ")
            taskID = input("Enter the desired task ID: ")
            newUser = input("Enter the username of the desired user: ")

            user.remove_assignee_from_task(prID , taskID , newUser)

            printOptionOfUser()
            answ = input()
        elif answ == "13":
            prID = input("Enter the desired project ID: ")
            taskID = input("Enter the desired task ID: ")

            user.delTask(prID , taskID)

            printOptionOfUser()
            answ = input()
        elif answ == "14":
            os.system('cls')
            printOptionOfUser()
            answ = input()
        elif answ == "15":
            rprint("[orange_red1]Come back soon dear.[/orange_red1]")
            exit()
        else:
            rprint("[deep_pink2]The answer is invalid, try again.[/deep_pink2]")
            
            printOptionOfUser()
            answ = input()


def printOptionOfAdmin():
    rprint("[gold3]What do you want to do?[/gold3]")
    rprint("[bright_white]1)[/bright_white][hot_pink3]Ban a user[/hot_pink3]")
    rprint("[bright_white]2)[/bright_white][hot_pink3]Unban a user[/hot_pink3]")
    rprint("[bright_white]3)[/bright_white][hot_pink3]Quit[/hot_pink3]")


def adminOptions():
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


def start():
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
                    userOptions(user)
                    break
                elif ans == "yes":
                    user = CheckUserInformation()
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

#************************************************************************************************************************
#Project related functions

def generate_unique_id():
    return str(uuid.uuid4())


def load_projectIDs(filename = "projectsID.json"):
    if not os.path.exists(filename):
        return set()
    
    with open(filename, 'r') as file:
        pIDs = json.load(file)
    return set(pIDs)


def save_projectID(pID , filename = "projectsID.json"):
    project_ids = load_projectIDs(filename)
    project_ids.add(pID)
    
    with open(filename, 'w') as file:
        json.dump(list(project_ids) , file , indent=4)

def projectID_availability(projectID , filename = "projectsID.json"):
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


#************************************************************************************************************************
class User():

    def __init__(self , username=None , email=None , hashedPassword=None):
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
                    return task
                break
        
    def change_priority(self , prID , taskID):
        project = Project.loadProject(prID)
        task = Task.loadTask(taskID)

        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            project.remv_task(task)
            task.Priority = task.get_priority().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
        elif self.username in task.Assignees:
            project.tasks[task.Status.value][task.Priority.value].remove({"taskID" : task.taskID , "taskTitle" : task.taskTitle})
            task.Priority = task.get_priority().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
        else:
            print("You don't have the ability to do so")

    def change_status(self , prID , taskID): 
        project = Project.loadProject(prID)
        task = Task.loadTask(taskID)

        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            project.remv_task(task)
            task.Status = task.get_status().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
        elif self.username in task.Assignees:
            project.remv_task(task)
            task.Status = task.get_status().value
            task.saveTask()
            project.add_task(task)
            project.saveProject(project.projectID)
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
                else:
                    print(f"{task.taskTitle} was not assigned to {username}")
            else:
                print("Can't do that.the user is not a member of this project!!")
        else:
            print("Only admin of a project could do this!")


    #ask about that
    def delTask(self , prID , taskID):
        prj = Project.loadProject(prID)
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if taskID in prj.tasks:
                pass
    def assignTask():
        pass
    def showTask():
        pass


#************************************************************************************************************************
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
    
    def showProject():
        pass
    

#************************************************************************************************************************    
class Task:
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
        self.comments = {}

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
            "Assignees": self.Assignees
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
        return task
    """it'll be done soon. nothing much"""
    def saveHistory(self , username , historyNote):
        pass

    def showTask():
        pass


#************************************************************************************************************************
if __name__ == "__main__":
    start()