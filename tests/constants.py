class Urls:
    HEALTHCHECK = "/healthcheck"

    class Auth:
        LOGIN = "/api/v1/authentication/login"

    class Common:
        INFO = "/api/v1/common/info"

    class Users:
        CREATE = "/api/v1/users"
        GET_ALL = "/api/v1/users"
        GET_BY_ID = "/api/v1/users/user/{user_id}"
        PROFILE = "/api/v1/users/profile"
