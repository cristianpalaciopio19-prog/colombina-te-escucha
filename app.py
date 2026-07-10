import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g

from routes_data import RUTAS, TIPOS_PQR

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "colombina-te-escucha-dev-key")

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "pqr.db"))
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "colombina2026")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS pqr (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            nombre TEXT NOT NULL,
            cin TEXT NOT NULL,
            ruta TEXT NOT NULL,
            municipio TEXT NOT NULL,
            conductor TEXT NOT NULL,
            placa TEXT NOT NULL,
            tipo_pqr TEXT NOT NULL,
            detalle TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        rutas_json=json.dumps(RUTAS, ensure_ascii=False),
        tipos_pqr=TIPOS_PQR,
    )


@app.route("/enviar", methods=["POST"])
def enviar():
    nombre = request.form.get("nombre", "").strip()
    cin = request.form.get("cin", "").strip()
    ruta = request.form.get("ruta", "").strip()
    municipio = request.form.get("municipio", "").strip()
    conductor = request.form.get("conductor", "").strip()
    placa = request.form.get("placa", "").strip()
    tipo_pqr = request.form.get("tipo_pqr", "").strip()
    detalle = request.form.get("detalle", "").strip()

    if not all([nombre, cin, ruta, municipio, conductor, placa, tipo_pqr, detalle]):
        flash("Por favor completa todos los campos antes de enviar.", "error")
        return redirect(url_for("index"))

    if tipo_pqr not in TIPOS_PQR:
        flash("Tipo de PQR no válido.", "error")
        return redirect(url_for("index"))

    db = get_db()
    db.execute(
        """
        INSERT INTO pqr (fecha, nombre, cin, ruta, municipio, conductor, placa, tipo_pqr, detalle)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nombre,
            cin,
            ruta,
            municipio,
            conductor,
            placa,
            tipo_pqr,
            detalle,
        ),
    )
    db.commit()

    flash("¡Gracias! Tu PQR fue registrada correctamente.", "success")
    return redirect(url_for("index"))


@app.route("/admin")
def admin():
    clave = request.args.get("clave", "")
    if clave != ADMIN_PASSWORD:
        return render_template("admin_login.html")

    db = get_db()
    registros = db.execute(
        "SELECT * FROM pqr ORDER BY id DESC"
    ).fetchall()
    return render_template("admin.html", registros=registros, clave=clave)


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
