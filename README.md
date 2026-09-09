# Sistema de Gestión de Auditoría Médica — Med Sis SRL

Sistema web completo desarrollado en Python/Flask para la gestión de Auditoría Médica Crónica y Alto Costo.

## Módulos incluidos

| Módulo | Descripción |
|---|---|
| **Dashboard** | KPIs generales: empadronamientos, aprobaciones, alto costo |
| **Empadronamientos** | Crónicos, Diabetes y Discapacidad — CRUD + auditoría |
| **Alto Costo** | Medicamentos que requieren autorización especializada |
| **Vademécum** | Catálogo de medicamentos por segmento y condición |
| **Afiliados** | Consulta de afiliados con historial clínico |
| **Proveedores** | Droguerías y laboratorios — CRUD |
| **Compras** | Órdenes de compra, seguimiento y reportes |
| **Recetas** | Historial de recetas electrónicas |
| **Estadísticas** | KPIs, distribución por tipo, top auditores |
| **API REST** | Endpoint `/api/stats` con datos en JSON |

## Instalación

```bash
pip install flask
python app.py
```

Luego abrir: http://localhost:5000

## Estructura del proyecto

```
Med Sis/
├── app.py              # Aplicación Flask principal
├── data/
│   └── db.json         # Base de datos JSON (persistente)
├── templates/
│   ├── base.html       # Layout con sidebar y topbar
│   ├── dashboard.html
│   ├── empadronamientos.html
│   ├── emp_form.html
│   ├── emp_detalle.html
│   ├── alto_costo.html
│   ├── ac_form.html
│   ├── vademecum.html
│   ├── vademecum_form.html
│   ├── proveedores.html
│   ├── proveedor_form.html
│   ├── compras.html
│   ├── compra_form.html
│   ├── afiliados.html
│   ├── afiliado_detalle.html
│   ├── estadisticas.html
│   └── recetas.html
└── README.md
```

## Cotización SaaS (según propuesta Med Sis)

- Modelo: 0,0045% per cápita por sistema (Cronicidad + Alto Costo)
- Pago: mensual adelantado, hasta día 15 de cada mes
- Actualización: según Tabla de Honorarios del CMPC
- SLA: P1 ≤2h respuesta / P2 ≤4h / P3 ≤1 jornada hábil
- Soporte: Lunes–Viernes 08:00–16:00

## Contacto
Med Sis SRL · Av. Vélez Sarsfield 84, Piso 1°, Córdoba
info@Med Sis.ar · (351) 509-8585
