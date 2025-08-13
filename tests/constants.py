class Urls:
    HEALTHCHECK = "/healthcheck"

    class Auth:
        LOGIN = "/api/v1/authentication/login"
        PROFILE = "/api/v1/authentication/profile"

    class Common:
        INFO = "/api/v1/common/info"

    class Orders:
        CREATE = "/api/v1/orders"
        GET_ALL = "/api/v1/orders"
        GET_BY_ID = "/api/v1/orders/{order_id}"

    class Users:
        CREATE = "/api/v1/users"
        GET_ALL = "/api/v1/users"
        GET_BY_ID = "/api/v1/users/{user_id}"
