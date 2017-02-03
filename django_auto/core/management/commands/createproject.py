# -*- coding: utf-8 -*-
# FileName      : 'createproject'
# CreateTime    : '2017/1/11 14:18'
# CreateAuthor  : 'Mundy'
"""
Automatically create django projects, including the creation of projects and virtual environment.
"""
from __future__ import unicode_literals

import sys
import re
import os
import platform
import django_auto
from importlib import import_module

from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.core import exceptions
from ..utils import get_random_secret_key
from django.utils.encoding import force_str
from django.utils import six
from distutils.sysconfig import get_python_lib
from django_auto.utils.django_helper import run_cmd, project_init_settings, app_init_settings
from django_auto.core import management


lib_path = [get_python_lib()][0]


class NotRunningInTTYException(Exception):
    pass


class Command(TemplateCommand):
    help = (
        "Creates a Django project directory and a virtual environment structure for the given project "
        "name in the current directory or optionally in the given directory."
    )

    def add_arguments(self, parser):
        parser.add_argument('--directory', dest='directory', default=None,
                            help='Specifies the project directory.')
        parser.add_argument('--projectname', dest='projectname', default=None,
                            help='Specifies the project name.')
        parser.add_argument('--envname', action='store', dest='envname',
                            default=None,
                            help='Specifies the a virtual environment to use.')

        parser.add_argument('--template', help='The path or URL to load the template from.')
        parser.add_argument(
            '--extension', '-e', dest='extensions',
            action='append', default=['py'],
            help='The file extension(s) to render (default: "py"). '
                 'Separate multiple extensions with commas, or use '
                 '-e multiple times.'
        )
        parser.add_argument(
            '--name', '-n', dest='files',
            action='append', default=[],
            help='The file name(s) to render. Separate multiple extensions '
                 'with commas, or use -n multiple times.'
        )

    def execute(self, *args, **options):
        self.stdin = options.get('stdin', sys.stdin)  # Used for testing
        return super(Command, self).execute(*args, **options)

    def handle(self, **options):
        project_name, target, envname = options.pop('projectname'), options.pop('directory'), options.pop('envname')

        try:
            if platform.system() == "Windows":
                move_command = "move"
                mkdir_command = "md"
            else:
                move_command = "mv"
                mkdir_command = "mkdir"

            # Get a directory
            if target is None:
                target = self.get_input_data(force_str("Please enter the path to create the project "
                                                       "(relative path is preferred):"))
            target = os.path.abspath(target)
            while not os.path.exists(target):
                self.stderr.write("Sorry! {0} directory does not exist".format(target))
                target = self.get_input_data(force_str("Please enter the path to create the project "
                                                       "(relative path is preferred):"))

            self.stdout.write("Your project path: %s" % target)

            # Get a projectname
            while not self.check_name(project_name, 'project') or project_name in os.listdir(os.path.join(target)):
                project_name = self.get_input_data(force_str("Please enter the project name:"))
                if project_name in os.listdir(os.path.join(target)):
                    self.stderr.write("Sorry! the {0} directory already exists {1} directory"
                                      .format(os.path.join(target), project_name))

            project_dir = target  # project directory is target
            self.stdout.write("Your project name: %s" % project_name)

            # Get a environment name
            if envname is None:
                virtualenv_need = False
                while True:
                    virtualenv_choice = self.get_input_data(force_str("Do you need a virtual environment?(Y/N):"))
                    if virtualenv_choice == "Y" or virtualenv_choice == "y":
                        virtualenv_need = True
                        break
                    elif virtualenv_choice == "N" or virtualenv_choice == "n":
                        virtualenv_need = False
                        break
            else:
                virtualenv_need = True

            if virtualenv_need:
                # Check virtualenv package
                current_python_path = os.path.dirname(os.path.dirname(get_python_lib()))
                if platform.system() == "Windows":
                    virtualenv_command = os.path.join(current_python_path, "Scripts", "virtualenv.exe")
                else:
                    current_scripts_path = os.path.dirname(current_python_path)
                    virtualenv_command = os.path.join(current_scripts_path, "bin", "virtualenv")

                if os.path.exists(virtualenv_command):
                    while not self.check_name(envname, 'environment'):
                        envname = self.get_input_data(force_str("Please enter the virtual environment name(leave "
                                                                "blank to use %s):" % (unicode(project_name) + "Env")))
                        if envname is None or envname == '':
                            envname = unicode(project_name) + "Env"

                    # Set the script path
                    package_dir = os.path.join(os.path.dirname(django_auto.__file__), 'package')
                    virtualenv_dir = os.path.join(target, envname)
                    if platform.system() == "Windows":
                        pip_path = os.path.join(virtualenv_dir, "Scripts", "pip.exe")
                    else:
                        pip_path = os.path.join(virtualenv_dir, "bin", "pip")

                    # Create a virtual environment
                    self.stdout.write("Create virtual environment %s..." % envname)
                    virtualenv_dir = os.path.join(target, envname)
                    self.stdout.write(run_cmd("{0} {1}".format(virtualenv_command, virtualenv_dir)))
                    self.stdout.write("Successfully created a virtual environment: %s" % envname)

                    # -----------------Installed in the virtual environment with module package--------------
                    env_basic_modal = ["Django"]
                    env_choice_list = ["djangorestframework", "xadmin", "celery", "redis"]
                    env_basic_choice_modal = []
                    env_extend_modal = []
                    for _modal in env_choice_list:
                        while True:
                            modal_require = self.get_input_data(force_str("The virtual environment need {0}?(Y/N):"
                                                                          .format(_modal)))
                            if modal_require == "Y" or modal_require == "y":
                                env_basic_choice_modal.append(_modal)
                                break
                            if modal_require == "N" or modal_require == "n":
                                break
                    while True:
                        other_modal = self.get_input_data(
                            force_str("If you have a public network, you can enter the other modules you need to "
                                      "install the package, do not need to enter 'n' to exit(such as: redis):"))
                        if other_modal:
                            if other_modal == "N" or other_modal == "n":
                                break
                            else:
                                other_modal_version = self.get_input_data(
                                    force_str("Please enter {0} version (format "
                                              "such as: 1.9.7, leave blank use"
                                              " latest version):"
                                              .format(other_modal)))
                                if other_modal_version == "":
                                    env_extend_modal.append("{0}".format(other_modal))
                                else:
                                    env_extend_modal.append("{0}=={1}".format(other_modal, other_modal_version))
                        else:
                            self.stderr.write("The package name cannot be empty!")

                    self.stdout.write("Installing package in virtualenv...")

                    # Installation package
                    if env_basic_modal:
                        self.stdout.write("--------------Install basic package--------------")
                        for _modal in env_basic_modal:
                            self.stdout.write("Installing {0}:".format(_modal))
                            self.stdout.write(run_cmd("{0} install --no-index --use-wheel "
                                                      "--find-links={1} {2}".format(pip_path, package_dir, _modal)))

                    if env_basic_choice_modal:
                        self.stdout.write("--------------Install basic choice package--------------")
                        for _modal in env_basic_choice_modal:
                            self.stdout.write("Installing {0}:".format(_modal))
                            self.stdout.write(run_cmd("{0} install --no-index --use-wheel "
                                                      "--find-links={1} {2}".format(pip_path, package_dir, _modal)))

                    if env_extend_modal:
                        self.stdout.write("--------------Install online choice package--------------")
                        for _modal in env_extend_modal:
                            self.stdout.write("Installing {0}:".format(_modal))
                            self.stdout.write(run_cmd("{0} install {1}".format(pip_path, _modal)))

                    self.stdout.write("--------------The current package of virtual environment--------------")
                    self.stdout.write(run_cmd("{0} list".format(pip_path)))

                else:
                    self.stderr.write("Sorry, the creation of virtual environment fails, "
                                      "the current python environment is not found in the virtual-related orders")

            # Create a random SECRET_KEY to put it in the main settings.
            options['secret_key'] = get_random_secret_key()

            # Create project
            self.stdout.write("Creating project...")
            super(Command, self).handle('project', project_name, target, **options)
            self.stdout.write("Successfully created a project: %s" % project_name)

            self.stdout.write("Modify the project configuration...")
            # New add some directory
            project_template_dir = os.path.join(project_dir, "template")
            project_static_dir = os.path.join(project_dir, "static")
            project_collectstatic_dir = os.path.join(project_dir, "collectstatic")
            project_media_dir = os.path.join(project_dir, "media")

            project_media_tempfiles_dir = os.path.join(project_media_dir, "tempfiles")
            project_media_tempfiles_log_dir = os.path.join(project_media_tempfiles_dir, "logs")

            os.popen("{0} {1}".format(mkdir_command, project_template_dir))  # template file directory
            os.popen("{0} {1}".format(mkdir_command, project_static_dir))  # static file directory
            os.popen("{0} {1}".format(mkdir_command, project_collectstatic_dir))  # collect static file directory
            os.popen("{0} {1}".format(mkdir_command, project_media_dir))  # media file directory
            os.popen("{0} {1}".format(mkdir_command, project_media_tempfiles_dir))  # template file  directory
            os.popen("{0} {1}".format(mkdir_command, project_media_tempfiles_log_dir))  # log file directory

            #: After adding project initialization settings
            project_project_settings_file = os.path.join(project_dir, project_name, "settings.py")
            project_init_settings(project_project_settings_file)

            self.stdout.write("Successfully modify project configure.")

            # Create app
            self.stdout.write("Create app...")
            while True:
                app_name = self.get_input_data(force_str("Please enter the name of the app (heavy star will be "
                                                         "overwritten, enter 'n' out!):"))
                if app_name == "N" or app_name == 'n':
                    break
                if self.check_name(app_name, "app"):
                    if app_name != project_name:
                        # 新建app
                        management.call_command("startapp", app_name)
                        if not os.path.exists(os.path.join(project_dir, app_name)):
                            run_cmd("{0} {1} {2}".format(move_command, app_name, project_dir))
                        # 相关app设置
                        self.stdout.write("Modify the app configuration...")
                        app_init_settings(project_project_settings_file, app_name)
                        self.stdout.write("Successfully create app: {0}".format(app_name))

                    else:
                        self.stdout.write("Sorry, the app failed to create and the {0} name can not be the same as "
                                          "the project name!".format(app_name))

        except KeyboardInterrupt:
            self.stderr.write("\nOperation cancelled.")
            sys.exit(1)

        except NotRunningInTTYException:
            self.stdout.write(
                "Project creation skipped due to not running in a TTY. "
                "You can run `manage.py createproject` in your project "
                "to create one manually."
            )
            sys.exit(1)

    def get_input_data(self, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = raw_input(message)
        if default and raw_value == '':
            raw_value = default

        return raw_value

    def check_name(self, name, name_attribute):
        """
        Check whether the name is conform to the specifications
        :param name: name string
        :param name_attribute: name attribute
        :return: True or False
        """
        # if hasattr(self.stdin, 'isatty') and not self.stdin.isatty():
        #     raise NotRunningInTTYException("Not running in a TTY")

        if name is None:
            self.stderr.write("you must provide one %s name" % name_attribute)
            return False
        # If it's not a valid directory name.
        if six.PY2:
            if not re.search(r'^[_a-zA-Z]\w*$', name):
                # Provide a smart error message, depending on the error.
                if not re.search(r'^[_a-zA-Z]', name):
                    message = 'make sure the name begins with a letter or underscore'
                else:
                    message = 'use only numbers, letters and underscores'
                self.stderr.write("%r is not a valid %s name. Please %s." %
                                   (name, name_attribute, message))
                return False
        else:
            if not name.isidentifier():
                self.stderr.write(
                    "%r is not a valid %s name. Please make sure the name is "
                    "a valid identifier." % (name, name_attribute)
                )
                return False

        # Check that the project_name cannot be imported.
        try:
            import_module(name)
        except ImportError:
            pass
        else:
            self.stderr.write(
                "%r conflicts with the name of an existing Python module and "
                "cannot be used. Please try another name." % name
            )
            return False

        return True
