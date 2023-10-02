from racksdb import RacksDB

db = RacksDB.load()


for datacenter in db.datacenters.items:
    print(datacenter.name)
    print(datacenter.tags)

print(' ')
print('####################################')
print(' ')

print(db.datacenters.first().name)

print(' ')
print('####################################')
print(' ')

for infrastructure in db.infrastructures:
    print(infrastructure.name)
    print(infrastructure.tags)


print(' ')
print('####################################')
print(' ')

for datacenter in db.datacenters.items:
    for room in datacenter.rooms:
        for row in room.rows:
            for rack in row.racks:
                print(datacenter.name)
                print(datacenter.tags)
                print(room.name)
                print(room.dimensions.width)
                print(room.dimensions.depth)
                print(len(room.rows.items))
                print(rack.name)


print(' ')
print('####################################')
print(' ')

for infrastructure in db.infrastructures:
    for r in infrastructure.layout:
        print(infrastructure.name)
        print(r.rack.name)


print(' ')
print('####################################')
print(' ')


for datacenter in db.datacenters.filter(name='paris'):
    for infrastructure in db.infrastructures.filter(name='moon'):
            for room in datacenter.rooms:
                for row in room.rows:
                    for rack in row.racks:
                        print(rack.name, ' ', infrastructure.name)
                            

print(' ')
print('####################################')
print(' ')

for infrastructure in db.infrastructures.filter(name='moon'):
    for rack in infrastructure.layout:
        for node in rack.nodes:
            print(infrastructure.name)
            print(node.name) # nom du noeud
            print(node.type.id) # identifiant du type de node



print(' ')
print('####################################')
print(' ')

for infrastructure in db.infrastructures.filter(name='mercury'):
    for rack in infrastructure.layout:
        for node in rack.nodes:
            print(infrastructure.name)
            print(node.type.id)
            print(node.type.model)
            print(node.type.height)
            print(node.type.width)
            print(node.type.specs)
            print(node.type.cpu.sockets)
            print(node.type.cpu.model)
            print(node.type.cpu.specs)
            print(node.type.cpu.cores)
            print(node.type.ram.dimm)
            print(node.type.netifs)

print(' ')
print('####################################')
print(' ')

for infrastructure in db.infrastructures.filter(name='mercury'):
    for rack in infrastructure.layout:
        for storage in rack.storage:
            for type in storage.type.disks:
                print(infrastructure.name)
                print(storage.type.id)
                print(storage.type.model)
                print(storage.type.height)
                print('disks:')
                print(type.type)
                print(type.size)
                print(type.model)
                print(type.number)


print(' ')
print('####################################')
print(' ')

for infrastructure in db.infrastructures.filter(name='mercury'):
    for rack in infrastructure.layout:
        for network in rack.network:
            for type in network.type.netifs:
                print('###################################')
                print(infrastructure.name)
                print(network.type.id)
                print(network.type.model)
                print(network.type.height)
                print(network.type.width)
                print('netifs:')
                print(type.type)
                print(type.bandwidth)
                print(type.number)


print(' ')
print('####################################')
print(' ')

for datacenter in db.datacenters:
    for room in datacenter.rooms:
        for row in room.rows:
            for rack in row.racks:
                print(row.name)
                print(rack.type.id)
                print(rack.type.slots)
                data = row.name

print(' ')
print('####################################')
print(' ')

for node in db.infrastructures['mercury'].nodes:
    print(node.type.height)