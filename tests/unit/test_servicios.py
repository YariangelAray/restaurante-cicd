from datetime import date, timedelta

import pytest

from app.servicios import ErrorRestaurante, calcular_total


def test_calcular_total_suma_precios_por_cantidad():
    items = [{"plato_id": 1, "cantidad": 2}, {"plato_id": 4, "cantidad": 1}]
    assert calcular_total(items) == 32000 * 2 + 9000


def test_calcular_total_rechaza_plato_inexistente():
    with pytest.raises(ErrorRestaurante):
        calcular_total([{"plato_id": 99, "cantidad": 1}])


def test_calcular_total_rechaza_cantidad_cero():
    with pytest.raises(ErrorRestaurante):
        calcular_total([{"plato_id": 1, "cantidad": 0}])


def test_calcular_total_rechaza_pedido_vacio():
    with pytest.raises(ErrorRestaurante):
        calcular_total([])


def test_mesa_de_dos_sirve_para_dos_personas(restaurante, manana):
    assert 1 in restaurante.mesas_disponibles(manana, "19:00", 2)


def test_mesas_disponibles_se_ordenan_de_menor_a_mayor_capacidad(restaurante, manana):
    assert restaurante.mesas_disponibles(manana, "19:00", 5) == [5, 6]


def test_reserva_asigna_la_mesa_mas_pequena(restaurante, manana):
    reserva = restaurante.crear_reserva("Ana", "ana@correo.com", manana, "19:00", 3)
    assert reserva["mesa"] == 3
    assert reserva["codigo"] == "R-0001"


def test_mesa_reservada_deja_de_estar_disponible(restaurante, manana):
    restaurante.crear_reserva("Ana", "ana@correo.com", manana, "19:00", 8)
    assert 6 not in restaurante.mesas_disponibles(manana, "19:00", 1)


def test_sin_mesas_libres_devuelve_conflicto(restaurante, manana):
    restaurante.crear_reserva("Ana", "ana@correo.com", manana, "20:00", 8)
    with pytest.raises(ErrorRestaurante) as error:
        restaurante.crear_reserva("Luis", "luis@correo.com", manana, "20:00", 7)
    assert error.value.codigo_http == 409


@pytest.mark.parametrize(
    "nombre, correo, hora, personas",
    [
        ("", "a@b.com", "19:00", 2),
        ("Ana", "sin-arroba", "19:00", 2),
        ("Ana", "a@b.com", "19:00", 0),
        ("Ana", "a@b.com", "19:00", 9),
        ("Ana", "a@b.com", "08:00", 2),
        ("Ana", "a@b.com", "hora", 2),
    ],
)
def test_reserva_con_datos_invalidos(restaurante, manana, nombre, correo, hora, personas):
    with pytest.raises(ErrorRestaurante):
        restaurante.crear_reserva(nombre, correo, manana, hora, personas)


def test_no_se_reserva_en_fecha_pasada(restaurante):
    ayer = (date.today() - timedelta(days=1)).isoformat()
    with pytest.raises(ErrorRestaurante):
        restaurante.crear_reserva("Ana", "a@b.com", ayer, "19:00", 2)


def test_pedido_en_mesa_inexistente(restaurante):
    with pytest.raises(ErrorRestaurante):
        restaurante.crear_pedido(20, [{"plato_id": 1, "cantidad": 1}])


def test_reporte_de_ventas_suma_los_pedidos(restaurante):
    restaurante.crear_pedido(1, [{"plato_id": 1, "cantidad": 1}])
    restaurante.crear_pedido(2, [{"plato_id": 5, "cantidad": 2}])
    assert restaurante.reporte_ventas() == {"pedidos": 2, "total": 32000 + 16000}
