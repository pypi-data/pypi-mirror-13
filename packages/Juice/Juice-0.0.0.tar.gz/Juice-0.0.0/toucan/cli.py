"""
Toucan

Command line tool

web-portfolio -c project_name

"""

import os
import re
import sys
import logging
import importlib
import pkg_resources
import utils
import __about__
import click
import yaml
import subprocess

CWD = os.getcwd()
SKELETON_DIR = "app-skel"
APPLICATION_DIR = "%s/application" % CWD
APPLICATION_DATA_DIR = "%s/data" % APPLICATION_DIR


def get_project_dir_path(project_name):
    return "%s/%s" % (APPLICATION_DIR, project_name)


def copy_resource(src, dest):
    """
    To copy package data to destination
    """
    dest = (dest + "/" + os.path.basename(src)).rstrip("/")
    if pkg_resources.resource_isdir("toucan", src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        for res in pkg_resources.resource_listdir(__name__, src):
            copy_resource(src + "/" + res, dest)
    else:
        if os.path.splitext(src)[1] not in [".pyc"]:
            with open(dest, "wb") as f:
                f.write(pkg_resources.resource_string(__name__, src))


def create_project(project_name, skel="basic"):
    """
    Create the project
    """
    project_dir = get_project_dir_path(project_name)
    app_tpl = pkg_resources.resource_string(__name__, '%s/app.py' % (SKELETON_DIR))
    propel_tpl = pkg_resources.resource_string(__name__, '%s/propel.yml' % (SKELETON_DIR))
    config_tpl = pkg_resources.resource_string(__name__, '%s/config.py' % (SKELETON_DIR))
    model_tpl = pkg_resources.resource_string(__name__, '%s/model.py' % (SKELETON_DIR))
    manage_tpl = pkg_resources.resource_string(__name__, '%s/manage.py' % (SKELETON_DIR))

    app_file = "%s/app_%s.py" % (CWD, project_name)
    requirements_txt = "%s/requirements.txt" % CWD
    propel_yml = "%s/propel.yml" % CWD
    config_py = "%s/config.py" % APPLICATION_DIR
    model_py = "%s/model.py" % APPLICATION_DIR
    manage_py = "%s/manage.py" % CWD
    extras_dir = "%s/extras" % APPLICATION_DIR

    dirs = [
        APPLICATION_DIR,
        APPLICATION_DATA_DIR,
        extras_dir,
        project_dir
    ]
    for d in dirs:
        if not os.path.isdir(d):
            os.makedirs(d)

    files = [
        ("%s/__init__.py" % APPLICATION_DIR, "# Toucan"),
        (config_py, config_tpl),
        (model_py, model_tpl),
        (app_file, app_tpl.format(project_name=project_name)),
        (requirements_txt, "%s==%s" % (__about__.name, __about__.version)),
        (propel_yml, propel_tpl.format(project_name=project_name)),
        (manage_py, manage_tpl),
        ("%s/__init__.py" % extras_dir, "# /application/extras: This is where you can place you custom/shared modules "),
    ]
    for f in files:
        if not os.path.isfile(f[0]):
            with open(f[0], "wb") as f0:
                f0.write(f[1])

    copy_resource("%s/skel/%s/" % (SKELETON_DIR, skel), project_dir)
    copy_resource("%s/%s/" % (SKELETON_DIR, "data"), APPLICATION_DATA_DIR)

# ------------------------------------------------------------------------------

class GitPush(object):
    """
    A class that allows you to deploy with git without setting up git remotes

    """
    def __init__(self, CWD, config_file="propel.yml"):
        """
        :param CWD: Current working dir
        :param config_file: the config file
        :return:
        """
        key = "git-remotes"
        self.prefix = "webcli"
        f = CWD + "/" + config_file
        with open(f) as pf:
            config = yaml.load(pf)
        self.config = config[key]
        self.CWD = CWD

    def run(self, cmd):
        subprocess.call(cmd.strip(), shell=True)

    def remote(self, name, force=False):
        remotes = self.config[name]
        name = "%s_push__%s" % (self.prefix, name)
        cmd = self._gen_git_remote_command(name, remotes)
        cmd += self._gen_git_push_remote(name, force)
        cmd += self._gen_git_remove_remote(name)
        self.run("cd %s; %s" % (self.CWD, cmd))

    def all(self, force=False):
        l = []
        [l.extend(h) for k, h in self.config.items()]
        remotes = list(set(l))
        name = "%s_push__all" % self.prefix
        cmd = self._gen_git_remote_command(name, remotes)
        cmd += self._gen_git_push_remote(name, force)
        cmd += self._gen_git_remove_remote(name)
        self.run("cd %s; %s" % (self.CWD, cmd))

    def reset_git(self):
        cmd = ""
        for k, values in self.config.items():
            cmd += self._gen_git_remote_command(k, values)
        self.run("cd %s; %s" % (self.CWD, cmd))

    def _gen_git_push_remote(self, name, force=False):
        force = " -f" if force else ""
        return "git push %s %s master;" % (force, name)

    def _gen_git_remove_remote(self, name):
        return "git remote remove %s;" % name

    def _gen_git_remote_command(self, name, remotes):
        """
        Generate the push command for a remote
        :param name (str): the remote name
        :param remotes (list): list of
        :return str:
        """
        if not isinstance(remotes, list):
            raise TypeError("'remotes' must be of list type")

        cmd = self._gen_git_remove_remote(name)
        cmd += "git remote add %s %s;" % (name, remotes[0])
        if len(remotes) > 1:
            for h in remotes:
                cmd += "git remote set-url %s --push --add %s;" % (name, h)
        return cmd

# ------------------------------------------------------------------------------

def _addCWDToSysPath():
    sys.path.append(CWD)

def _title(title=None):
    _description = "-" * 80
    _description += "\n%s %s" % (__about__.name, __about__.version)
    click.echo(_description)
    click.echo("")
    if title:
        click.echo("** %s **" % title)
        click.echo("")

_object_name_regex = re.compile('[^a-zA-Z]')
def format_app_name(name):
    return _object_name_regex.sub("", name)

def get_app_serve_module(project):
    _addCWDToSysPath()
    if "app_" not in project:
        project = format_app_name(project)
        project = "app_%s" % project
    return importlib.import_module(project)

def import_project_module(module):
    _addCWDToSysPath()
    return importlib.import_module(module)

@click.group()
def cli(): pass

@cli.command()
@click.option("--project", "-p", default="www")
@click.option("--skel", "-s", default="basic")
def create(project, skel):
    """  Create a new App """

    app = format_app_name(project)

    _title("Create New Project ...")
    click.echo("- Project: %s " % app)

    create_project(app, skel)

    click.echo("- Sweet! Your new project [ %s ] has been created" % app)
    click.echo("- Location: [ application/%s ]" % app)
    click.echo("")
    click.echo("> What's next?")
    click.echo("- Edit the config [ application/config.py ] ")
    click.echo("- If necessary edit and run the manager [ python manage.py setup ]")
    click.echo("- Launch local server, run [ toucan serve -p %s ]" % app)
    click.echo("")
    click.echo("*" * 80)

@cli.command()
@click.option("--project", "-p", default="www")
def buildassets(project):
    """
    Build web assets static files
    """

    _title("Build Project's assets files from bundles ...")
    click.echo("- Project: %s " % project)
    click.echo("")
    _buildassets(project)
    click.echo("Done!")

def _buildassets(app):

    from webassets.script import CommandLineEnvironment

    module = get_app_serve_module(app)
    assets_env = module.app.jinja_env.assets_environment

    log = logging.getLogger('webassets')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)

    cmdenv = CommandLineEnvironment(assets_env, log)
    cmdenv.build()

