from flask import Flask, jsonify
from racksdb import RacksDB
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Permet d'activer CORS pour que le frontend Vue.js puisse accéder au backend
db = RacksDB.load()

@app.route('/api/datacenters', methods=['GET'])
def get_datacenters():
    datacenters = []
    for datacenter in db.datacenters.items:
        for room in datacenter.rooms:
            datacenter_info ={
                'name': datacenter.name,
                'tags': datacenter.tags,
                'room_name': room.name,
                'room_width': room.dimensions.width,
                'room_depth': room.dimensions.depth,
                'nb_rack': len(room.rows.items),

            }
            datacenters.append(datacenter_info)
    return jsonify(datacenters)

@app.route('/api/infrastructures', methods=['GET'])
def get_infrastructures():
    infrastructures = []

    for infrastructure in db.infrastructures:
        infrastructure_info = {
            'name': infrastructure.name,
            'tags': infrastructure.tags
        }
        infrastructures.append(infrastructure_info)
    return jsonify(infrastructures)

@app.route('/api/racks', methods=['GET'])
def get_racks():
    racks = []
    for datacenter in db.datacenters.items:
        for room in datacenter.rooms:
            for row in room.rows:
                for rack in row.racks:
                    racks_info ={
                        'datacenter_name': datacenter.name,
                        'rack_name': rack.name,
                    }
                    racks.append(racks_info)
    return jsonify(racks)

if __name__ == '__main__':
    app.run(debug=True)