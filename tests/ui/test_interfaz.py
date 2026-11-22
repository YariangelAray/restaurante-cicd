"""Pruebas de interfaz con Selenium sobre el entorno de staging."""
import os
from datetime import date, timedelta

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

SELENIUM_URL = os.getenv("SELENIUM_URL")
APP_URL = os.getenv("APP_URL", "http://localhost:5000")

pytestmark = pytest.mark.skipif(not SELENIUM_URL, reason="Selenium no configurado")


@pytest.fixture
def navegador():
    opciones = webdriver.ChromeOptions()
    opciones.add_argument("--headless=new")
    driver = webdriver.Remote(command_executor=SELENIUM_URL, options=opciones)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def llenar(driver, campo, valor):
    elemento = driver.find_element(By.ID, campo)
    driver.execute_script("arguments[0].value = arguments[1];", elemento, valor)


def test_el_menu_carga(navegador):
    navegador.get(APP_URL + "/")
    assert "Menú del día" in navegador.page_source


def test_reservar_una_mesa_desde_el_formulario(navegador):
    manana = (date.today() + timedelta(days=1)).isoformat()
    navegador.get(APP_URL + "/reservar")
    llenar(navegador, "nombre", "Cliente Selenium")
    llenar(navegador, "correo", "selenium@prueba.com")
    llenar(navegador, "fecha", manana)
    llenar(navegador, "hora", "19:30")
    llenar(navegador, "personas", "4")
    navegador.find_element(By.ID, "enviar").click()
    assert navegador.find_element(By.ID, "confirmacion").text == "¡Reserva confirmada!"
    assert navegador.find_element(By.ID, "codigo").text.startswith("R-")
