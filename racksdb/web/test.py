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
