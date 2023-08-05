"""
Webmaster: API View
This endpoint illustrates how to use the is as a REST API
"""

from webmaster import (View, flash, abort, session, request, url_for,
                       redirect, flash_data, get_flashed_data)
from webmaster.decorators import (route, menu, template, plugin, methods,
                                  render_as_json, render_as_xml)
from webmaster.exceptions import (ApplicationError, ModelError, UserError)


@render_as_json
class Index(View):

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

    def test(self, id):
        return {
            "desc": "This is a test",
            "id": int(id)
        }


