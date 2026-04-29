from flask import Flask, request, jsonify
from services.security import validate_input, sanitize
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

app.config["RATELIMIT_HEADERS_ENABLED"] = True

# Rate limiter setup
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30 per minute"]
)
limiter.init_app(app)

# Register routes (we’ll import here)
from routes.test_routes import test_bp
app.register_blueprint(test_bp)

# 429 handler
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Too many requests. Please try again later."
    }), 429

# Global security middleware
@app.before_request
def security_layer():
    if request.method != "POST":
        return

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    found = False

    for key in ["input", "text", "query", "content"]:
        if key in data:
            value = data[key]

            valid, error = validate_input(value)
            if not valid:
                return jsonify({"error": error}), 400

            request.sanitized_input = sanitize(value)
            request.sanitized_key = key
            found = True
            break

    if not found:
        return jsonify({"error": "Missing valid input field"}), 400

# Optional health check route
@app.route("/")
def home():
    return "Server is running"

if __name__ == "__main__":
    app.run(debug=True)