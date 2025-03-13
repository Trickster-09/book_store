import os
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, request, jsonify

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
print(f"🔹 URI de conexión a MongoDB: {MONGO_URI}")

app = Flask(__name__)

client = MongoClient(MONGO_URI)
db = client["Biblioteca"]
usuarios = db["usuarios"]


@app.route("/usuario/<correo>/libros", methods=["GET"])
def obtener_libros_usuario(correo):
    usuario = usuarios.find_one({"correo": correo}, {"_id": 0, "libros_own": 1})
    return jsonify(usuario or {"libros_own": []})

@app.route("/usuario/<correo>/agregar", methods=["POST"])
def agregar_libro(correo):
    data = request.json
    titulo = data.get("titulo")

    if not titulo:
        return jsonify({"error": "Debe proporcionar un título"}), 400

    usuario = usuarios.find_one({"correo": correo})

    if not usuario:
        usuarios.insert_one({"correo": correo, "libros_own": []})

    usuarios.update_one({"correo": correo}, {"$addToSet": {"libros_own": titulo}})
    
    return jsonify({"message": f"Libro '{titulo}' agregado con éxito."})


@app.route("/usuario/<correo>/eliminar", methods=["DELETE"])
def eliminar_libro(correo):
    data = request.json
    titulo = data.get("titulo")

    if not titulo:
        return jsonify({"error": "Debe proporcionar un título"}), 400

    usuarios.update_one({"correo": correo}, {"$pull": {"libros_own": titulo}})
    return jsonify({"message": f"Libro '{titulo}' eliminado con éxito."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

