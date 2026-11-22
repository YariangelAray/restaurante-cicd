"""Prueba de carga: varios usuarios consultando el menú y la disponibilidad."""
from datetime import date, timedelta

from locust import HttpUser, between, task

MANANA = (date.today() + timedelta(days=1)).isoformat()


class Comensal(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(3)
    def ver_menu(self):
        self.client.get("/api/menu")

    @task(2)
    def consultar_mesas(self):
        self.client.get(f"/api/mesas/disponibles?fecha={MANANA}&hora=19:00&personas=2",
                        name="/api/mesas/disponibles")

    @task(1)
    def revisar_salud(self):
        self.client.get("/salud")
