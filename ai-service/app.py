from flask import Flask, request, jsonify
from services.security import validate_input, sanitize
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Enable rate limit headers
app.config["RATELIMIT_HEADERS_ENABLED"] = True

# Rate limiter setup (30 requests per minute per IP)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30 per minute"]
)
limiter.init_app(app)

# Register routes (Blueprints)
from routes.test_routes import test_bp
app.register_blueprint(test_bp)

# Handle rate limit errors
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Too many requests. Please try again later."
    }), 429

# Global security middleware (runs BEFORE request)
@app.before_request
def security_layer():
    if request.method != "POST":
        return

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    found = False

    # Check for valid input keys
    for key in ["input", "text", "query", "content"]:
        if key in data:
            value = data[key]

            # Validate input
            valid, error = validate_input(value)
            if not valid:
                return jsonify({"error": error}), 400

            # Sanitize input
            request.sanitized_input = sanitize(value)
            request.sanitized_key = key
            found = True
            break

    if not found:
        return jsonify({"error": "Missing valid input field"}), 400

# Global response security headers (fixes ZAP findings)
@app.after_request
def add_security_headers(response):
    # Prevent XSS attacks
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Prevent MIME-type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Reduce server info exposure (optional)
    response.headers["Server"] = "SecureServer"

    return response

# Health check route
@app.route("/")
def home():
    return "Server is running"

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True) 