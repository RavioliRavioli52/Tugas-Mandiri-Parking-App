from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parkir.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class DataKendaraan(db.Model):
    __tablename__ = 'data_kendaraan'

    id = db.Column(db.Integer, primary_key=True)
    nomor_plat = db.Column(db.String(20), unique=True, nullable=False)
    jenis_kendaraan = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<DataKendaraan {self.nomor_plat}>'

class DataParkir(db.Model):
    __tablename__ = 'data_parkir'

    id = db.Column(db.Integer, primary_key=True)
    nomor_plat = db.Column(db.String(20), db.ForeignKey('data_kendaraan.nomor_plat', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    waktu_masuk = db.Column(db.DateTime, nullable=False)
    waktu_keluar = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<DataParkir {self.nomor_plat} masuk pada {self.waktu_masuk}>'

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# API Routes for Data Kendaraan
@app.route('/data_kendaraan', methods=['GET', 'POST'])
def data_kendaraan():
    if request.method == 'GET':
        return get_data_kendaraan()
    elif request.method == 'POST':
        return create_data_kendaraan()

@app.route('/data_kendaraan/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def data_kendaraan_detail(id):
    if request.method == 'GET':
        return get_data_kendaraan_detail(id)
    elif request.method == 'PUT':
        return update_data_kendaraan(id)
    elif request.method == 'DELETE':
        return delete_data_kendaraan(id)

# API Routes for Data Parkir
@app.route('/data_parkir', methods=['GET', 'POST'])
def data_parkir():
    if request.method == 'GET':
        return get_data_parkir()
    elif request.method == 'POST':
        return add_parkir()

@app.route('/data_parkir/<int:id>', methods=['PUT', 'DELETE'])
def data_parkir_detail(id):
    if request.method == 'PUT':
        return update_data_parkir(id)
    elif request.method == 'DELETE':
        return delete_data_parkir(id)

# Update Waktu Keluar for Data Parkir
@app.route('/update_waktu_keluar', methods=['POST'])
def update_waktu_keluar():
    data = request.json
    parkir_id = data['parkirId']
    waktu_keluar = data['waktuKeluar']
    
    parkir = DataParkir.query.get_or_404(parkir_id)
    parkir.waktu_keluar = datetime.strptime(waktu_keluar, '%Y-%m-%d %H:%M:%S')
    db.session.commit()
    
    return jsonify({'message': 'Waktu Keluar updated successfully!'})

# Helper Functions for Data Kendaraan
def get_data_kendaraan():
    kendaraan_list = DataKendaraan.query.all()
    data_kendaraan = [{'id': kendaraan.id, 'nomor_plat': kendaraan.nomor_plat, 'jenis_kendaraan': kendaraan.jenis_kendaraan} for kendaraan in kendaraan_list]
    return jsonify({'data_kendaraan': data_kendaraan})

def create_data_kendaraan():
    data = request.json
    new_kendaraan = DataKendaraan(nomor_plat=data['nomor_plat'], jenis_kendaraan=data['jenis_kendaraan'])
    db.session.add(new_kendaraan)
    db.session.commit()
    return jsonify({'message': 'Data Kendaraan created successfully!'})

def get_data_kendaraan_detail(id):
    kendaraan = DataKendaraan.query.get_or_404(id)
    data_kendaraan = {'id': kendaraan.id, 'nomor_plat': kendaraan.nomor_plat, 'jenis_kendaraan': kendaraan.jenis_kendaraan}
    return jsonify(data_kendaraan)

def update_data_kendaraan(id):
    kendaraan = DataKendaraan.query.get_or_404(id)
    data = request.json
    kendaraan.nomor_plat = data.get('nomor_plat', kendaraan.nomor_plat)
    kendaraan.jenis_kendaraan = data.get('jenis_kendaraan', kendaraan.jenis_kendaraan)
    db.session.commit()
    return jsonify({'message': 'Data Kendaraan updated successfully!'})

def delete_data_kendaraan(id):
    kendaraan = DataKendaraan.query.get_or_404(id)
    db.session.delete(kendaraan)
    db.session.commit()
    return jsonify({'message': 'Data Kendaraan deleted successfully!'})

# Helper Functions for Data Parkir
def get_data_parkir():
    parkir_list = DataParkir.query.all()
    data_parkir = [
        {
            'id': parkir.id,
            'nomor_plat': parkir.nomor_plat,
            'waktu_masuk': parkir.waktu_masuk.strftime('%Y-%m-%d %H:%M:%S'),
            'waktu_keluar': parkir.waktu_keluar.strftime('%Y-%m-%d %H:%M:%S') if parkir.waktu_keluar else None
        } for parkir in parkir_list
    ]
    return jsonify({'data_parkir': data_parkir})

def add_parkir():
    data = request.get_json()
    nomor_plat = data['nomor_plat']
    waktu_masuk = datetime.strptime(data['waktu_masuk'], '%Y-%m-%dT%H:%M')

    # Validasi apakah nomor plat ada di DataKendaraan
    kendaraan = DataKendaraan.query.filter_by(nomor_plat=nomor_plat).first()
    if not kendaraan:
        return jsonify({'message': 'Nomor plat tidak ditemukan di data kendaraan'}), 400

    new_parkir = DataParkir(nomor_plat=nomor_plat, waktu_masuk=waktu_masuk)
    db.session.add(new_parkir)
    db.session.commit()
    return jsonify({'message': 'Data parkir berhasil ditambahkan'})

def update_data_parkir(id):
    parkir = DataParkir.query.get_or_404(id)
    data = request.json
    parkir.nomor_plat = data.get('nomor_plat', parkir.nomor_plat)
    parkir.waktu_masuk = datetime.strptime(data.get('waktu_masuk'), '%Y-%m-%dT%H:%M') if data.get('waktu_masuk') else parkir.waktu_masuk
    parkir.waktu_keluar = datetime.strptime(data.get('waktu_keluar'), '%Y-%m-%dT%H:%M') if data.get('waktu_keluar') else parkir.waktu_keluar
    db.session.commit()
    return jsonify({'message': 'Data Parkir updated successfully!'})

def delete_data_parkir(id):
    parkir = DataParkir.query.get_or_404(id)
    db.session.delete(parkir)
    db.session.commit()
    return jsonify({'message': 'Data Parkir deleted successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
