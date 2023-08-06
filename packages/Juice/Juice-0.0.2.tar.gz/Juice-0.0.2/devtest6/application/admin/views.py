""" Juice """

from juice import (View, flash, abort, session, request, url_for,
                       redirect, flash_data, get_flashed_data)
from juice.decorators import (route, menu, template, plugin, methods,
                                  render_as_json, render_as_xml,
                                  require_user_roles, login_required,
                                  no_login_required)
from juice.ext import (mailer, cache, storage, recaptcha, csrf)
from juice.packages import (user, publisher)
from juice.exceptions import (ApplicationError, ModelError, UserError)
from application import model

# ------------------------------------------------------------------------------
# /admin
# Creates and admin view
# Extends publisher.admin to manage posts
# Extends user.admin to manage users
#

@menu("My Admin", group_name="admin")
@template("Juice/admin/layout.html", brand_name="Admin 2.0")
@plugin(user.admin, model=model.User, menu={"group_name": "admin"})
@plugin(publisher.admin, model=model.Publisher, menu={"group_name": "admin"})
class Index(View):

    @menu("All")
    def index(self):
        return {}


