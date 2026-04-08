# Prode Mundial 2026 — API Backend

API REST para gestionar el fixture y el sistema de pronósticos (ProDe) del Mundial de Fútbol 2026.

Desarrollada con **Python + Flask + MySQL**, para la materia Introducción al Desarrollo de Software (TB022) — FIUBA.

---

## Estructura del proyecto

```
prode-mundial/
├── main.py                # Programa principal
├── data/
│   ├── partidos.py        # Lista de partidos
│   ├── usuarios.py        # Lista de usuarios
│   ├── resultados.py      # Resultados
│   └── predicciones.py    # Predicciones
│
├── logic/
│   ├── partidos.py        # Funciones sobre partidos
│   ├── usuarios.py        # Funciones sobre usuarios
│   ├── predicciones.py    # Funciones de predicción
│   └── ranking.py         # Cálculo de ranking
│
└── tests/
    └── test_partidos.py
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
