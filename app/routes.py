# filepath: app/routes.py
from flask import Blueprint, render_template, request
from app.models import processar_dados

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def index():
    return render_template("form.html")

@main.route("/resultado", methods=["POST"])
def resultado():
    latitude = float(request.form.get("latitude"))
    longitude = float(request.form.get("longitude"))
    cultura = request.form.get("cultura")
    estagio = request.form.get("estagio")


    resultados = processar_dados(latitude, longitude, cultura, estagio)
    return render_template("resultado.html", **resultados)