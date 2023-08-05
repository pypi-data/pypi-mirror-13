"""
Error Page

This plugin to display customize error page

Can be called as standalone
"""
from __future__ import division
import logging
from webmaster import (View, register_package, abort)
from webmaster import exceptions
from sqlalchemy.exc import SQLAlchemyError

register_package(__package__)

class SQLAlchemyHTTPException(exceptions.HTTPException):

    code = 500
    description = "SQLAlchemy Error"

    def __init__(self, error):
        """Takes an optional list of valid http methods
        starting with werkzeug 0.3 the list will be mandatory."""
        exceptions.HTTPException.__init__(self, self.description)
        #self.valid_methods = valid_methods
        # statement, params, orig, message


    @classmethod
    def wrap(cls, exception, name=None):
        """This method returns a new subclass of the exception provided that
        also is a subclass of `BadRequest`.
        """
        ("SQLAlchemy Error")
        httpexc.code = 500
        return httpexc


def error_page(template_dir=None):

    if not template_dir:
        template_dir = "Webmaster/Package/ErrorPage"
    template_page = "%s/index.html" % template_dir

    class ErrorPage(View):

        @classmethod
        def register(cls, app, **kwargs):
            super(cls, cls).register(app, **kwargs)

            @app.errorhandler(400)
            @app.errorhandler(401)
            @app.errorhandler(403)
            @app.errorhandler(404)
            @app.errorhandler(405)
            @app.errorhandler(406)
            @app.errorhandler(408)
            @app.errorhandler(409)
            @app.errorhandler(410)
            @app.errorhandler(429)
            @app.errorhandler(500)
            @app.errorhandler(501)
            @app.errorhandler(502)
            @app.errorhandler(503)
            @app.errorhandler(504)
            @app.errorhandler(505)
            @app.errorhandler(SQLAlchemyError)
            def register_error(error):

                if isinstance(error, SQLAlchemyError):
                    error = SQLAlchemyHTTPException(error)

                if int(error.code // 100) != 4:
                    _error = str(error)
                    _error += " - HTTException Code: %s" % error.code
                    _error += " - HTTException Description: %s" % error.description
                    print "-" * 80
                    print _error
                    print "-" * 80
                    logging.error(_error)

                cls.meta_tags(title="Error %s" % error.code)
                return cls.render_(error=error, template_=template_page)

    return ErrorPage

e = error_page()