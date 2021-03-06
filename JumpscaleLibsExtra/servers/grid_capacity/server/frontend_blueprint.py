# DO NOT EDIT THIS FILE. This file will be overwritten when re-running go-raml.
import os
from flask import Blueprint, send_from_directory, render_template, request, session, abort, redirect
from .flask_itsyouonline import requires_auth, force_invalidate_session, ITSYOUONLINE_KEY
from .models import NodeRegistration, FarmerRegistration, FarmerNotFoundError
import jwt

frontend_bp = Blueprint("frontent", __name__)

dir_path = os.path.dirname(os.path.realpath(__file__))


@frontend_bp.route("/static/<path:path>")
def send_js(path):
    return send_from_directory(dir_path, os.path.join("static", path))


@frontend_bp.route("/", methods=["GET"])
def capacity():
    countries = NodeRegistration.all_countries()
    farmers = FarmerRegistration.list().order_by("name")

    nodes = []
    form = {"mru": 0, "cru": 0, "sru": 0, "hru": 0, "country": ""}

    if len(request.args) != 0:
        for unit in ["mru", "cru", "sru", "hru"]:
            u = request.args.get(unit) or None
            if u:
                form[unit] = int(u)

        form["country"] = request.args.get("country") or ""
        form["farmer"] = request.args.get("farmer") or ""

        form["page"] = int(request.args.get("page") or 1)
        form["per_page"] = int(request.args.get("pre_page") or 20)

        nodes = NodeRegistration.search(**form, order="-updated")

    return render_template("capacity.html", nodes=nodes, form=form, countries=countries, farmers=farmers)


@frontend_bp.route("/farmers", methods=["GET"])
def list_farmers():
    farmers = FarmerRegistration.list(order="name")
    return render_template("farmers.html", farmers=farmers)


@frontend_bp.route("/farm_registered", methods=["GET"])
def farmer_registered():
    jwt = session["iyo_jwt"]
    return render_template("farm_registered.html", jwt=jwt)


@frontend_bp.route("/farm_updated", methods=["GET"])
def farmer_updated():
    jwt = session["iyo_jwt"]
    return render_template("farm_updated.html", jwt=jwt)


@frontend_bp.route("/api", methods=["GET"])
def api_index():
    return render_template("api.html")


@frontend_bp.route("/register_farm", methods=["GET"])
def register_farmer():
    return render_template("register_farm.html")


@frontend_bp.route("/edit_farm/<organization>", methods=["GET"])
def edit_farmer(organization):
    @requires_auth(org_from_request=organization)
    def handler():
        jwt_string = session["iyo_jwt"]
        jwt_info = jwt.decode(jwt_string, ITSYOUONLINE_KEY)
        scopes = jwt_info["scope"]
        for scope in scopes:
            if organization in scope:
                break
        else:
            # invalidate iyo_authenticated to retry login with the new scope.
            force_invalidate_session()

            return redirect("/edit_farm/{}".format(organization))
        try:
            farmer = FarmerRegistration.get(organization)
        except FarmerNotFoundError as e:
            abort(404)
        else:
            return render_template("edit_farm.html", farmer=farmer)

    return handler()
