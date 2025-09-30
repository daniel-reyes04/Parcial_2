import os
import random
import uuid
from flask import Flask, request, jsonify
from neo4j import GraphDatabase
from dotenv import load_dotenv
import socket

load_dotenv()

app = Flask(__name__)

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(uri, auth=(user, password))

def generar_persona():
    nombres = ["Daniel", "Laura", "Andrés", "Camila", "Juan", "Sofía"]
    nombre = random.choice(nombres)
    edad = random.randint(18, 70)
    persona_id = str(uuid.uuid4())

    return {
        "id": persona_id,
        "nombre": nombre,
        "edad": edad
    }

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/v1/personas", methods=["GET"])
def get_personas():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    skip = (page - 1) * limit

    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Persona)
            RETURN p
            SKIP $skip LIMIT $limit
            """,
            skip=skip, limit=limit
        )
        personas = [dict(record["p"]) for record in result]

        total_result = session.run("MATCH (p:Persona) RETURN count(p) AS total")
        total = total_result.single()["total"]

    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    hostname = socket.gethostname()

    return jsonify({
        "page": page,
        "per_page": limit,
        "total_records": total,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "data": personas,
        "hostname": hostname
    })

@app.route("/v1/legendario", methods=["POST"])
def create_persona():
    persona = generar_persona()

    with driver.session() as session:
        result = session.run(
            """
            CREATE (p:Persona {
                id: $id,
                nombre: $nombre,
                edad: $edad
            })
            RETURN p
            """,
            **persona
        )
        created_persona = dict(result.single()["p"])

    return jsonify({
        "message": "Persona creada exitosamente",
        "data": created_persona
    }), 201
    


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)