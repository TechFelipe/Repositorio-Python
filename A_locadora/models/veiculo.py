from . import db
from .base import ModeloBase


class Veiculo(ModeloBase):
    __tablename__ = "veiculos"

    placa = db.Column(db.String(10), nullable=False)
    modelo = db.Column(db.String(80), nullable=False)
    # TODO ALUNO: diaria (Float)
    # diaria = db.Column(...)

    # TODO ALUNO: relationship com Locacao

    @classmethod
    def listar(cls):
        return cls.query.order_by(cls.modelo).all()
