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
        datacenter_info ={
            'name': datacenter.name,
            'tags': datacenter.tags
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

if __name__ == '__main__':
    app.run(debug=True)