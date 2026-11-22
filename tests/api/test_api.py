def test_salud(cliente):
    respuesta = cliente.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {"estado": "ok"}


def test_menu(cliente):
    menu = cliente.get("/api/menu").get_json()
    assert len(menu) == 5


def test_crear_reserva(cliente, manana):
    datos = {"nombre": "Ana", "correo": "ana@correo.com", "fecha": manana,
             "hora": "19:00", "personas": 2}
    respuesta = cliente.post("/api/reservas", json=datos)
    assert respuesta.status_code == 201
    assert respuesta.get_json()["codigo"] == "R-0001"


def test_reserva_invalida_devuelve_400(cliente, manana):
    datos = {"nombre": "", "correo": "ana@correo.com", "fecha": manana,
             "hora": "19:00", "personas": 2}
    assert cliente.post("/api/reservas", json=datos).status_code == 400


def test_mesa_ocupada_devuelve_409(cliente, manana):
    datos = {"nombre": "Ana", "correo": "a@b.com", "fecha": manana, "hora": "21:00", "personas": 8}
    cliente.post("/api/reservas", json=datos)
    datos["personas"] = 7
    assert cliente.post("/api/reservas", json=datos).status_code == 409


def test_mesas_disponibles(cliente, manana):
    respuesta = cliente.get(f"/api/mesas/disponibles?fecha={manana}&hora=19:00&personas=6")
    assert respuesta.get_json() == {"mesas": [5, 6]}


def test_pedido_y_reporte(cliente):
    pedido = {"mesa": 3, "items": [{"plato_id": 2, "cantidad": 2}]}
    respuesta = cliente.post("/api/pedidos", json=pedido)
    assert respuesta.status_code == 201
    assert respuesta.get_json()["total"] == 56000
    assert cliente.get("/api/reportes/ventas").get_json() == {"pedidos": 1, "total": 56000}


def test_pagina_de_inicio_muestra_el_menu(cliente):
    assert "Bandeja paisa" in cliente.get("/").get_data(as_text=True)


def test_formulario_de_reserva(cliente, manana):
    assert cliente.get("/reservar").status_code == 200
    datos = {"nombre": "Ana", "correo": "a@b.com", "fecha": manana,
             "hora": "19:00", "personas": "2"}
    respuesta = cliente.post("/reservar", data=datos)
    assert respuesta.status_code == 201
    assert "R-0001" in respuesta.get_data(as_text=True)
    assert "Ana" in cliente.get("/reservas").get_data(as_text=True)


def test_formulario_con_error(cliente, manana):
    datos = {"nombre": "Ana", "correo": "a@b.com", "fecha": manana,
             "hora": "19:00", "personas": "x"}
    respuesta = cliente.post("/reservar", data=datos)
    assert respuesta.status_code == 400
