"""
--------------------------------------------------------------------------------
    /$$$$$ /$$   /$$ /$$$$$$  /$$$$$$  /$$$$$$$$
   |__  $$| $$  | $$|_  $$_/ /$$__  $$| $$_____/
      | $$| $$  | $$  | $$  | $$  \__/| $$
      | $$| $$  | $$  | $$  | $$      | $$$$$
 /$$  | $$| $$  | $$  | $$  | $$      | $$__/
| $$  | $$| $$  | $$  | $$  | $$    $$| $$
|  $$$$$$/|  $$$$$$/ /$$$$$$|  $$$$$$/| $$$$$$$$
 \______/  \______/ |______/ \______/ |________/

--------------------------------------------------------------------------------
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
import sh

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
    if pkg_resources.resource_isdir("juice", src):
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
    manage_tpl = pkg_resources.resource_string(__name__, '%s/cli.py' % (SKELETON_DIR))

    app_file = "%s/%s.py" % (CWD, project_name)
    requirements_txt = "%s/requirements.txt" % CWD
    propel_yml = "%s/propel.yml" % CWD
    config_py = "%s/config.py" % APPLICATION_DIR
    model_py = "%s/model.py" % APPLICATION_DIR
    manage_py = "%s/cli.py" % CWD
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
        ("%s/__init__.py" % APPLICATION_DIR, "# Juice"),
        (config_py, config_tpl),
        (model_py, model_tpl),
        (app_file, app_tpl.format(project_name=project_name)),
        (requirements_txt, "%s==%s" % (__about__.__title__, __about__.__version__)),
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


def git_push_to_master(cwd, hosts, force=False):
    """
    To push to master
    :param cwd:
    :param hosts:
    :param force:
    :return:
    """
    with sh.pushd(cwd):
        name = "__juice_push"
        force = " -f" if force else ""

        if sh.git("status", "--porcelain").strip():
            raise Exception("Repository is UNCLEAN. Commit your changes")

        remote_list = sh.git("remote").strip().split()
        if name in remote_list:
            sh.git("remote", "remove", name)
        sh.git("remote", "add", name, hosts[0])
        if len(hosts) > 1:
            for h in hosts:
                sh.git("remote", "set-url", name, "--push", "--add", h)
            sh.git("push", force, name, "master")
            sh.git("remote", "remove", name)


def get_git_remotes_hosts(cwd, key=None, file="propel.yml"):
    """
    Returns the remote hosts in propel
    :param cwd:
    :param key:
    :param file:
    :return:
    """
    with open("%s/%s" % (cwd, file)) as f:
        config = yaml.load(f)["git-remotes"]
    return config[key] if key else config

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


def cwd_to_sys_path():
    sys.path.append(CWD)


def import_module(project):
    cwd_to_sys_path()
    project = sanitize_name(project)
    return importlib.import_module(project)


def sanitize_name(name):
    return re.compile('[^a-zA-Z]').sub("", name)


def header(title=None):
    print(__doc__)
    print("v. %s" % __about__.__version__)
    print("")
    if title:
        print("** %s **" % title)
        print("")


def build_assets(mod):
    from webassets.script import CommandLineEnvironment

    module = import_module(mod)
    assets_env = module.app.jinja_env.assets_environment

    log = logging.getLogger('webassets')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)

    cmdenv = CommandLineEnvironment(assets_env, log)
    cmdenv.build()


@click.group()
def cli(): pass


@cli.command()
@click.argument("project")
@click.option("--skel", "-s", default="app")
def create(project, skel):
    """  Create a new App """

    app = sanitize_name(project)

    header("Create New Project ...")
    print("- Project: %s " % app)

    create_project(app, skel)

    print("----- Juicy! ----")
    print("")
    print("- Your new project [ %s ] has been created" % app)
    print("- Location: [ application/%s ]" % app)
    print("")
    print("> What's next?")
    print("- Edit the config [ application/config.py ] ")
    print("- If necessary edit and run the command [ juice:cli setup ]")
    print("- Launch local server, run [ juice serve %s ]" % app)
    print("")
    print("*" * 80)


@cli.command()
@click.argument("project")
def buildassets(project):
    """
    Build web assets static files
    """

    header("Build Project's assets files from bundles ...")
    print("- Project: %s " % project)
    print("")
    build_assets(project)
    print("Done!")


@cli.command()
@click.argument("project")
def assets2s3(project):
    """ To upload static web assets files to S3"""

    import flask_s3
    module = get_app_app_module(project)

    header("Build and  Upload static assets files to S3 ...")
    print("- Project: %s " % project)
    print("")

    build_assets(project)
    flask_s3.create_all(module.app)
    print("Done!")


@cli.command()
@click.argument("project")
@click.option("--port", "-p", default=5000)
@click.option("--no-watch", default=False)
def serve(project, port, no_watch):
    """ Serve a project in Local Development environment """

    header("Serve application on local ")
    print("- Project: %s " % project)
    print("")
    print("- Port: %s" % port)
    print("")

    module = import_module(project)

    extra_files = []
    if not no_watch:
        extra_dirs = [CWD,]
        extra_files = extra_dirs[:]
        for extra_dir in extra_dirs:
            for dirname, dirs, files in os.walk(extra_dir):
                for filename in files:
                    filename = os.path.join(dirname, filename)
                    if os.path.isfile(filename):
                        extra_files.append(filename)
    module.app.run(debug=True,
                   host='0.0.0.0',
                   port=port,
                   extra_files=extra_files)

@cli.command()
@click.argument("remote")
@click.option("--all", "-a", default="")
#@click.option("--force", "-f", default=False)
def push(remote, all, force=False):
    """ To Git Push application to remote git servers """

    header("Git Push Application ...")

    if all:
        print("All remotes...")
        hosts = get_git_remotes_hosts(CWD)
        git_push_to_master(cwd=CWD, hosts=hosts, force=force)
    elif remote:
        print("Remote: %s" % remote)
        hosts = get_git_remotes_hosts(CWD, remote)
        git_push_to_master(cwd=CWD, hosts=hosts, force=force)
    print("Done!")

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def app_cli():
    """
    Run the application CLI
    :return:
    """
    try:
        module = import_module("cli")
        module.app.cli()
    except ImportError as e:
        print("")
        print("IMPORT ERROR: Missing 'cli.py' "
              "at the root of your application: %s" % CWD)
        print("")
