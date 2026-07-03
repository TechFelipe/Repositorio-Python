from datetime import date

from models import ClienteLocadora, Locacao, Veiculo, db


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

    locacao = Locacao(
        cliente_id=clientes[0].id,
        veiculo_id=veiculos[0].id,
        data_inicio=date(2026, 7, 1),
        data_fim=date(2026, 7, 5),
        valor_total=480.0,
    )
    db.session.add(locacao)
    db.session.commit()