@cli.command()
@click.option("--project", "-p", default="www")
def assets2s3(project):
    """ To upload static web assets files to S3"""

    import flask_s3
    module = get_app_app_module(project)

    _title("Build and  Upload static assets files to S3 ...")
    click.echo("- Project: %s " % project)
    click.echo("")

    _buildassets(project)
    flask_s3.create_all(module.app)
    click.echo("Done!")

@cli.command()
@click.option("--project", "-p", default="www")
@click.option("--port", default=5000)
def serve(project, port):
    """ Serve a project in Local Development environment """

    _title("Start server in Local environment ...")
    click.echo("- App: %s " % project)
    click.echo("- Port: %s" % port)
    click.echo("")

    module = get_app_serve_module(project)

    extra_dirs = [CWD,]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    extra_files.append(filename)
    module.app.run(debug=True, host='0.0.0.0', port=port, extra_files=extra_files)

@cli.command()
@click.option("--remote", "-r", default="web")
@click.option("--all", "-a", default="")
#@click.option("--force", "-f", default=False)
def push(remote, all):
    """ To Git Push application to remote git servers """

    _title("Git Push Application ...")

    gp = GitPush(CWD, "propel.yml")

    force = False
    reset_git = False
    if remote:
        click.echo("Remote: %s ..." % remote)
        gp.remote(name=remote)
    elif all:
        click.echo("All remotes...")
        gp.all()
    elif reset_git:
        pass

    click.echo("Done!")

