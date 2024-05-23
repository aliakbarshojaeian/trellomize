import argparse
import json
import hashlib
import os
import glob
import shutil
from rich import print as rprint

def hashPassword(password):
    """
    A function to hash a password.
    """
    sha256Hash = hashlib.sha256()

    sha256Hash.update(password.encode())

    hashedPassword = sha256Hash.hexdigest()

    return hashedPassword


def deleteFilesWithExtension(extension):
    """
    A function to delete files based on their extension.
    """
    files = glob.glob(f'*.{extension}')
    for file in files:
        try:
            os.remove(file)
            rprint(f"'{file}' [spring_green1]deleted successfully.[/spring_green1]")
        except OSError as e:
            print(f"Error: {e}")


def deleteDir(newDir):
    """
    A function to delete a directory.
    """
    try:
        shutil.rmtree(newDir)
        rprint(f"'{newDir}' [spring_green1]deleted successfully.[/spring_green1]")
    except FileNotFoundError as e:
        rprint("[deep_pink2]There are no files to delete.[/deep_pink2]")
        exit()


def createAdmin():
    parser = argparse.ArgumentParser(description='Manager script')
    parser.add_argument('action', choices=['create-admin', 'purge-data'], help='Action to perform')
    parser.add_argument('--username', help='Username for admin')
    parser.add_argument('--password', help='Password for admin')
    args = parser.parse_args()

    if args.action == 'create-admin':
        admin = {args.username : {"username" : args.username, "password" : hashPassword(args.password)}}

        with open('admin.json', 'a') as f:
            if os.path.getsize("admin.json") == 0:
                json.dump(admin, f, indent=4)
                rprint("[spring_green1]The admin account was created successfully.[/spring_green1]")
            else:
                rprint("[deep_pink2]Admin account already exists.[/deep_pink2]")

    if args.action == 'purge-data':
        while(True):
            rprint("[turquoise4]Are you sure you want to purge data?(Answer [yellow2]yes[/yellow2] or [yellow2]no[/yellow2]):[turquoise4]")
            message = input()
            if message == "yes":
                deleteFilesWithExtension("json")
                deleteDir("users")
                deleteDir("tasks")
                deleteDir("projects")
                break
            elif message == "no":
                break
            else:
                rprint("[deep_pink2]Unacceptable answer, please answer [yellow2]yes[/yellow2] or [yellow2]no[/yellow2].[/deep_pink2]") 


if __name__ == "__main__":
    createAdmin()