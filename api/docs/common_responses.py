RESOURCE_ERRORS = [
    (401, "Unauthorized access."),
    (404, "Resource not found."),
    (500, "Internal server error."),
]

CREATION_ERRORS = [
    (401, "Unauthorized access."),
    (409, "Resource already exists."),
    (500, "Internal server error."),
]

LISTING_ERRORS = [
    (401, "Unauthorized access."),
    (500, "Internal server error."),
]

def apply_common_responses(blp, responses):
    def decorator(fn):
        for code, desc in responses:
            fn = blp.alt_response(code, description=desc)(fn)
        return fn
    return decorator