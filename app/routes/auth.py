"""Authentication: admin login / logout with session management."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        role = session.get("role", "admin")
        if role == "customer":
            return redirect(url_for("customer_portal.home"))
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        # Check admin credentials
        if (username == current_app.config["ADMIN_USERNAME"]
                and password == current_app.config["ADMIN_PASSWORD"]):
            session.permanent = True
            session["logged_in"] = True
            session["username"] = username
            session["role"] = "admin"
            flash("Welcome back, Administrator.", "success")
            nxt = request.args.get("next")
            return redirect(nxt or url_for("dashboard.index"))
        
        # Check customer credentials
        if (username == current_app.config.get("CUSTOMER_USERNAME", "customer")
                and password == current_app.config.get("CUSTOMER_PASSWORD", "customer123")):
            session.permanent = True
            session["logged_in"] = True
            session["username"] = username
            session["role"] = "customer"
            flash("Welcome to Customer Portal.", "success")
            return redirect(url_for("customer_portal.home"))
        
        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
