"""
Webmaster
Your Application's View
"""

from webmaster import (View, flash, abort, session, request, url_for,
                       redirect, flash_data, get_flashed_data)
from webmaster.decorators import (route, menu, template, plugin, methods,
                                  render_as_json, render_as_xml,
                                  require_user_roles, login_required,
                                  no_login_required)
from webmaster.ext import (mailer, cache, storage, recaptcha, csrf)
from webmaster.packages import (contact_page, user, publisher)
from webmaster.exceptions import (ApplicationError, ModelError, UserError)
from application import model

# ------------------------------------------------------------------------------
# /
# This is the entry point of the site
# All root based (/) endpoint could be placed in here
# It extends the contact_page module, to be accessed at '/contact'
#


@menu("Main Menu", order=1)
@plugin(contact_page.contact_page)
@route("/")
class Index(View):

    @menu("Home", order=1)
    def index(self):
        self.meta_tags(title="Hello View!")
        return {}

    @menu("Boom")
    @template("Index/index2.html", version="1.6.9.6")
    def boom(self):
        return {}

# ------------------------------------------------------------------------------
# /account
# The User Account section
# Extends user.account which forces the whole endpoint to be authenticated
# If an action needs not authentication, @no_login_required can be added
#

@menu("My Account", group_name="account", order=3, align_right=True,
      visible=False, show_profile_avatar=True, show_profile_name=True)
@plugin(user.auth, model=model.User)
class Account(View):

    @menu("My Account", order=1)
    def index(self):
        self.meta_tags(title="My Account")
        return {}

    @menu("Upload Image Demo", order=2)
    @route("upload", methods=["GET", "POST"])
    def upload(self):

        self.meta_tags(title="Upload Demo")

        if request.method == "POST":
            try:
                _file = request.files.get('file')
                if _file:
                    my_object = storage.upload(_file,
                                               prefix="demo/",
                                               public=True,
                                               allowed_extensions=["gif", "jpg", "jpeg", "png"])
                    if my_object:
                        return redirect(url_for("Account:upload", object_name=my_object.name))
            except Exception as e:
                flash_error(e.message)
            return redirect(url_for("Account:upload"))

        my_object = None
        object_name = request.args.get("object_name")
        if object_name:
            my_object = storage.get(object_name=object_name)

        return {"my_object": my_object}

    @menu("No Login", order=3)
    @no_login_required
    def no_login(self):
        return {}



# ------------------------------------------------------------------------------
# /blog
# Using the publisher.page, we created a blog
#

@plugin(publisher.page,
        model=model.Publisher,
        query={"types": ["blog"]},
        slug="slug",
        title="Blog",
        endpoint="",
        menu={"name": "Blog"})
class Blog(View):
    pass

# ------------------------------------------------------------------------------
# /admin
# Creates and admin view
# Extends publisher.admin to manage posts
# Extends user.admin to manage users
#

@menu("My Admin", group_name="admin")
@template("Webmaster/admin/layout.html", brand_name="The Admin 2.0")
@plugin(user.admin, model=model.User, menu={"group_name": "admin"})
@plugin(publisher.admin, model=model.Publisher, menu={"group_name": "admin"})
@route("/admin")
class Admin(View):

    @menu("All")
    def index(self):
        return {}


# ------------------------------------------------------------------------------
# /api
# This endpoint illustrates and /api endpoint
# All actions return json
# @methods is used to change the required method on the action
#
@render_as_json
class Api(View):

    def index(self):
        return {
            "name": "My API",
            "version": 1.0
        }

    def get(self, id):
        return {
            "description": "This is a get",
            "id": id
        }

    @methods("post")
    def test(self, id):
        return {
            "desc": "This is a test",
            "id": int(id)
        }


