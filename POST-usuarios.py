from Flask import request, jsonify
from Flask import Blueprint
from data.db import get_connection

usuarios_bp= Blueprint('usuarios', __name__)

@usuarios_bp.route("/usuarios", methods=['POST'])
def crear_usuario():
    datos= request.get_json()

    conexion= get_connection()
    cursor= conexion.cursor(dictionary=True)
    try:
        if not datos:
            return jsonify({"error" : "Body vacio"}), 400
        
        if 'nombre' not in datos or 'email' not in datos:
            return jsonify({"error" : "Fantan campos obligatorios"}), 400
        
        nombre= datos.get('nombre')
        email= datos.get('email')
        
        if not nombre or not email:
            return jsonify({"error" : "Campos obligatorios vacios"}), 400
        
        cursor.execute("SELECT * FROM usuarios WHERE nombre = %s or email= %s", (nombre, email))
        usuario_existiente= cursor.fetchone()

        if usuario_existiente:
            return jsonify({"error": "email o nombre ya ingresado"}), 409
        
        cursor.execute("INSERT INTO usuarios (nombre, email) VALUES (%s, %s) ", (nombre, email))

        conexion.commit()

        return jsonify({"mensaje" : "Usuario creado con exito"}), 201
    
    except Exception as e:
        return jsonify({"error" : "Error interno del servidor"}), 500
    
    finally: 
        cursor.close()
        conexion.close()
        



