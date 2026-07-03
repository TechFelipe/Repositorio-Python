from models import ClienteLocadora, Veiculo, db


def popular_dados():
    if ClienteLocadora.query.count() > 0:
        return

    clientes = [
        ClienteLocadora(nome="Ana Silva", cpf="111.222.333-44", cnh="12345678900"),
        ClienteLocadora(nome="Bruno Costa", cpf="555.666.777-88", cnh="98765432100"),
    ]
    veiculos = [
        Veiculo(placa="ABC-1D23", modelo="Fiat Argo", diaria=120.0),
        Veiculo(placa="XYZ-9K87", modelo="Hyundai HB20", diaria=135.0),
    ]
    db.session.add_all(clientes + veiculos)
    db.session.commit()