data = {
    'latitude': 123,
    'longitude': 321,
    'driverAvailable': "true"
}


sql = 'UPDATE Drivers SET'

fields = ('latitude', 'longitude', 'driverAvailable')
filtered = filter(lambda x: data.get(x), fields)
# print "---- filtered: {0}".format(filtered)

if not len(filtered):
    print "Error"

# print ["%s=?" for x in filtered]

sql += ",".join(["%s=?" for x in filtered])

# print "---- sql: {0}".format(sql)
sql += ' WHERE driverId=?'
# print "---- sql: {0}".format(sql)
print tuple(map(data.get, filtered) + ["1"])
