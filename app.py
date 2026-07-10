from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "https://mahendrapulikallup.github.io")

CORS(
    app,
    resources={r"/send-email": {"origins": [ALLOWED_ORIGIN]}},
    supports_credentials=False
)

SMTP_HOST = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
SMTP_PORT = int(os.getenv("SMTP_PORT", 2525))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Mailtrap backend is running!"
    })


@app.route("/send-email", methods=["POST", "OPTIONS"])
def send_email():
    if request.method == "OPTIONS":
        return make_response("", 200)

    try:
        data = request.get_json(silent=True) or {}

        receiver_email = data.get("receiverEmail", "").strip()
        subject = data.get("subject", "").strip()
        message = data.get("message", "").strip()

        if not receiver_email or not subject or not message:
            return jsonify({
                "success": False,
                "message": "Receiver email, subject and message are required."
            }), 400

        if not SMTP_USER or not SMTP_PASS:
            return jsonify({
                "success": False,
                "message": "SMTP_USER or SMTP_PASS missing in Render environment."
            }), 500

        msg = MIMEMultipart()
        msg["From"] = "sandbox@mailtrap.io"
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        # Mailtrap SMTP connection
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(msg["From"], receiver_email, msg.as_string())
        server.quit()

        return jsonify({
            "success": True,
            "message": "Email sent successfully to Mailtrap inbox!"
        }), 200

    except smtplib.SMTPAuthenticationError as e:
        return jsonify({
            "success": False,
            "message": f"SMTP Authentication failed: {str(e)}"
        }), 401

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Backend error: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
