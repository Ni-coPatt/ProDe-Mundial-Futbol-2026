from flask import Flask, jsonify, Blueprint
from data.db import get_connection

usuarios_bp = Blueprint('usuarios', __name__) 

@usuarios_bp.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuarios_id(id):

    if id <= 0:
        return jsonify({'error': 'El ID debe ser un número positivo'}), 400
    
    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        #Traigo todos los datos (id, nombre, email) del usuario con ese id.
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,)) 
        usuario = cursor.fetchone()

        if usuario:
            return jsonify(usuario), 200
        return jsonify({'error': 'Usuario no encontrado'}), 404
    

    except Exception as e:
        print(e)
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
