"""
---------------------------------- JUICE:CLI -----------------------------------

A command line tool to manage your app

To run, Juice already has a hook that you can directly use in the command line

Run:

    juice:cli

It will show the list of actions available

To run an action:

    juice:cli $action


By default it will use the dev environment. On production, change the env

    ENV=PRODUCTION juice:cli $action


If you are using Propel, the example below will run the setup in the production
environment

    scripts:

      # Run before all
      before_all:
        -
          command: "juice:cli setup"
          environment: ENV="Production"

-----

Examples:

@app.cli.command(with_appcontext=False)
def hello():
    ''' Hello Description '''
    print(":Hello")
    print("Hello From the Other Side!")

@app.cli.command(with_appcontext=False)
@click.option("--id")
def user(id):
    ''' This is the user's description '''
    print("User ID: %s" % id)


- The hello() can be called

    juice:cli hello

- The user() can be called:

    juice:cli user --id 1

--------------------------------------------------------------------------------

"""

from juice import get_env_config, abort
import juice.utils as utils
from application import config, model
from juice.plugins import user, publisher
from juice.ext import mailman
from www import app
import click

# Load the config
conf = get_env_config(config)

# ------------------------------------------------------------------------------


def setup_admin_user_publisher():
    """
    Setup Juice User and Publisher Admin
    :return:
    """

    # ==== Create All Tables from model.py === #

    model.db.create_all()

    # ==== Setup User Admin === #

    admin_email = conf.APPLICATION_ADMIN_EMAIL
    if not admin_email:
        print("ERROR: APPLICATION_ADMIN_EMAIL is empty")
        exit()

    password = utils.generate_random_string()
    if user.setup(model.User,
                  admin_email=admin_email,
                  password=password):

        if mailman.validated:
            body = "Admin Password: %s" % password
            mailman.send(to=admin_email, subject="Admin Password", body=body)

        print("---- Setup SUPER ADMIN User ----")
        print("- Admin Email: %s" % admin_email)
        print("- Admin Password: %s" % password)
        print("-" * 40)
        print("")

    # ==== Setup Publisher === #

    # admin user
    admin_user = model.User.User.get_by_email(admin_email)

    # Set default categories and post types
    post_categories = ["Uncategorized"]
    post_types = ["Page", "Blog", "Document", "Other"]

    if admin_user and admin_user.role.name.lower() == "superadmin":
        print("---- Setup PUBLISHER ----")
        if publisher.setup(model.Publisher,
                           admin_user_id=admin_user.id,
                           post_types=post_types,
                           post_categories=post_categories):
            print("Completed")
        print("-" * 40)
        print("")

# ------------------------------------------------------------------------------

@app.cli.command(with_appcontext=False)
def setup():

    """ Setup """
    print("::Setup")

    setup_admin_user_publisher()

    print("Done!")






