from flask import Flask, jsonify
from racksdb import RacksDB
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Permet d'activer CORS pour que le frontend Vue.js puisse accéder au backend
db = RacksDB.load()

# This route gives all the data (datacenter and infrastructure) for the page homeview
@app.route('/api/homeview', methods=['GET'])
def get_homeview():
    datacenters = []
    infrastructures = []
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

    for infrastructure in db.infrastructures:
        infrastructure_info = {
            'name': infrastructure.name,
            'tags': infrastructure.tags,
        }
        infrastructures.append(infrastructure_info)

    reponse_data = {
        'datacenters': datacenters,
        'infrastructures': infrastructures
    }
    return jsonify(reponse_data)


# This route gives all the data for the page datacenter
@app.route('/api/datacenters', methods=['GET'])
def get_datacenters():
    datacenters = []
    racks = []
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

    for datacenter in db.datacenters.items:
        for room in datacenter.rooms:
            for row in room.rows:
                for rack in row.racks:
                    racks_info ={
                        'datacenter_name': datacenter.name,
                        'rack_name': rack.name,
                    }
                    racks.append(racks_info)

    reponse_data = {
        'datacenters': datacenters,
        'racks': racks
    }
    return jsonify(reponse_data)



# This route gives all the data for the page infrastructure
@app.route('/api/infrastructures', methods=['GET'])
def get_infrastructures():
    infrastructures = []
    racks = []
    for infrastructure in db.infrastructures:
                infrastructure_info = {
                    'name': infrastructure.name,
                    'tags': infrastructure.tags,
                }
                infrastructures.append(infrastructure_info)

    for infrastructure in db.infrastructures:
        for rack in infrastructure.layout:
             for node in rack.nodes:
                  rack_info = {
                       'infrastructure_name': infrastructure.name,
                       'rack_name': rack.rack.name,
                       'node_name': node.name,
                       'node_id': node.type.id,  
                  }
                  racks.append(rack_info)


    reponse_data = {
        'infrastructures': infrastructures,
        'racks': racks
    }
    return jsonify(reponse_data)

if __name__ == '__main__':
    app.run(debug=True)