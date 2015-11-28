from flask import Flask, request, jsonify, abort, make_response
app = Flask(__name__)

# TODO: add persistence with sqlite

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
        driver = [driver for driver in drivers if driver['driverId'] == driver_id]
        if len(driver) == 0:
            abort(404)
        return jsonify({'driver': driver})

    elif request.method == 'POST':

        # validation
        if not request.json:
            abort(400)
        if 'latitude' and 'longitude' and 'driverAvailable' not in request.json.keys():
            abort(400)
        if not is_number(request.json['longitude']) or not is_number(request.json['latitude']):
            abort(400)
        if not isinstance(request.json['driverAvailable'], bool):
            print 'not bool'
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


# GET /drivers/inArea?sw=-23.612474,-46.702746&ne=-23.589548,-46.673392
@app.route('/drivers/inArea', methods=['GET'])
def who_is_active_here():

    # validation
    try:
        sw = tuple([float(i) for i in request.args.get('sw').split(',')])
        ne = tuple([float(i) for i in request.args.get('ne').split(',')])
    except:
        abort(400)

    drivers_in_rectangle = []
    for driver in drivers:
        driver_pos = (driver['latitude'], driver['longitude'])
        driver_availability = driver['driverAvailable']
        if is_inside_rectangle(sw, ne, driver_pos) and driver_availability == 'true':
            drivers_in_rectangle.append(driver)

    return make_response(jsonify({'drivers_in_rectangle': drivers_in_rectangle}), 200)


# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_bool(s):
    return s in ['true', 'false']


def is_inside_rectangle(sw, ne, point):
    if point[0] < sw[0] or point[0] > ne[0]:
        return False
    elif point[1] < sw[1] or point[1] > ne[1]:
        return False
    else:
        return True


if __name__ == '__main__':
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    app.debug = True
    app.run()
