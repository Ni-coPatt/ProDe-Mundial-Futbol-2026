# Prode Mundial 2026 — API Backend

API REST para gestionar el fixture y el sistema de pronósticos (ProDe) del Mundial de Fútbol 2026.

Desarrollada con **Python + Flask + MySQL**, para la materia Introducción al Desarrollo de Software (TB022) — FIUBA.

---

## Estructura del proyecto

```
ProDe-Mundial-Futbol-2026/
├── data/
│   └── db.py    # Conexión con la base de datos
├── database/
│   ├── base_datos.sql        # Script para crear la base de datos y las tablas
│   └── queries.py    # Consultas SQL
├── routes/
│   ├── partidos.py        # Endpoints de partidos
│   ├── ranking.py        # Endpoint de ranking
│   └── usuarios.py    # Endpoints de usuarios
├── utils/
│   ├── helpers.py        # Funciones de utilidad general
│   └── validations.py    # Validacion de entrada de datos
├── .gitignore               # Archivos excluidos
├── app.py        # Archivo principal
├── README.md        # Documentación general del proyecto
├── requirements.txt       # Dependencias de la API
└── swagger.yaml    
```

---

## Cómo correr el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/Ni-coPatt/ProDe-Mundial-Futbol-2026
cd ProDe-Mundial-Futbol-2026
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

con el script SQL:
```bash
mysql -u root -p < database/base_datos.sql
```



### 5. Levantar el servidor

```bash
python3 app.py
# Servidor corriendo en http://localhost:5000
```
