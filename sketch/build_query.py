data1 = {
    'latitude': 123,
    'longitude': 321,
    'driverAvailable': "true"
}


sql1 = 'UPDATE Drivers SET '

fields1 = ('latitude', 'longitude', 'driverAvailable')
filtered1 = filter(lambda x: data1.get(x), fields1)

sql1 += ", ".join(["%s=?" for x in filtered1])
sql1 += ' WHERE driverId=?'
sql1 = sql1 % filtered1

# print sql1

# ------------------------------------------------------------------

# INSERT INTO Drivers (name, carPlate) VALUES (?, ?)

data2 = {
    "name": "Saulo",
    "carPlate": "CCO-1233",
    "dasd": "dqw"
}

sql2 = 'INSERT INTO Drivers ('
fields2 = ('name', 'carPlate')
filtered2 = filter(lambda x: data2.get(x), fields2)

sql2 += ", ".join([x for x in filtered2]) + ") VALUES ("
sql2 += ", ".join(["?" for x in filtered2]) + ")"
print sql2
