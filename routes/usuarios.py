from flask import Flask
from flask import request, jsonify
from flask import Blueprint
from data.db import get_connection

usuarios_bp= Blueprint('usuarios', __name__)

@usuarios_bp.route("/usuarios", methods=['GET'])
def listar_usuarios():
    conexion= get_connection()
    cursor= conexion.cursor(dictionary=True)
    
    try:
        limite= request.args.get('_limit', default= '10')
        offset_prev= request.args.get('_offset', default= '0')

        if not limite.isdigit() or not offset_prev.isdigit():
            return jsonify({"error" : "Parametros 'limit' o 'offset' invalidos"}), 400
        
        
        limit= int(limite)
        offset= int(offset_prev)
        
        if limit <= 0 or offset < 0:
            return jsonify({"error" : "Parametros 'limit' o 'offset' fuera de rango"}), 400
        
        cursor.execute("SELECT id, nombre FROM usuarios LIMIT %s OFFSET %s", (limit, offset))
        usuarios= cursor.fetchall()
        
        if not usuarios:
            return jsonify({"usuarios": []}), 204
        
         #calculamos el ultimo offset posible.
         cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
         resultado = cursor.fetchone()
        total_usuarios= resultado['total']
        ultimo_offset= ((total_usuarios - 1) // limit) * limit
    
        lista= {
            "usuarios" : usuarios,
            "_links" : {
            "_first" : {"href":f"/usuarios?_offset=0&_limit={limit}"},
            "_prev" : {"href": f"/usuarios?_offset={max(0, offset - limit)}&_limit={limit}"},
            "_next" : {"href":f"/usuarios?_offset={offset + limit}&_limit={limit}"},
            "_last" : {"href":f"/usuarios?_offset={ultimo_offset}&_limit={limit}"},
        }
        }

        return jsonify(lista), 200
    
    except Exception as e:
        return jsonify({"error" : "Error interno del servidor"}), 500
    
    finally: 
        cursor.close()
        conexion.close()

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

@usuarios_bp.route("/usuarios", methods=['POST'])
def crear_usuario():
    datos= request.get_json()

    conexion= get_connection()
    cursor= conexion.cursor(dictionary=True)
    try:
        if not datos:
            return jsonify({"error" : "Body vacio"}), 400
        
        if 'nombre' not in datos or 'email' not in datos:
            return jsonify({"error" : "Faltan campos obligatorios"}), 400
        
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

@usuarios_bp.route('/usuarios/<int:id>', methods=['PUT'])
def reemplazar_usuario(id):
    datos = request.get_json()

    if not datos:
        return jsonify({"error" : "Body vacio"}), 400
    
    if 'nombre' not in datos or 'email' not in datos:
        return jsonify({"error" : "Faltan campos obligatorios"}), 400
    
    nombre = datos.get('nombre')
    email = datos.get('email')

    conexion = None
    cursor = None

    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        query_update = "UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s"
        cursor.execute(query_update, (nombre, email, id))
        
        if cursor.rowcount == 0:
            query_insert = "INSERT INTO usuarios (nombre, email, puntos) VALUES (%s, %s, 0)"
            cursor.execute(query_insert, (nombre, email))
            
        conexion.commit()

        return "", 204

    except Exception as e:
        if conexion:
            conexion.rollback()
        print(e)
        return jsonify({"error" : "Error interno del servidor"}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

