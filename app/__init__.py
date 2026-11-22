"""Aplicación web del sistema de pedidos y reservas del restaurante."""
from flask import Flask, jsonify, render_template, request

from app.servicios import MENU, ErrorRestaurante, Restaurante


def create_app():
    app = Flask(__name__)
    restaurante = Restaurante()

    @app.errorhandler(ErrorRestaurante)
    def error_negocio(error):
        return jsonify({"error": error.mensaje}), error.codigo_http

    # ---------- Páginas ----------
    @app.get("/")
    def inicio():
        return render_template("inicio.html", menu=MENU)

    @app.route("/reservar", methods=["GET", "POST"])
    def reservar():
        if request.method == "GET":
            return render_template("reservar.html")
        try:
            reserva = restaurante.crear_reserva(
                request.form.get("nombre"),
                request.form.get("correo"),
                request.form.get("fecha"),
                request.form.get("hora"),
                int(request.form.get("personas", 0)),
            )
        except (ErrorRestaurante, ValueError) as error:
            mensaje = getattr(error, "mensaje", "Datos no válidos")
            return render_template("reservar.html", error=mensaje), 400
        return render_template("confirmacion.html", reserva=reserva), 201

    @app.get("/reservas")
    def lista_reservas():
        return render_template("reservas.html", reservas=restaurante.reservas)

    # ---------- API ----------
    @app.get("/salud")
    def salud():
        return jsonify({"estado": "ok"})

    @app.get("/api/menu")
    def api_menu():
        return jsonify(MENU)

    @app.get("/api/mesas/disponibles")
    def api_mesas():
        personas = request.args.get("personas", type=int, default=1)
        mesas = restaurante.mesas_disponibles(
            request.args.get("fecha"), request.args.get("hora"), personas
        )
        return jsonify({"mesas": mesas})

    @app.post("/api/reservas")
    def api_reservar():
        datos = request.get_json(silent=True) or {}
        reserva = restaurante.crear_reserva(
            datos.get("nombre"),
            datos.get("correo"),
            datos.get("fecha"),
            datos.get("hora"),
            datos.get("personas"),
        )
        return jsonify(reserva), 201

    @app.post("/api/pedidos")
    def api_pedir():
        datos = request.get_json(silent=True) or {}
        pedido = restaurante.crear_pedido(datos.get("mesa"), datos.get("items", []))
        return jsonify(pedido), 201

    @app.get("/api/reportes/ventas")
    def api_reporte():
        return jsonify(restaurante.reporte_ventas())

    return app
