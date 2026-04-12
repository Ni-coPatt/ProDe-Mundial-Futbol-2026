from Flask import request, jsonify
from Flask import Blueprint
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
        resultado= cursor.fetcheone()
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
