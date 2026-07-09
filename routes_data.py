# Colombina te Escucha

Formulario web de PQR (Petición, Queja, Reclamo, Sugerencia, Felicitación) para los pasajeros del transporte fijo de Planta Confitería (PL1). Al seleccionar la ruta, se autocompletan Municipio, Conductor y Placa.

## Estructura
```
app.py               -> app Flask (formulario + guardado en SQLite + panel admin)
routes_data.py        -> 24 rutas fijas con conductor/placa/municipio (de Programación_fija.xlsx)
templates/            -> index.html (formulario), admin.html, admin_login.html
static/                -> style.css, colombina_logo.jpg
requirements.txt
Procfile
```

## Correr localmente
```bash
pip install -r requirements.txt
python app.py
```
Abrir http://localhost:5000

## Panel de PQR (solo lectura)
Ir a `/admin` e ingresar la clave (por defecto `colombina2026`, configurable con la variable de entorno `ADMIN_PASSWORD`).

## Subir a GitHub
```bash
cd colombina-te-escucha
git init
git add .
git commit -m "Colombina te Escucha - primera versión"
git branch -M main
git remote add origin https://github.com/cristianpalaciopio19-prog/colombina-te-escucha.git
git push -u origin main
```

## Desplegar en Render
1. New + → Web Service → conectar el repo `colombina-te-escucha`.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app`
4. Variables de entorno (opcional):
   - `ADMIN_PASSWORD` → clave para ver `/admin`
   - `SECRET_KEY` → cualquier cadena aleatoria

## Nota sobre persistencia (igual que en el proyecto Vehículos)
Este proyecto usa SQLite (`pqr.db`) igual que arrancó "Vehiculos". En el plan gratuito de Render el disco no es persistente entre deploys/reinicios, así que los registros pueden perderse. Si necesitas conservarlos de forma permanente, el mismo camino que ya seguimos en "Vehiculos" aplica aquí: migrar a Supabase (Postgres) cuando quieras.
