"""
Juice
"""

from juice import (View, flash, abort, request, url_for, redirect)
from juice.decorators import (route, menu, template, plugin, methods)
from juice.ext import (storage, )
from juice.plugins import (contact_page, )

# ------------------------------------------------------------------------------

@plugin(contact_page.contact_page, menu={"name": "Contact Us", "order": 3})
class Index(View):

    @menu("Home", order=1)
    def index(self):
        self.meta_tags(title="Hello View!")
        return {}

    @menu("Boom", order=4)
    @template("Index/index2.html", version="1.6.9.6")
    def boom(self):
        return {}

    @menu("Upload Image Demo", order=2)
    @methods("GET", "POST")
    def upload(self):
        self.meta_tags(title="Upload Demo")
        if request.method == "POST":
            try:
                _file = request.files.get("file")
                if _file:
                    my_object = storage.upload(_file,
                                               prefix="demo/",
                                               public=True,
                                               allowed_extensions=["gif", "jpg",
                                                                   "jpeg", "png"]
                                               )
                    if my_object:
                        return redirect(url_for("Index:upload",
                                                object_name=my_object.name))
            except Exception as e:
                flash(e.message, "error")
            return redirect(url_for("Index:upload"))

        my_object = None
        object_name = request.args.get("object_name")
        if object_name:
            my_object = storage.get(object_name=object_name)

        return {"my_object": my_object}


    @menu("Forms", order=4)
    @methods("GET", "POST")
    def forms(self):
        self.meta_tags(title="My Form")
        if request.method == "POST":
            flash("Form was submitted successfully", "success")
            return redirect(url_for("Index:forms"))
        return {}

@menu("Dropdown Menu", order=5)
class Docs(View):

    @menu("All")
    def index(self):
        return {}

    @menu("External Link", url="https://google.com", target="_blank")
    def google_link(self):
        return {}



