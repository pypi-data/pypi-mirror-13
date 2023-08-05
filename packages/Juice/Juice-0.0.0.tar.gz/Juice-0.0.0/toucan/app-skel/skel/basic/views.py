"""

Toucan: Simple View

"""

from toucan import (View, flash, abort, session, request, url_for, redirect,
                    flash_data, get_flashed_data)
from toucan.decorators import (route, menu, template, plugin, methods,
                               render_as_json, render_as_xml)
from toucan.exceptions import (ApplicationError, ModelError, UserError)
from toucan.ext import (mailman, storage, cache, recaptcha, csrf)
from toucan.plugins import (contact_page,)


# ------------------------------------------------------------------------------
# /
# This is the entry point of the site
# All root based (/) endpoint could be placed in here
#
@menu("Main Menu", order=1)
class Index(View):

    @menu("Home", order=1)
    def index(self):
        self.meta_tags(title="Hello View!")
        return {}

    @menu("Boom")
    @template("Index/index2.html", version="1.6.9.6")
    def boom(self):
        return {}

@menu("Docs", order=2)
class Docs(View):

    @menu("All")
    def index(self):
        return {}


@plugin(contact_page.contact_page, menu={"name": "Contact Us", "order": 3})
@route("/")
class Index2(View):
    pass
