from mysql.connector import Error


def crear_partido_db(conn, equipo_local, equipo_visitante, fecha, fase):
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO partidos (equipo_local, equipo_visitante,fecha,fase)
            VALUES(%s,%s,%s,%s)
        """
        cur.execute(query, (equipo_local, equipo_visitante, fecha, fase))
        conn.commit()
        return cur.lastrowid
    finally:
        if cur:
            cur.close()


def buscar_partido_por_id(id, conn):
    try:
        cur = conn.cursor(dictionary=True)

        query = "SELECT * FROM partidos WHERE id = %s"
        cur.execute(query, (id,))
        return cur.fetchone()

    finally:
        if cur:
            cur.close()


def reemplazar_partido_db(conn, id, equipo_local, equipo_visitante, fecha, fase):
    try:
        cur = conn.cursor()

        query = """
            UPDATE partidos
            SET equipo_local = %s,
                equipo_visitante = %s,
                fecha = %s,
                fase = %s
            WHERE id = %s
        """

        cur.execute(query, (equipo_local, equipo_visitante, fecha, fase, id))
        conn.commit()

        return cur.rowcount > 0

    finally:
        if cur:
            cur.close()


def actualizar_partido(id, cambios, conn):
    try:
        cur = conn.cursor()

        campos = ", ".join([f"{k} = %s" for k in cambios.keys()])
        valores = list(cambios.values())
        valores.append(id)

        query = f"""
            UPDATE partidos
            SET {campos}
            WHERE id = %s
        """

        cur.execute(query, valores)
        conn.commit()

        return cur.rowcount > 0

    finally:
        if cur:
            cur.close()


def eliminar_partido(id, conn):
    try:
        cur = conn.cursor()

        query = "DELETE FROM partidos WHERE id = %s"
        cur.execute(query, (id,))
        conn.commit()

        return cur.rowcount > 0

    finally:
        if cur:
            cur.close()


def listar_partidos_db(conn, limit, offset):
    try:
        cur = conn.cursor(dictionary=True)

        query = """
            SELECT * FROM partidos
            LIMIT %s OFFSET %s
        """

        cur.execute(query, (limit, offset))
        return cur.fetchall()

    finally:
        if cur:
            cur.close()


def contar_partidos_db(conn):
    try:
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT COUNT(*) as total FROM partidos")
        return cur.fetchone()["total"]

    finally:
        if cur:
            cur.close()
