from datetime import datetime

from . import db


class ModeloBase(db.Model):
    """Classe base abstrata: todo model herda id + data_criacao daqui."""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
