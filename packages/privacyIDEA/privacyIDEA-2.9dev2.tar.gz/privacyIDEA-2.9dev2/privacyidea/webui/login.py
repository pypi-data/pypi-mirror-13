# -*- coding: utf-8 -*-
#
# http://www.privacyidea.org
# (c) cornelius kölbel, privacyidea.org
#
# 2015-11-04 Cornelius Kölbel <cornelius@privacyidea.org>
#            Add REMOTE_USER check
# 2014-12-22 Cornelius Kölbel, <cornelius@privacyidea.org>
#
# This code is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
__doc__ = """This is the starting point for the single web application.
Other html code is dynamically loaded via angularJS and located in
/static/views/...
"""
__author__ = "Cornelius Kölbel, <cornelius@privacyidea.org>"

from flask import (Blueprint, render_template, request, current_app)
from privacyidea.api.lib.prepolicy import is_remote_user_allowed

DEFAULT_THEME = "/static/contrib/css/bootstrap-theme.css"

login_blueprint = Blueprint('login_blueprint', __name__)


@login_blueprint.route('/', methods=['GET'])
def single_page_application():
    instance = request.script_root
    if instance == "/":
        instance = ""
    # The backend URL should come from the configuration of the system.
    backend_url = ""

    # The default theme. We can change this later
    theme = current_app.config.get("PI_CSS", DEFAULT_THEME)

    browser_lang = request.accept_languages.best_match(["en", "de"])
    # check if login with REMOTE_USER is allowed.
    remote_user = ""
    if is_remote_user_allowed(request):
        remote_user = request.remote_user
    return render_template("index.html", instance=instance,
                           backendUrl=backend_url,
                           browser_lang=browser_lang,
                           remote_user=remote_user,
                           theme=theme)

