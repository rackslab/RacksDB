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
    nodes = []
    storages = []
    networks = []

    for infrastructure in db.infrastructures:
                infrastructure_info = {
                    'name': infrastructure.name,
                    'tags': infrastructure.tags,
                }
                infrastructures.append(infrastructure_info)

    for infrastructure in db.infrastructures:
        for rack in infrastructure.layout:
             for node in rack.nodes:
                  node_info = {
                       'infrastructure_name': infrastructure.name,
                       'rack_name': rack.rack.name,
                       'name': node.name,
                       'id': node.type.id,  
                       'type': 'Node'
                  }
                  nodes.append(node_info)

        for infrastructure in db.infrastructures:
            for rack in infrastructure.layout:
                for storage in rack.storage:
                    storage_info = {
                        'infrastructure_name': infrastructure.name,
                        'name': storage.name,
                        'id': storage.type.id,  
                    }
                    storages.append(storage_info)

        for infrastructure in db.infrastructures:
            for rack in infrastructure.layout:
                for network in rack.network:
                    network_info = {
                        'infrastructure_name': infrastructure.name,
                        'name': network.name,
                        'id': network.type.id,  
                    }
                    networks.append(network_info)


    reponse_data = {
        'infrastructures': infrastructures,
        'nodes': nodes,
        'storages': storages,
        'networks': networks,
    }
    return jsonify(reponse_data)

# This route gives all the data about the equipment for the popup on the infrastructure page
@app.route('/api/equipments', methods=['GET'])
def get_equipments():
    node_equipments = []
    storage_equipments = []
    network_equipments = []

    for infrastructure in db.infrastructures:
        for rack in infrastructure.layout:
                for node in rack.nodes:
                    node_info = {
                        'infrastructure_name': infrastructure.name,
                        'node_id': node.type.id,
                        'node_model': node.type.model,
                        'node_height': node.type.height,
                        'node_width': node.type.width,
                        'node_specs': node.type.specs,
                        'node_cpu_socket': node.type.cpu.sockets,
                        'node_cpu_model': node.type.cpu.model,
                        'node_cpu_specs': node.type.cpu.specs,
                        'node_cpu_cores': node.type.cpu.cores,
                        'node_ram_dimm': node.type.ram.dimm,
                        'node_ram_size': node.type.ram.size,
                    } 
                node_equipments.append(node_info)
    
    for infrastructure in db.infrastructures:
         for rack in infrastructure.layout:
              for storage in rack.storage:
                   for type in storage.type.disks:
                        storage_info = {
                             'infrastructure_name': infrastructure.name,
                             'storage_id': storage.type.id,
                             'storage_model': storage.type.model,
                             'storage_height': storage.type.height,
                             'disk_type': type.type,
                             'disk_size': type.size,
                             'disk_model': type.model,
                             'disk_number': type.number
                        }
                        storage_equipments.append(storage_info)
        
    for infrastrucure in db.infrastructures:
         for rack in infrastructure.layout:
              for network in rack.network:
                   for type in network.type.netifs:
                        network_info = {
                            'infrastructure_name': infrastrucure.name,
                            'network_id': network.type.id,
                            'network_model': network.type.model,
                            'network_height': network.type.height,
                            'network_width': network.type.width,
                            'netif_type': type.type,
                            'netif_bandwidth': type.bandwidth,
                            'netif_number': type.number,    
                        }
                        network_equipments.append(network_info)


    reponse_data = {
        'node_equipments': node_equipments,
        'storage_equipments': storage_equipments,
        'network_equipments': network_equipments
    }
    return jsonify(reponse_data)


# This route gives all the data for datacenterRoom page
@app.route('/api/datacenterroom', methods=['GET'])
def get_room():
    datacenters = []
    infrastructures = []
    racks = []

    for datacenter in db.datacenters.items:
        for room in datacenter.rooms:
            datacenter_info ={
                'name': datacenter.name,
                'room_name': room.name,
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

    for infrastructure in db.infrastructures:
        for rack in infrastructure.layout:
                  infrastructure_info = {
                       'name': infrastructure.name,
                       'rack_name': rack.rack.name,
  
                  }
                  infrastructures.append(infrastructure_info)

    reponse_data = {
        'datacenters': datacenters,
        'infrastructures': infrastructures,
        'racks': racks
    }

    return jsonify(reponse_data)
         



if __name__ == '__main__':
    app.run(debug=True)