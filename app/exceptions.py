from http import HTTPStatus


class BaseHttpException(Exception):
    code = HTTPStatus.BAD_GATEWAY
    error_code = HTTPStatus.BAD_GATEWAY
    message = HTTPStatus.BAD_GATEWAY.description


class UserAlreadyExistsError(BaseHttpException):
    pass


class UserNotFoundError(BaseHttpException):
    code = HTTPStatus.NOT_FOUND
    error_code = HTTPStatus.NOT_FOUND
    message = HTTPStatus.NOT_FOUND.description


class InvalidCredentialsError(BaseHttpException):
    code = HTTPStatus.BAD_REQUEST
    error_code = HTTPStatus.BAD_REQUEST
    message = HTTPStatus.BAD_REQUEST.description


class InvalidTokenError(InvalidCredentialsError):
    pass
