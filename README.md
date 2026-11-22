# Restaurante El Fogón – Pipeline CI/CD

Sistema de pedidos y reservas de un restaurante (Flask) con un pipeline de integración y entrega continua en Jenkins.

## Módulos
- **Menú**: platos y precios (`/`, `/api/menu`).
- **Reservas**: disponibilidad de mesas y reservas con confirmación (`/reservar`, `/api/mesas/disponibles`, `/api/reservas`).
- **Pedidos**: registro de pedidos y cálculo del total (`/api/pedidos`).
- **Reportes**: ventas del día (`/api/reportes/ventas`).
- **Salud**: estado del servicio (`/salud`).

## Etapas del pipeline (`Jenkinsfile`)
1. Checkout
2. Preparar entorno
3. Calidad de código (flake8)
4. Seguridad: Bandit y pip-audit (en paralelo)
5. Pruebas unitarias y de API (pytest + cobertura)
6. Análisis SonarQube
7. Construir imagen Docker
8. Desplegar en staging
9. Pruebas en staging: interfaz con Selenium y carga con Locust (en paralelo)
10. Aprobación manual
11. Desplegar en producción (puerto 8089 por defecto)

## Infraestructura local
`infra/docker-compose.yml` levanta Jenkins (8080), SonarQube (9000) y Selenium (4444, noVNC en 7900).

## Ejecutar las pruebas en local
```bash
python -m venv .venv
.venv/Scripts/activate      # en Windows (Git Bash: source .venv/Scripts/activate)
pip install -r requirements-dev.txt
pytest
```
