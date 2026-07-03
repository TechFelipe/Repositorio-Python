from flask import Blueprint, render_tamplate
from models import locacao, veiculo

loc_bp = Blueprint ("dashboard", __name__)

@loc_bp.route("/")
def index():
    "index.html"
    return render_template("index.html", total_veiculos = veiculos.query.count())