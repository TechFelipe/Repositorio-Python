# O ponto em "from ." = import da MESMA pasta models (vizinho de quarto)
from . import db
from .base import ModeloBase


class ClienteLocadora(ModeloBase):
    __tablename__ = "clientes_locadora"

    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    cnh = db.Column(db.String(20), nullable=False)

    locacoes = db.relationship("Locacao", back_populates="cliente")

    @classmethod
    def listar(cls):
        return cls.query.order_by(cls.nome).all()
