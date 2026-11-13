"""
Hash de contrasenias con la libreria estandar (hashlib), sin dependencias externas.
Formato almacenado:  pbkdf2_sha256$iteraciones$sal_hex$hash_hex
"""
import hashlib
import hmac
import os

ITERACIONES = 200_000


def generar_hash(clave, sal=None, iteraciones=ITERACIONES):
    sal = sal or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, iteraciones)
    return f"pbkdf2_sha256${iteraciones}${sal.hex()}${digest.hex()}"


def verificar(clave, almacenado):
    """True si la clave coincide con el hash almacenado."""
    try:
        algoritmo, iteraciones, sal, esperado = almacenado.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"),
                                     bytes.fromhex(sal), int(iteraciones))
        return hmac.compare_digest(digest.hex(), esperado)
    except (ValueError, AttributeError):
        return False
