from flask import Flask, render_template, request, redirect, session, url_for, flash
from db import db
from ai_model import predict_all
import os

app = Flask(__name__)
app.secret_key = "brainai"

UPLOAD = "static/uploads"
RESULT = "static/results"
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(RESULT, exist_ok=True)


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        if user:
            session["user"] = email
            session["role"] = user[4]

            # Use role to choose where to go
            if user[4] == "admin":
                flash("Logged in as admin.", "success")
                return redirect(url_for("admin"))
            else:
                flash("Logged in as user.", "success")
                return redirect(url_for("user"))

        flash("Invalid email or password.", "error")
        return redirect(url_for("login"))

    # GET: show login page
    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    admin_key = request.form.get("admin_key")
    role = "admin" if admin_key == "brainai123" else "user"
    approved = 1

    existing = db.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    ).fetchone()

    if existing:
        flash("Email already registered.", "error")
        return redirect(url_for("login"))

    db.execute(
        "INSERT INTO users(name,email,password,role,approved) VALUES(?,?,?,?,?)",
        (name, email, password, role, approved)
    )
    db.commit()

    flash("Account created successfully.", "success")
    return redirect(url_for("login"))


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    if "user" in session:
        flash("Logged out.", "info")
    session.clear()
    return redirect(url_for("login"))


# ---------------- ADMIN LOGIN + DASHBOARD ----------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Admin login form
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=? AND role='admin'",
            (email, password)
        ).fetchone()

        if not user:
            flash("Invalid admin login.", "error")
            return redirect(url_for("login"))

        session["user"] = email
        session["role"] = "admin"
        flash("Admin login successful.", "success")
        return redirect(url_for("admin"))

    # Admin dashboard (GET only, after login)
    if "user" not in session or session.get("role") != "admin":
        flash("Please log in as admin.", "error")
        return redirect(url_for("login"))

    users = db.execute("SELECT * FROM users").fetchall()
    msgs = db.execute("SELECT * FROM messages").fetchall()

    return render_template("admin_dashboard.html", users=users, msgs=msgs)


# ---------------- MAKE ADMIN ----------------
@app.route("/make_admin/<email>")
def make_admin(email):
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    db.execute("UPDATE users SET role='admin' WHERE email=?", (email,))
    db.commit()

    flash("User promoted to admin.", "success")
    return redirect(url_for("admin"))


# ---------------- REMOVE ADMIN ----------------
@app.route("/remove_admin/<email>")
def remove_admin(email):
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    db.execute("UPDATE users SET role='user' WHERE email=?", (email,))
    db.commit()

    flash("Admin rights removed.", "success")
    return redirect(url_for("admin"))


# ---------------- USER DASHBOARD ----------------
@app.route("/user")
def user():
    if "user" not in session:
        flash("Please log in.", "error")
        return redirect(url_for("login"))

    return render_template("user_dashboard.html", approved=1)


# ---------------- PREDICT ----------------
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        flash("Please log in to predict.", "error")
        return redirect(url_for("login"))

    files = {}
    for k in ["t1", "t1ce", "flair", "t2"]:
        if k not in request.files:
            flash(f"Missing file: {k}", "error")
            return redirect(url_for("user"))

        f = request.files[k]
        if f.filename == "":
            flash(f"No file selected for {k}.", "error")
            return redirect(url_for("user"))

        path = os.path.join(UPLOAD, f.filename)
        f.save(path)
        files[k] = path

    try:
        result = predict_all(
            files["t1"],
            files["t1ce"],
            files["flair"],
            files["t2"]
        )
    except Exception as e:
        flash(f"Prediction Error: {str(e)}", "error")
        return redirect(url_for("user"))

    return render_template(
        "user_dashboard.html",
        result=result,
        approved=1,
        thanks=True
    )


# ---------------- CHAT ----------------
@app.route("/send", methods=["POST"])
def send():
    if "user" not in session:
        flash("Please log in to send chat.", "error")
        return redirect(url_for("login"))

    msg = request.form["msg"].strip()
    if not msg:
        flash("Message cannot be empty.", "error")
        return redirect(url_for("user"))

    db.execute(
        "INSERT INTO messages(sender,receiver,msg) VALUES(?,?,?)",
        (session["user"], "admin", msg)
    )
    db.commit()

    flash("Message sent to admin.", "info")
    return redirect(url_for("user"))


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)