# Prode Mundial 2026 — API Backend

API REST para gestionar el fixture y el sistema de pronósticos (ProDe) del Mundial de Fútbol 2026.

Desarrollada con **Python + Flask + MySQL**, para la materia Introducción al Desarrollo de Software (TB022) — FIUBA.

---

## Estructura del proyecto

```
prode-mundial/
├── run.py                  # Punto de entrada
├── requirements.txt
├── .env.example            # Variables de entorno (renombrar a .env)
│
├── config/
│   └── settings.py         # Configuración de la app (DB, secret key)
│
├── app/
│   ├── __init__.py         # create_app(): fábrica de la aplicación Flask
│   ├── extensions.py       # Instancia compartida de SQLAlchemy
│   │
│   ├── models/             # Modelos ORM (tablas de la base de datos)
│   │   ├── partido.py      # Tabla partidos
│   │   ├── resultado.py    # Tabla resultados (relación 1-a-1 con partido)
│   │   ├── usuario.py      # Tabla usuarios
│   │   └── prediccion.py   # Tabla predicciones (usuario + partido + marcador)
│   │
│   ├── routes/             # Blueprints: reciben requests y devuelven responses
│   │   ├── partidos.py     # GET/POST/PUT/PATCH/DELETE /partidos
│   │   ├── resultados.py   # PUT /partidos/<id>/resultado
│   │   ├── usuarios.py     # CRUD /usuarios
│   │   ├── predicciones.py # POST /partidos/<id>/prediccion
│   │   └── ranking.py      # GET /ranking
│   │
│   ├── services/           # Lógica de negocio y validaciones
│   │   ├── partido_service.py
│   │   ├── resultado_service.py
│   │   ├── usuario_service.py
│   │   ├── prediccion_service.py
│   │   └── ranking_service.py
│   │
│   └── utils/
│       └── pagination.py   # Helper HATEOAS: _limit, _offset, _first, _prev, _next, _last
│
├── migrations/
│   └── crear_tablas.sql    # Script SQL para crear la DB manualmente
│
└── tests/
    └── test_partidos.py    # Tests con pytest (usan SQLite en memoria)
```

---

## Cómo correr el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/prode-mundial.git
cd prode-mundial
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales de MySQL
```

### 4. Crear la base de datos

**Opción A** — con el script SQL:
```bash
mysql -u root -p < migrations/crear_tablas.sql
```

**Opción B** — automático al levantar la app:
```bash
python run.py   # db.create_all() crea las tablas si no existen
```

### 5. Levantar el servidor

```bash
python run.py
# Servidor corriendo en http://localhost:5000
```
