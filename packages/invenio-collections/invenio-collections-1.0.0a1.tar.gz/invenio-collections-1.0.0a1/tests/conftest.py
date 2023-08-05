# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os

import pytest
from flask import Flask
from flask_babelex import Babel
from flask_breadcrumbs import Breadcrumbs
from flask_cli import FlaskCLI
from flask_menu import Menu
from invenio_db import InvenioDB, db

from invenio_collections import InvenioCollections
from invenio_collections.views import blueprint


@pytest.fixture()
def app(request):
    """Flask application fixture."""
    app = Flask('testapp')
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI',
                                          'sqlite://'),
    )
    FlaskCLI(app)
    Babel(app)
    Menu(app)
    Breadcrumbs(app)
    InvenioDB(app)
    InvenioCollections(app)

    app.register_blueprint(blueprint)

    def teardown():
        with app.app_context():
            db.drop_all()

    request.addfinalizer(teardown)

    with app.app_context():
        db.create_all()

    return app
