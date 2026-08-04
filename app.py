import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, url_for, flash, g

from routes_data import RUTAS, TIPOS_PQR

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "colombina-te-escucha-dev-key")

DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "colombina2026")
ZONA_COLOMBIA = ZoneInfo("America/Bogota")


def hora_colombia():
    return datetime.now(ZONA_COLOMBIA).strftime("%Y-%m-%d %H:%M:%S")


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS pqr (
            id SERIAL PRIMARY KEY,
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
    conn.commit()
    cur.close()
    conn.close()


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
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO pqr (fecha, nombre, cin, ruta, municipio, conductor, placa, tipo_pqr, detalle)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            hora_colombia(),
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
    cur.close()

    flash("¡Gracias! Tu PQR fue registrada correctamente.", "success")
    return redirect(url_for("index"))


@app.route("/admin")
def admin():
    clave = request.args.get("clave", "")
    if clave != ADMIN_PASSWORD:
        return render_template("admin_login.html")

    tipo = request.args.get("tipo", "")

    db = get_db()
    cur = db.cursor()
    if tipo:
        cur.execute("SELECT * FROM pqr WHERE tipo_pqr = %s ORDER BY id DESC", (tipo,))
    else:
        cur.execute("SELECT * FROM pqr ORDER BY id DESC")
    registros = cur.fetchall()
    cur.close()
    return render_template(
        "admin.html",
        registros=registros,
        clave=clave,
        filtro_tipo=tipo,
        tipos_pqr=TIPOS_PQR,
    )


@app.route("/admin/detalle/<int:pqr_id>")
def admin_detalle(pqr_id):
    clave = request.args.get("clave", "")
    if clave != ADMIN_PASSWORD:
        return render_template("admin_login.html")

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM pqr WHERE id = %s", (pqr_id,))
    registro = cur.fetchone()
    cur.close()

    if registro is None:
        flash("Ese registro ya no existe.", "error")
        return redirect(url_for("admin", clave=clave))

    return render_template("admin_detalle.html", r=registro, clave=clave)


@app.route("/admin/eliminar/<int:pqr_id>", methods=["POST"])
def admin_eliminar(pqr_id):
    clave = request.form.get("clave", "")
    if clave != ADMIN_PASSWORD:
        return render_template("admin_login.html")

    tipo = request.form.get("tipo", "")

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM pqr WHERE id = %s", (pqr_id,))
    db.commit()
    cur.close()
    flash("Registro eliminado.", "success")
    return redirect(url_for("admin", clave=clave, tipo=tipo))


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
