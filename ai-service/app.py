from flask import Flask, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.security import validate_input, sanitize
from flask_talisman import Talisman

# Create app FIRST
app = Flask(__name__)

# ---------------------------
# Security (Talisman)
# ---------------------------
csp = {
    'default-src': "'self'",
    'script-src': "'self'",
    'style-src': "'self'",
    'img-src': "'self' data:",
    'font-src': "'self'",
    'connect-src': "'self'",
    'object-src': "'none'",
    'frame-ancestors': "'none'",
    'base-uri': "'self'",
    'form-action': "'self'"
}

Talisman(
    app,
    content_security_policy=csp,
    frame_options="DENY",
    force_https=False   # important for localhost
)

# Add nosniff header manually
@app.after_request
def add_nosniff(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# ---------------------------
# Import routes
# ---------------------------
from routes.query import query_bp
from routes.health import health_bp
from routes.report import report_bp
from routes.test_routes import test_bp

# ---------------------------
# Rate Limiter
# ---------------------------
app.config["RATELIMIT_HEADERS_ENABLED"] = True

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30 per minute"]
)
limiter.init_app(app)

# ---------------------------
# Register Blueprints
# ---------------------------
app.register_blueprint(query_bp)
app.register_blueprint(health_bp)
app.register_blueprint(report_bp)
app.register_blueprint(test_bp)

# ---------------------------
# Error Handler
# ---------------------------
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Too many requests. Please try again later."
    }), 429

# ---------------------------
# Security Middleware
# ---------------------------
@app.before_request
def security_layer():
    if request.method != "POST":
        return

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    for key in ["input", "text", "query", "content","question"]:
        if key in data:
            value = data[key]

            valid, error = validate_input(value)
            if not valid:
                return jsonify({"error": error}), 400

            # FIX: use g instead of request
            g.sanitized_input = sanitize(value)
            g.sanitized_key = key
            return

    return jsonify({"error": "Missing valid input field"}), 400

# ---------------------------
# Home Route
# ---------------------------
@app.route("/")
def home():
    return "Server working"

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    print("Flask is starting...")
    app.run(debug=True, port=5000)