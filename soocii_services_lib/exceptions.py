class BaseValidationError(Exception):
    pass


class TokenSchemaError(BaseValidationError):
    pass


class TokenExpiredError(BaseValidationError):
    pass


class AccessTokenValidationError(BaseValidationError):
    pass


class RefreshTokenValidationError(BaseValidationError):
    pass
