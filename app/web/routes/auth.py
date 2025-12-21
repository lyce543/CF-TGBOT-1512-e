from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from app.database.crud import async_session_maker, get_manager_by_username
import asyncio

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        async def check_credentials():
            async with async_session_maker() as db_session:
                manager = await get_manager_by_username(db_session, username)
                if manager and check_password_hash(manager.password_hash, password):
                    return True
                return False
        
        if asyncio.run(check_credentials()):
            session["manager"] = username
            return redirect(url_for("dialogs.dashboard"))
        else:
            return render_template("login.html", error="Неверные учетные данные")
    
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("manager", None)
    return redirect(url_for("auth.login"))