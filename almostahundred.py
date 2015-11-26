from flask import Flask, request, jsonify, abort, make_response
app = Flask(__name__)

# TODO: add persistence with sqlite
# TODO: add driver search endpoint

drivers = [
    {
        "driverId": "1",
        "latitude": -23.54981095,
        "longitude": -46.69982655,
        "driverAvailable": True
    },
    {
        "driverId": "2",
        "latitude": -23.60810717,
        "longitude": -46.67500346,
        "driverAvailable": False
    },
    {
        "driverId": "3",
        "latitude": -23.98287476,
        "longitude": -46.11236872,
        "driverAvailable": True
    }]


@app.route('/drivers/', methods=['GET'])
def get_drivers():
    return jsonify({"drivers": drivers})


@app.route('/drivers/<driver_id>/status', methods=['GET', 'POST'])
def driver_status(driver_id):

    if request.method == 'GET':
        print "-- driver_id GET: {0}".format(driver_id)
        driver = [driver for driver in drivers if driver['driverId'] == driver_id]
        if len(driver) == 0:
            abort(404)
        return jsonify({'driver': driver})

    elif request.method == 'POST':
        if 'latitude' and 'longitude' and 'driverAvailable' not in request.json.keys():
            print "NOT HERE"
            abort(400)

        driver_found = False
        for index, driver in enumerate(drivers):
            if driver['driverId'] == driver_id:
                driver_found = True
                drivers[index] = {
                    "driverId": driver_id,
                    "latitude": request.json['latitude'] or "",
                    "longitude": request.json['longitude'] or "",
                    "driverAvailable": request.json['driverAvailable'] or ""
                }

                return driver_id
        if not driver_found:
            abort(404)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    # remember to turn this off!!!!!!
    app.debug = True
    app.run()
