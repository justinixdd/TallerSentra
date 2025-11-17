from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime
import os

# =============================
# Cargar variables desde .env
# =============================
load_dotenv()

# =============================
# Configuración Flask
# =============================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta_segura")

# Carpeta para subir imágenes
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# =============================
# Conexión a MongoDB Atlas
# =============================
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("❌ ERROR: No se encontró la variable MONGO_URI en el entorno (.env o Render).")

client = MongoClient(MONGO_URI)
db = client["TallerDB"]

# Colecciones
users_collection = db["users"]
buys_collection = db["buys"]
contact_collection = db["contact"]
piezas_collection = db["piezas"]
servicios_collection = db["servicios"]

# =============================
# Crear administrador (una sola vez)
# =============================
def create_admin():
    admin_exists = users_collection.find_one({"username": "admin"})
    if not admin_exists:
        hashed_password = generate_password_hash("admin123", method="pbkdf2:sha256")
        admin_user = {
            "username": "admin",
            "password": hashed_password,
            "is_admin": True
        }
        users_collection.insert_one(admin_user)
        print("✅ Administrador creado correctamente.")

create_admin()

# =============================
# Rutas principales
# =============================
@app.route("/")
def index():
    piezas = list(piezas_collection.find())
    servicios = list(servicios_collection.find())
    return render_template("index.html", piezas=piezas, servicios=servicios)

@app.route("/acercade")
def acercade():
    return render_template("acercade.html")

# =============================
# Ruta productos/admin
# =============================
@app.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "POST":
        if not session.get("is_admin"):
            flash("Acceso no autorizado.", "error")
            return redirect(url_for("login"))

        categoria = request.form["opciones"]
        nombre = request.form["product_name"]
        precio = float(request.form["product_price"])
        descripcion = request.form["product_description"]
        cantidad = int(request.form["product_quantity"])
        imagen = request.files.get("product_image")

        imagen_url = None
        if imagen and imagen.filename:
            filename = secure_filename(imagen.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            imagen.save(filepath)
            imagen_url = f"/{filepath}"

        producto = {
            "categoria": categoria,
            "nombre": nombre,
            "precio": precio,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "imagen_url": imagen_url
        }

        if categoria == "piezas":
            piezas_collection.insert_one(producto)
        elif categoria == "servicios":
            servicios_collection.insert_one(producto)

        flash(f"Producto '{nombre}' agregado correctamente.", "success")
        return redirect(url_for("admin"))

    piezas = list(piezas_collection.find())
    servicios = list(servicios_collection.find())
    return render_template("index.html", piezas=piezas, servicios=servicios)

# =============================
# Admin panel
# =============================
@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        flash("Acceso no autorizado", "error")
        return redirect(url_for("login"))

    users = list(users_collection.find())
    contact = list(contact_collection.find())
    piezas = list(piezas_collection.find())
    servicios = list(servicios_collection.find())
    return render_template("admin.html", users=users, contact=contact, piezas=piezas, servicios=servicios)

# =============================
# Eliminar usuario/mensaje/producto
# =============================
@app.route("/admin/eliminar_usuario/<id>", methods=["POST"])
def eliminar_usuario(id):
    if not session.get("is_admin"):
        flash("Acceso no autorizado", "error")
        return redirect(url_for("index"))
    users_collection.delete_one({"_id": ObjectId(id)})
    flash("Usuario eliminado.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/eliminar_mensaje/<id>", methods=["POST"])
def eliminar_mensaje(id):
    if not session.get("is_admin"):
        flash("Acceso no autorizado", "error")
        return redirect(url_for("index"))
    contact_collection.delete_one({"_id": ObjectId(id)})
    flash("Mensaje eliminado.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/eliminar_producto/<categoria>/<id>", methods=["POST"])
def eliminar_producto(categoria, id):
    if not session.get("is_admin"):
        flash("Acceso no autorizado", "error")
        return redirect(url_for("admin"))

    if categoria == "piezas":
        piezas_collection.delete_one({"_id": ObjectId(id)})
    elif categoria == "servicios":
        servicios_collection.delete_one({"_id": ObjectId(id)})

    flash("Producto eliminado.", "success")
    return redirect(url_for("admin"))

# =============================
# Contactos
# =============================
@app.route("/contactos", methods=["GET", "POST"])
def contactos():
    if request.method == "POST":
        if "user" not in session:
            flash("Debes iniciar sesión para enviar un mensaje.", "error")
            return redirect(url_for("login"))

        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not name or not email or not message:
            flash("Completa todos los campos.", "warning")
            return redirect(url_for("contactos"))

        contact_collection.insert_one({
            "user": session["user"],
            "name": name,
            "email": email,
            "message": message
        })
        flash("Mensaje enviado correctamente.", "success")
        return redirect(url_for("contactos"))

    return render_template("contactos.html")

# =============================
# Perfil usuario
# =============================
@app.route("/perfil")
def perfil():
    if not session.get("user"):
        flash("Debes iniciar sesión para ver tu perfil.", "error")
        return redirect(url_for("login"))

    user_username = session["user"]
    user_buys = list(buys_collection.find({"usuario": user_username}))

    return render_template("perfil.html", username=user_username, buys=user_buys)

# =============================
# FINALIZAR COMPRA (CORREGIDO)
# =============================
@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    if 'user' not in session:
        return {"status": "error", "message": "Debes iniciar sesión."}, 401

    data = request.json
    carrito = data.get("carrito", [])

    if not carrito:
        return {"status": "error", "message": "Carrito vacío."}, 400

    # Crear compra con cantidades multiplicadas
    compra = {
        "usuario": session["user"],
        "productos": carrito,
        "total": sum(item["price"] * item["quantity"] for item in carrito),
        "fecha": datetime.now()
    }

    buys_collection.insert_one(compra)

    # Reducir stock correctamente
    for item in carrito:
        nombre = item["name"]
        cantidad = item["quantity"]

        if piezas_collection.find_one({"nombre": nombre}):
            piezas_collection.update_one(
                {"nombre": nombre},
                {"$inc": {"cantidad": -cantidad}}
            )
        elif servicios_collection.find_one({"nombre": nombre}):
            servicios_collection.update_one(
                {"nombre": nombre},
                {"$inc": {"cantidad": -cantidad}}
            )

    return {"status": "success", "message": "Compra registrada correctamente."}, 200

# =============================
# Login / Registro
# =============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            session["is_admin"] = user.get("is_admin", False)
            if session["is_admin"]:
                flash("Has iniciado sesión como administrador.", "success")
                return redirect(url_for("admin"))
            else:
                flash("Inicio de sesión exitoso.", "success")
                return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos.", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users_collection.find_one({"username": username}):
            flash("Usuario ya registrado.", "warning")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            "username": username,
            "password": hashed_password,
            "is_admin": False
        })
        flash("Registro exitoso.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# =============================
# Logout
# =============================
@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.", "success")
    return redirect(url_for("index"))

# =============================
# Variables de sesión disponibles en todas las plantillas
# =============================
@app.context_processor
def inject_user():
    return dict(user=session.get("user"), is_admin=session.get("is_admin"))

# =============================
# Ejecutar app
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8500)), debug=True)
