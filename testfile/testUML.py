import uuid
import hashlib
import json
import re
import bisect
import os
from rich import print as rprint

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

def projectID_availability(project_id , filename = "projectsID.json"):
    #
    project_ids = load_projectIDs(filename)
    return project_id not in project_ids

#*********************************************************************************

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

    with open('users.json') as f:
        users = json.load(f)

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

    rprint("[spring_green1]Your account has been created successfully.[/spring_green1]")
    user1 = User(username , email , hashedPassword)
    user1.saveUser()


def CheckUserInformation():
    """
    A function to check the information of users that already exist in the system.
    """
    rprint("[turquoise4]Please enter your username:[/turquoise4]")
    username = input()
    rprint("[turquoise4]Please enter your password:[/turquoise4]")
    password = input()

    hashedPassword = hashPassword(password)

    with open('users.json') as f:
        users = json.load(f)

    while(True):
        if not checkPresenceUsername(users, username):
            rprint("[deep_pink2]Invalid username, try again.[/deep_pink2]")
            rprint("[turquoise4]Please enter your username correctly:[/turquoise4]")
            username = input()
        elif users[username]["password"] != hashedPassword:
            rprint("[deep_pink2]Password is wrong, try again.[/deep_pink2]")
            rprint("[turquoise4]Please enter your password correctly:[/turquoise4]")
            password = input()
            hashedPassword = hashPassword(password)
        else:
            break

    users[username]["loginStatus"] = "logged in"
    rprint("[spring_green1]You have successfully logged in.[/spring_green1]")

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
        filename = self.username + ".json"
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
    def loadUser(filename):

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
        ID = input("Enter an ID for your project:")        
        if not projectID_availability(ID):
            print("Project ID is already taken.")
            return None
        
        PrName = input()
        while(True):
            if projectID_availability(ID):
                break
            else:
                ID = input()
                PrName = input()
        
        project = Project(ID , PrName , self.username)
        project.saveProject(ID + ".json")
        self.projects[ID] = {
            "ProjectName": PrName,
            "Admin": self.username,
            "Members": [],
            "Tasks": {}
        }
        
        self.saveUser()
        save_projectID(ID)
        return project
            

    def add_member_to_project(self, prID, username):
        # adding a member to the chosen pr
        print(self.projects[prID]["Admin"] , "&&&&&&&")    
        if prID in self.projects and self.projects[prID]["Admin"] == self.username:
            if username not in self.projects[prID]["Members"]:
                # load the pr with the ID and add member to it
                fname = prID + ".json"
                pr = Project.loadProject(fname)
                pr.members.append(username)
                pr.saveProject(pr.projectID + ".json")
                
                #add member to member part of prj
                
                self.projects[prID]["Members"].append(username)
                self.saveUser()
            #need to fix this later:
                addedMember = User.loadUser(username + ".json")
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
                
                userFname = username + ".json"
                #Some error handling is needed here.!! 
                removed_user = User.loadUser(userFname)
                removed_user.assignedProjects.remove(prID) 
                removed_user.saveUser()

                fname = prID + ".json"
                pr = Project.loadProject(fname)
                pr.members.remove(username)
                pr.saveProject(fname)                   
            else:
                print(f"User {username} is not a member of {prID}.")
        else:
            print("You do not have permission to remove members from this project.")

    def delete_project(project_id):
        pass
    def addTask():
        pass
    def moveTask():
        pass
    def delTask():
        pass
    def assignTask():
        pass
    def showTask():
        pass

    
class Project:
    def __init__(self , projectID, title , admin):
        self.projectID = projectID
        self.title = title
        self.description = ""
        self.admin = admin
        self.members = []
        self.tasks = {}
        

    def add_task(self, task):
        pass

    def saveProject(self, filename):
        projectData = {
            "projectID": self.projectID,
            "title": self.title,
            "description": self.description,
            "admin": self.admin,
            "members": self.members,
            "tasks": {}
        }
        with open(filename, 'w') as jsonFile:
            json.dump(projectData, jsonFile, indent=4)

    @staticmethod
    def loadProject(filename):
        with open(filename, 'r') as jsonFile:
            data = json.load(jsonFile)
        project = Project(
            projectID=data["projectID"],
            title=data["title"],
            admin=data["admin"],
        )
        project.description = data["description"]
        project.members=data["members"]
        project.tasks=data["tasks"]

        return project
    

# TBD    
class Task:
    pass 


rprint("[deep_pink4]Welcome, you already have an account?(answer [yellow2]yes[/yellow2] or [yellow2]no[/yellow2] or To exit, type [yellow2]quit[/yellow2]):[/deep_pink4]")
answer = input()
while(True):
    if answer == "no":
        createNewUser()
        break
    elif answer == "yes":
        CheckUserInformation()
        break
    elif answer == "quit":
        exit()
    else:
        rprint("[deep_pink2]The answer is invalid, try again.[/deep_pink2]")
        rprint("[deep_pink4]You already have an account?(answer [yellow2]yes[/yellow2] or [yellow2]no[/yellow2] or To exit, type [yellow2]quit[/yellow2]):[/deep_pink4]")
        answer = input() 
    
    #!!!!!
    #for now to check if the functions work you could use them as below:
    
#if __name__ == "__main__":
    

    #a = input()
    #user = User.loadUser("Tim.json")
    #pr = user.createProject()
    #pr = Project.loadProject("2.json")
    #print(pr.projectID)
    #print(pr.members)
    #print(user.projects["2"]["Admin"])
    #print("***********************")
    ##user.add_member_to_project(pr.projectID , "Tim")
    ##user.add_member_to_project(pr.projectID , "Alex")
    ##pr2 = Project.loadProject("2.json")
    #print(pr.members)
    #user.remove_user_from_project(pr.projectID , "Tim")
    #user.remove_user_from_project(pr.projectID , "Alex")
    #pr2 = Project.loadProject("2.json")
    #print(pr2.members)
    
