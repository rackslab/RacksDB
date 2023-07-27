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

for datacenter in db.datacenters.filter(name='paris').items:
    for room in datacenter.rooms:
        print(datacenter.name)
        print(datacenter.tags)
        print(room.name)
        print(room.dimensions.width)
        print(room.dimensions.depth)
        print(len(room.rows.items))
