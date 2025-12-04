# Внешние зависимости
import base64


# Получить бинарные данные из base64 строки
def get_binary_bytes(binary: str) -> bytes:
    try:
        return base64.b64decode(binary)
    except Exception:
        raise ValueError("Invalid base64 string")