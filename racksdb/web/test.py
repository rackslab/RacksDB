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
