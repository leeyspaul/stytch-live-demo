import os

from dotenv import load_dotenv
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from stytch import Client

load_dotenv()


stytch_client = Client(
    project_id=os.getenv("PROJECT_ID"),
    secret=os.getenv("SECRET"),
    environment=os.getenv("ENVIRONMENT"),
)

MAGIC_LINK_AUTH_URL = os.getenv("MAGIC_LINK_AUTH_URL")

app = Flask(__name__)
app.secret_key = "DEV"


@app.route("/demo")
def demo():
    return render_template("home.html")


@app.route("/launch-demo", methods=["POST"])
def launch_demo():
    demo_product = request.form["demo-product"]
    demo_redirects = {
        "email-magic-links": "/email-magic-links-demo",
        "sms-otp": "/mobile-otp-demo",
        "email-otp": "/email-otp-demo",
        "whatsapp-otp": "/whatsapp-otp-demo",
    }

    return redirect(demo_redirects[demo_product])


@app.route("/email-magic-links-demo", methods=["GET"])
def email_magic_links_demo():
    return render_template("email-magic-links-demo.html")


@app.route("/email-magic-link", methods=["POST"])
def email_magic_link():
    resp = stytch_client.magic_links.email.login_or_create(
        email=request.form["email"],
        login_magic_link_url=MAGIC_LINK_AUTH_URL,
        signup_magic_link_url=MAGIC_LINK_AUTH_URL
    )

    if resp.status_code != 200:
        return render_template("error.html")

    return render_template("magic-link-emailed.html")


@app.route("/authenticate", methods=["GET"])
def authenticate():
    resp = stytch_client.magic_links.authenticate(request.args.get("token"))

    if resp.status_code != 200:
        return render_template("error.html")

    session["method"] = "Magic Links"

    return redirect("/authenticated")


@app.route("/mobile-otp-demo", methods=["GET"])
def mobile_otp_demo():
    return render_template("otp-demo.html")


@app.route("/whatsapp-otp-demo", methods=["GET"])
def whatsapp_otp_demo():
    return render_template("otp-whatsapp-demo.html")


@app.route("/send-otp", methods=["POST"])
def send_otp():
    phone_number = request.form.get("phone-number")
    resp = stytch_client.otps.sms.login_or_create(phone_number=phone_number)

    if resp.status_code != 200:
        return render_template("error.html")

    data = resp.json()
    session["phone_number_id"] = data["phone_id"]
    return render_template("otp-demo-authenticate.html")


@app.route("/send-whatsapp-otp", methods=["POST"])
def send_whatsapp_otp():
    phone_number = request.form.get("phone-number")
    resp = stytch_client.otps.whatsapp.login_or_create(
        phone_number=phone_number)

    if resp.status_code != 200:
        return render_template("error.html")

    data = resp.json()
    session["phone_number_id"] = data["phone_id"]
    return render_template("otp-demo-authenticate.html")


@app.route("/otps-demo/authenticate", methods=["POST"])
def otps_demo_authenticate():
    passcode = request.form.get("otp-passcode")
    phone_number_id = session["phone_number_id"]

    resp = stytch_client.otps.authenticate(
        method_id=phone_number_id, code=passcode)

    if resp.status_code != 200:
        return render_template("error.html")

    session["method"] = "OTP"

    return redirect("/authenticated")


@app.route("/authenticated", methods=["GET"])
def authenticated():
    data = {
        "method": session["method"]
    }

    return render_template("authenticated.html", data=data)


@app.route("/email-otp-demo", methods=["GET"])
def email_otp_demo():
    return render_template("otp-email-demo.html")


@app.route("/send-email-otp", methods=["POST"])
def send_email_otp():
    email = request.form.get("email")
    resp = stytch_client.otps.email.login_or_create(email=email)

    if resp.status_code != 200:
        return render_template("error.html")

    data = resp.json()
    session["email"] = data["email_id"]
    return render_template("otp-email-demo-authenticate.html")


@app.route("/otps-email-demo/authenticate", methods=["POST"])
def otps_email_demo_authenticate():
    passcode = request.form.get("otp-passcode")
    email_id = session["email"]

    resp = stytch_client.otps.authenticate(method_id=email_id, code=passcode)

    if resp.status_code != 200:
        return render_template("error.html")

    session["method"] = "OTP"

    return redirect("/authenticated")


if __name__ == "__main__":
    app.run(port=9000, debug=True)
