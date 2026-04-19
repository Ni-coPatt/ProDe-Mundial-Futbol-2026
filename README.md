# Prode Mundial 2026 — API Backend

API REST para gestionar el fixture y el sistema de pronósticos (ProDe) del Mundial de Fútbol 2026.

Desarrollada con **Python + Flask + MySQL**, para la materia Introducción al Desarrollo de Software (TB022) — FIUBA.

---

## Estructura del proyecto

```
ProDe-Mundial-Futbol-2026/
├── data/
│   └── db.py    # Predicciones
├── database/
│   ├── base_datos.sql        # Lista de partidos
│   └── queries.py    # Predicciones
├── routes/
│   ├── partidos.py        # Lista de partidos
│   ├── ranking.py        # Lista de partidos
│   └── usuarios.py    # Predicciones
├── utils/
│   ├── helpers.py        # Lista de partidos
│   └── validations.py    # Predicciones
├── .gitignore               # Programa principal
├── app.py        # Lista de partidos
├── README.md        # Lista de partidos
├── requirements.txt       # Lista de partidos
└── swagger.yaml    # Predicciones
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
python run.py
# Servidor corriendo en http://localhost:5000
```
