from flask import Flask, request, jsonify
import requests 
import os 

app = Flask(__name__)

# Leer URLs de los servicios desde variables de entorno
WAND_URL = os.getenv("WAND_URL", "http://wand-service:5001")
HOUSE_URL = os.getenv("HOUSE_URL", "http://house-service:5002")
OWL_URL = os.getenv("OWL_URL", "http://owl-service:5003")

@app.route('/enroll', methods=['POST'])
def enroll_student():
    student_data = request.get_json()
    if not student_data or 'student' not in student_data:
        return jsonify({"error": "Se requiere el campo 'student'"}), 400
    
    student = student_data['student']
    successful_steps = []

    try:
        # Paso 1: Validar Varita
        print(f"Iniciando Matrícula para {student}")
        res = requests.post(f"{WAND_URL}/validate", json={"student": student})
        res.raise_for_status() # Lanza una excepción si el status no es 2xx
        successful_steps.append("wand")
        print(f"✅ Varita validada para {student}")

        # Paso 2: Asignar Casa (puede fallar)
        res = requests.post(f"{HOUSE_URL}/assign", json={"student": student})
        res.raise_for_status()
        successful_steps.append("house")
        print(f"✅ Casa asignada para {student}")

        # Paso 3: Enviar Lechuza
        res = requests.post(f"{OWL_URL}/deliver", json={"student": student})
        res.raise_for_status()
        successful_steps.append("owl")
        print(f"✅ Lechuza enviada a {student}")

        print(f"🎉 Matrícula completada exitosamente para {student}")
        return jsonify({"status": "success", "student": student}), 200

    except requests.exceptions.RequestException as e:
        print(f"❌ Fallo en la matrícula para {student}. Error: {e.response.text if e.response else str(e)}")
        # Iniciar compensación en orden inverso
        print("--- Iniciando compensación ---")
        if "owl" in successful_steps:
            requests.post(f"{OWL_URL}/revoke", json={"student": student})
            print(f"↪️ Lechuza revocada para {student}")
        if "house" in successful_steps:
            requests.post(f"{HOUSE_URL}/undo", json={"student": student})
            print(f"↪️ Asignación de casa deshecha para {student}")
        if "wand" in successful_steps:
            requests.post(f"{WAND_URL}/revoke", json={"student": student})
            print(f"↪️ Validación de varita revocada para {student}")
        
        return jsonify({"status": "failed", "student": student, "error": "Saga fallida, compensación ejecutada"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)