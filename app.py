from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/organigrama_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Organigrama en la base de datos
class Organigrama(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "fecha_creacion": self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_creacion else None
        }

# Modelo de Nodo en la base de datos
class Nodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(20), nullable=False)
    nodo_padre_id = db.Column(db.Integer, db.ForeignKey('nodo.id'), nullable=True)
    organigrama_id = db.Column(db.Integer, db.ForeignKey('organigrama.id'), nullable=False)  # Referencia al organigrama

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "color": self.color,
            "nodo_padre_id": self.nodo_padre_id,
            "organigrama_id": self.organigrama_id
        }

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para obtener todos los organigramas
@app.route('/get_organigramas', methods=['GET'])
def get_organigramas():
    organigramas = Organigrama.query.all()
    return jsonify([org.to_dict() for org in organigramas])

# Ruta para crear un nuevo organigrama
@app.route('/add_organigrama', methods=['POST'])
def add_organigrama():
    data = request.json
    nuevo_organigrama = Organigrama(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', '')
    )
    db.session.add(nuevo_organigrama)
    db.session.commit()
    return jsonify({"mensaje": "Organigrama creado exitosamente", "id": nuevo_organigrama.id})

# Ruta para obtener un organigrama específico
@app.route('/get_organigrama/<int:id>', methods=['GET'])
def get_organigrama(id):
    organigrama = Organigrama.query.get(id)
    if organigrama:
        return jsonify(organigrama.to_dict())
    return jsonify({"error": "Organigrama no encontrado"}), 404

# Ruta para editar un organigrama
@app.route('/edit_organigrama/<int:id>', methods=['PUT'])
def edit_organigrama(id):
    data = request.json
    organigrama = Organigrama.query.get(id)
    if organigrama:
        organigrama.nombre = data['nombre']
        organigrama.descripcion = data.get('descripcion', organigrama.descripcion)
        db.session.commit()
        return jsonify({"mensaje": "Organigrama actualizado correctamente"})
    return jsonify({"error": "Organigrama no encontrado"}), 404

# Ruta para eliminar un organigrama
@app.route('/delete_organigrama/<int:id>', methods=['DELETE'])
def delete_organigrama(id):
    organigrama = Organigrama.query.get(id)
    if organigrama:
        # Eliminar todos los nodos asociados a este organigrama
        Nodo.query.filter_by(organigrama_id=id).delete()
        db.session.delete(organigrama)
        db.session.commit()
        return jsonify({"mensaje": "Organigrama eliminado"})
    return jsonify({"error": "Organigrama no encontrado"}), 404

# Ruta para obtener todos los nodos de un organigrama específico
@app.route('/get_nodos/<int:organigrama_id>', methods=['GET'])
def get_nodos(organigrama_id):
    nodos = Nodo.query.filter_by(organigrama_id=organigrama_id).all()
    return jsonify([nodo.to_dict() for nodo in nodos])

# Ruta para agregar un nodo a un organigrama específico
@app.route('/add_nodo', methods=['POST'])
def add_nodo():
    data = request.json
    nuevo_nodo = Nodo(
        nombre=data['nombre'],
        color=data['color'],
        nodo_padre_id=data.get('nodo_padre_id'),
        organigrama_id=data['organigrama_id']
    )
    db.session.add(nuevo_nodo)
    db.session.commit()
    return jsonify({"mensaje": "Nodo agregado exitosamente"})

# Ruta para obtener un nodo específico
@app.route('/get_nodo/<int:id>', methods=['GET'])
def get_nodo(id):
    nodo = Nodo.query.get(id)
    if nodo:
        return jsonify(nodo.to_dict())
    return jsonify({"error": "Nodo no encontrado"}), 404

# Ruta para editar un nodo
@app.route('/edit_nodo/<int:id>', methods=['PUT'])
def edit_nodo(id):
    data = request.json
    nodo = Nodo.query.get(id)
    if nodo:
        nodo.nombre = data['nombre']
        nodo.color = data['color']
        nodo.nodo_padre_id = data.get('nodo_padre_id')
        db.session.commit()
        return jsonify({"mensaje": "Nodo actualizado correctamente"})
    return jsonify({"error": "Nodo no encontrado"}), 404

# Ruta para eliminar un nodo
@app.route('/delete_nodo/<int:id>', methods=['DELETE'])
def delete_nodo(id):
    nodo = Nodo.query.get(id)
    if nodo:
        db.session.delete(nodo)
        db.session.commit()
        return jsonify({"mensaje": "Nodo eliminado"})
    return jsonify({"error": "Nodo no encontrado"}), 404

# Crear tablas en la base de datos si no existen
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)