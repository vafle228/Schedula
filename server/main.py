from bottle import Bottle, response, HTTPResponse, request


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
}


def handle_options():
    if request.method == "OPTIONS":
        raise HTTPResponse(headers=CORS_HEADERS)


def enable_cors():
    for key, value in CORS_HEADERS.items():
        response.set_header(key, value)


def build_api() -> Bottle:
    app = Bottle()
    app.add_hook("after_request", enable_cors)
    app.add_hook("before_request", handle_options)

    return app


if __name__ == "__main__":
    api = build_api()
    api.run(host="127.0.0.1", port="8000", debug=True)
