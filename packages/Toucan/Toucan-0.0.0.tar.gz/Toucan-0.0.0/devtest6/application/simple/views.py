""" Toucan """

from toucan import (View, flash, abort, session, request, url_for,
                       redirect, flash_data, get_flashed_data)
from toucan.decorators import (route, menu, template, plugin, methods,
                                  render_as_json, render_as_xml,
                                  require_user_roles, login_required,
                                  no_login_required)
from toucan.ext import (mailer, cache, storage, recaptcha, csrf)
from toucan.exceptions import (ApplicationError, ModelError, UserError)


# ------------------------------------------------------------------------------
# /admin
# Creates and admin view
# Extends publisher.admin to manage posts
# Extends user.admin to manage users
#

error.render(json)

class Index(View):

    @menu("Home", order=1)
    def index(self):
        return {}

    @menu("About Us", order=3)
    def about_us(self):
        return {}

@menu("Music", order=2)
class Music(View):

    @menu("Browse All")
    def index(self):
        return {}

    def get(self, id):
        return {
            "album_name": "Webmaster",
            "artist_name": "Mardix",
            "genre": "Hip-Hop"
        }

    @menu("Search")
    def search(self):
        return {}

    @methods("POST")
    def submit(self):
        return {}


