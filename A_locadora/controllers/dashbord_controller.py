from flask import Blueprint, render_template

from models import ClienteLocadora, Locacao, Veiculo

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template(
        "locadora/Index.html",
        total_clientes=ClienteLocadora.query.count(),
        total_veiculos=Veiculo.query.count(),
        total_locacoes=Locacao.query.count(),
    )
