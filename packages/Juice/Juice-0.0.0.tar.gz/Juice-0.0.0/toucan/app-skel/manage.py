"""
:: Toucan ::

command line tool

To run setup >
    python manage.py setup
"""

import click
from toucan import get_env_config
import toucan.utils as utils
from application import config, model
from toucan.packages import user, publisher

conf = get_env_config(config)

# ------------------------------------------------------------------------------


def setup_default():

    # Create all db
    model.db.create_all()

    # Setup User
    admin_email = conf.APPLICATION_ADMIN_EMAIL
    password = utils.generate_random_string()
    if user.setup(model.User, admin_email=admin_email, password=password):
        click.echo("---- Setup SUPER ADMIN User ----")
        click.echo("- Admin Email: %s" % admin_email)
        click.echo("- Admin Password: %s" % password)
        click.echo("-" * 40)
        click.echo("")

    # Setup Publisher
    admin_user = model.User.User.get_by_email(admin_email)
    if admin_user and admin_user.role.name.lower() == "superadmin":
        click.echo("---- Setup PUBLISHER ----")
        if publisher.setup(model.Publisher, admin_user_id=admin_user.id):
            click.echo("Completed")
        click.echo("-" * 40)
        click.echo("")

# ------------------------------------------------------------------------------

@click.group()
def cli():
    pass

@cli.command()
def setup():
    """ Setup """
    click.echo(">> Setup...")
    setup_default()

if __name__ == "__main__":
    click.echo("")
    click.echo("#" * 80)
    click.echo(":: Toucan Manager ::")
    click.echo("")

    cli()


