# [Django Auto Create][docs]

# About

Django automatic creation wizard, can according to their own needs to create initialization and app django project, and can automatically create a virtual environment for you.

# Requirements

* Python (2.7, 3.2, 3.3, 3.4, 3.5)
* Django (1.10)

# Installation

Install using `pip`...

    pip install djangoautocreate

Install at local...

    python setup.py install

# Use

When you install success, you can use `django-auto-create createproject` to create a project, such as:

    django-auto-admin createproject

you will be prompted to enter the project directory path and project name as well as the virtual environment name, and you can also use the following parameters
Quickly create.

    django-auto-admin createproject --directory Test --projectname myProject --envname myEnv



# Example

Let's take a look at a quick example of using Auto crate to build a django project.

    D:\myWorkspace\python\django-auto-create-1.1>django-auto-admin createproject
    Please enter the path to create the project (relative path is preferred):Test
    Your project path: D:\myWorkspace\python\django-auto-create-1.1\Test
    you must provide one project name
    Please enter the project name:Md
    Your project name: Md
    Do you need a virtual environment?(Y/N):n
    Creating project...
    Successfully created a project: Md
    Modify the project configuration...
    Successfully modify project configure.
    Create app...
    Please enter the name of the app (heavy star will be overwritten, enter 'n' out!):app
    Modify the app configuration...
    Successfully create app: app
    Please enter the name of the app (heavy star will be overwritten, enter 'n' out!):n



[docs]: http://blog.scmud.com/