""" Webmaster """

from webmaster import (View, flash, abort, session, request, url_for,
                       redirect, flash_data, get_flashed_data)
from webmaster.decorators import (route, menu, template, plugin, methods,
                                  render_as_json, render_as_xml,
                                  require_user_roles, login_required,
                                  no_login_required)
from webmaster.ext import (mailer, cache, storage, recaptcha, csrf)
from webmaster.packages import (user, publisher)
from webmaster.exceptions import (ApplicationError, ModelError, UserError)
from application import model

# ------------------------------------------------------------------------------
# /admin
# Creates and admin view
# Extends publisher.admin to manage posts
# Extends user.admin to manage users
#

@menu("My Admin", group_name="admin")
@template("Webmaster/admin/layout.html", brand_name="Admin 2.0")
@plugin(user.admin, model=model.User, menu={"group_name": "admin"})
@plugin(publisher.admin, model=model.Publisher, menu={"group_name": "admin"})
class Index(View):

    @menu("All")
    def index(self):
        return {}


