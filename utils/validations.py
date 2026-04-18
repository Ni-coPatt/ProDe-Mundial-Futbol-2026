from datetime import datetime

FASES_VALIDAS = {"grupos", "dieciseisavos", "octavos", "cuartos", "semis", "final"}


def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def validar_fase(fase):
    return isinstance(fase, str) and fase.strip().lower() in FASES_VALIDAS


def validar_campos_obligatorios(data, campos):
    return [
        campo for campo in campos if campo not in data or data.get(campo) is None or str(data.get(campo)).strip() == ""
    ]


def validar_no_nulos(data, campos):
    return [campo for campo in campos if data.get(campo) is None or str(data.get(campo)).strip() == ""]


def validar_paginado(limit, offset):
    try:
        limit = int(limit)
        offset = int(offset)

        if limit <= 0 or offset < 0:
            return None

        return limit, offset

    except (ValueError, TypeError):
        return None


def validar_equipo(nombre):
    return isinstance(nombre, str) and len(nombre.strip()) > 0


def validar_email(email):
    return isinstance(email, str) and "@" in email and "." in email and len(email.strip()) > 0
