# Importar librerías
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configuración del proyecto
app = Flask(__name__)
CORS(app)

# Configuración de SQL Server
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://username:password@server/database_name?driver=ODBC+Driver+17+for+SQL+Server'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de datos
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(10), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

# Inicializar la base de datos
@app.before_first_request
def create_tables():
    db.create_all()

# Crear una tarea
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    if 'title' not in data or 'description' not in data:
        return jsonify({"error": "Faltan campos obligatorios (title, description)"}), 400
    
    new_task = Task(title=data["title"], description=data["description"])
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

# Listar todas las tareas
@app.route('/tasks', methods=['GET'])
def list_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks]), 200

# Actualizar el estado de una tarea
@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    data = request.json
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404
    
    if 'status' in data:
        task.status = data['status']
        db.session.commit()
        return jsonify(task.to_dict()), 200
    return jsonify({"error": "Falta el campo 'status'"}), 400

# Eliminar una tarea
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Tarea no encontrada"}), 404
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": f"Tarea con id {task_id} eliminada"}), 200

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
