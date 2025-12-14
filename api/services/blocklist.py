from api.infra.redis import get_redis

def add_jti_to_blocklist(jti: str, exp: int) -> None:
    """Add a JWT identifier (JTI) to the Redis blocklist."""
    get_redis().setex(f"blocklist:{jti}", exp, "true")

def is_jti_blocked(jti: str) -> bool:
    """Check if a JWT identifier (JTI) is present in the Redis blocklist."""
    return get_redis().exists(f"blocklist:{jti}") == 1