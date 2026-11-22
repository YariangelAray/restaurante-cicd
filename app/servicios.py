"""Lógica del sistema de pedidos y reservas del restaurante."""
from datetime import date, datetime

# Número de mesa -> capacidad de personas
MESAS = {1: 2, 2: 2, 3: 4, 4: 4, 5: 6, 6: 8}

MENU = [
    {"id": 1, "nombre": "Bandeja paisa", "precio": 32000},
    {"id": 2, "nombre": "Ajiaco santafereño", "precio": 28000},
    {"id": 3, "nombre": "Mojarra frita", "precio": 35000},
    {"id": 4, "nombre": "Limonada de coco", "precio": 9000},
    {"id": 5, "nombre": "Postre de natas", "precio": 8000},
]

HORA_APERTURA = "12:00"
HORA_CIERRE = "22:00"
MAX_PERSONAS = 8


class ErrorRestaurante(Exception):
    """Error de negocio con el código HTTP que debe devolver el API."""

    def __init__(self, mensaje, codigo_http=400):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_http = codigo_http


def calcular_total(items):
    """Suma el valor de los platos de un pedido."""
    if not items:
        raise ErrorRestaurante("El pedido no tiene platos")
    precios = {plato["id"]: plato["precio"] for plato in MENU}
    total = 0
    for item in items:
        plato_id = item.get("plato_id")
        cantidad = item.get("cantidad", 0)
        if plato_id not in precios:
            raise ErrorRestaurante(f"El plato {plato_id} no existe")
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ErrorRestaurante("La cantidad debe ser un número mayor que cero")
        total += precios[plato_id] * cantidad
    return total


class Restaurante:
    """Guarda en memoria las reservas y los pedidos del día."""

    def __init__(self):
        self.reservas = []
        self.pedidos = []

    def mesas_disponibles(self, fecha, hora, personas):
        ocupadas = {
            r["mesa"] for r in self.reservas if r["fecha"] == fecha and r["hora"] == hora
        }
        return [
            mesa
            for mesa, capacidad in sorted(MESAS.items(), key=lambda m: m[1])
            if capacidad >= personas and mesa not in ocupadas
        ]

    def crear_reserva(self, nombre, correo, fecha, hora, personas):
        nombre = (nombre or "").strip()
        if not nombre:
            raise ErrorRestaurante("El nombre es obligatorio")
        if "@" not in (correo or ""):
            raise ErrorRestaurante("El correo no es válido")
        if not isinstance(personas, int) or not 1 <= personas <= MAX_PERSONAS:
            raise ErrorRestaurante(f"El número de personas debe estar entre 1 y {MAX_PERSONAS}")
        try:
            dia = datetime.strptime(fecha, "%Y-%m-%d").date()
            datetime.strptime(hora, "%H:%M")
        except (TypeError, ValueError):
            raise ErrorRestaurante("La fecha o la hora no tienen un formato válido")
        if dia < date.today():
            raise ErrorRestaurante("No se puede reservar en una fecha pasada")
        if not HORA_APERTURA <= hora <= HORA_CIERRE:
            raise ErrorRestaurante(f"El horario de reservas es de {HORA_APERTURA} a {HORA_CIERRE}")

        disponibles = self.mesas_disponibles(fecha, hora, personas)
        if not disponibles:
            raise ErrorRestaurante("No hay mesas disponibles para esa fecha y hora", 409)

        reserva = {
            "codigo": f"R-{len(self.reservas) + 1:04d}",
            "nombre": nombre,
            "correo": correo,
            "fecha": fecha,
            "hora": hora,
            "personas": personas,
            "mesa": disponibles[0],
        }
        self.reservas.append(reserva)
        return reserva

    def crear_pedido(self, mesa, items):
        if mesa not in MESAS:
            raise ErrorRestaurante(f"La mesa {mesa} no existe")
        pedido = {
            "codigo": f"P-{len(self.pedidos) + 1:04d}",
            "mesa": mesa,
            "items": items,
            "total": calcular_total(items),
            "estado": "recibido",
        }
        self.pedidos.append(pedido)
        return pedido

    def reporte_ventas(self):
        return {
            "pedidos": len(self.pedidos),
            "total": sum(p["total"] for p in self.pedidos),
        }
