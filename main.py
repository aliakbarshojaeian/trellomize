import hashlib
import json
import re
from rich import print as rprint

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

    rprint("[spring_green1]Your account has been created successfully.[/spring_green1]")


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
    rprint("[spring_green1]You have successfully logged in.[/spring_green1]")


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
        

def userOptions():
    rprint("[gold3]What do you want to do?[/gold3]")
    rprint("[bright_white]1)[/bright_white][hot_pink3]Make a board[/hot_pink3]")
    rprint("[bright_white]2)[/bright_white][hot_pink3]Quit[/hot_pink3]")


    answ = input()

    while(True):
        if answ == "1":
            rprint("[deep_pink2]This feature is currently not active.[/deep_pink2]")
            rprint("[gold3]What do you want to do?[/gold3]")
            rprint("[bright_white]1)[/bright_white][hot_pink3]Make a board[/hot_pink3]")
            rprint("[bright_white]2)[/bright_white][hot_pink3]Quit[/hot_pink3]")

            answ = input()
        elif answ == "2":
            rprint("[orange_red1]Come back soon dear.[/orange_red1]")
            exit()
        else:
            rprint("[deep_pink2]The answer is invalid, try again.[/deep_pink2]")
            rprint("[gold3]What do you want to do?[/gold3]")
            rprint("[bright_white]1)[/bright_white][hot_pink3]Make a board[/hot_pink3]")
            rprint("[bright_white]2)[/bright_white][hot_pink3]Quit[/hot_pink3]")

            answ = input()

        
def adminOptions():
    rprint("[gold3]What do you want to do?[/gold3]")
    rprint("[bright_white]1)[/bright_white][hot_pink3]Ban a user[/hot_pink3]")
    rprint("[bright_white]2)[/bright_white][hot_pink3]Quit[/hot_pink3]")

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

                    rprint("[spring_green1]User successfully banned.[/spring_green1]")
                    rprint("[gold3]What do you want to do?[/gold3]")
                    rprint("[bright_white]1)[/bright_white][hot_pink3]Ban a user[/hot_pink3]")
                    rprint("[bright_white]2)[/bright_white][hot_pink3]Quit[/hot_pink3]")
                    answ = input()
                else:
                    rprint("[deep_pink2]This user does not exist, try again.[/deep_pink2]")    
            except FileNotFoundError:
                rprint("[deep_pink2]This user does not exist.[/deep_pink2]")
                rprint("[gold3]What do you want to do?[/gold3]")
                rprint("[bright_white]1)[/bright_white][hot_pink3]Ban a user[/hot_pink3]")
                rprint("[bright_white]2)[/bright_white][hot_pink3]Quit[/hot_pink3]")
                answ = input()
        elif answ == "2":
            rprint("[orange_red1]Come back soon dear.[/orange_red1]")
            exit()
        else:
            rprint("[deep_pink2]The answer is invalid, try again.[/deep_pink2]")
            rprint("[gold3]What do you want to do?[/gold3]")
            rprint("[bright_white]1)[/bright_white][hot_pink3]Ban a user[/hot_pink3]")
            rprint("[bright_white]2)[/bright_white][hot_pink3]Quit[/hot_pink3]")

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
                    createNewUser()
                    userOptions()
                    break
                elif ans == "yes":
                    CheckUserInformation()
                    userOptions()
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



if __name__ == "__main__":
    start()