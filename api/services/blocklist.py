import api.extensions as ext

def add_jti_to_blocklist(jti: str, exp: int):
    ext.redis_client.setex(f"blocklist:{jti}", exp, "true")

def is_jti_blocked(jti: str) -> bool:
    return ext.redis_client.exists(f"blocklist:{jti}") == 1