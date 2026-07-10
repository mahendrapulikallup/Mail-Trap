from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Your GitHub Pages origin (ONLY domain, not repo path)
ALLOWED_ORIGIN = "https://mahendrapulikallup.github.io"

CORS(
    app,
    resources={r"/*": {"origins": [ALLOWED_ORIGIN]}},
    supports_credentials=False
)

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 2525))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "SMTP Backend is running!"
    })


@app.route("/send-email", methods=["POST", "OPTIONS"])
def send_email():
    if request.method == "OPTIONS":
        response = make_response("", 200)
        origin = request.headers.get("Origin")
        if origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return response

    try:
        data = request.get_json(force=True)

        receiver_email = data.get("receiverEmail", "").strip()
        subject = data.get("subject", "").strip()
        message = data.get("message", "").strip()

        if not receiver_email or not subject or not message:
            return jsonify({
                "success": False,
                "message": "Receiver email, subject and message are required"
            }), 400

        if not SMTP_HOST or not SMTP_PORT or not SMTP_USER or not SMTP_PASS:
            return jsonify({
                "success": False,
                "message": "Mailtrap environment variables are missing in Render"
            }), 500

        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, receiver_email, msg.as_string())
        server.quit()

        return jsonify({
            "success": True,
            "message": "Email sent successfully!"
        }), 200

    except smtplib.SMTPAuthenticationError:
        return jsonify({
            "success": False,
            "message": "Mailtrap authentication failed. Check SMTP_USER and SMTP_PASS."
        }), 401

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
