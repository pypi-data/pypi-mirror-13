"""
Webmaster

model.py

You may place your models here.
"""

from active_alchemy import SQLAlchemy
import config
from webmaster import init_app, get_env_config
from webmaster.packages import user, publisher

# The config
conf = get_env_config(config)

# Connect the DB
db = SQLAlchemy(conf.SQL_URI)

# Attach the Active SQLAlchemy
init_app(db.init_app)

# ------------------------------------------------------------------------------

# User Model
User = user.model(db)

# Post Model
Publisher = publisher.model(User.User)

