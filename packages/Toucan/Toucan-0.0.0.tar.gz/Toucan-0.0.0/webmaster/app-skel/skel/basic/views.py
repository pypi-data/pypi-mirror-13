"""

Webmaster: Simple View

"""

from webmaster import (View, flash, abort, session, request, url_for,
                       redirect, flash_data, get_flashed_data)
from webmaster.decorators import (route, menu, template, plugin, methods,
                                  render_as_json, render_as_xml)
from webmaster.ext import (mailer, cache, storage, recaptcha, csrf)
from webmaster.packages import (contact_page,)
from webmaster.exceptions import (ApplicationError, ModelError, UserError)


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
