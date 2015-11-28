from flask import Flask, request, jsonify, make_response
from auth import requires_auth
from errors import InvalidUsage


app = Flask(__name__)

# TODO: add persistence with sqlite
# TODO: think about input parameters requirements
# TODO: create endpoint to add driver
# TODO: send to the cloud
# TODO: add authentication
# TODO: create another way to find available drivers

drivers = [
    {
        "driverId": "1",
        "latitude": -23.54981095,
        "longitude": -46.69982655,
        "driverAvailable": False
    },
    {
        "driverId": "2",
        "latitude": -23.60810717,
        "longitude": -46.67500346,
        "driverAvailable": True
    },
    {
        "driverId": "3",
        "latitude": -23.60810734,
        "longitude": -46.67500322,
        "driverAvailable": True
    },
    {
        "driverId": "4",
        "latitude": -23.98287476,
        "longitude": -46.11236872,
        "driverAvailable": True
    },
    {
        "driverId": "5",
        "latitude": -23.60810711,
        "longitude": -46.67500309,
        "driverAvailable": False
    }]


def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def _is_inside_rectangle(sw, ne, point):
    if point[0] < sw[0] or point[0] > ne[0]:
        return False
    elif point[1] < sw[1] or point[1] > ne[1]:
        return False
    else:
        return True


# routes
@app.route('/drivers/', methods=['GET'])
@requires_auth
def get_drivers():
    return jsonify({"drivers": drivers})


@app.route('/drivers/<driver_id>/status', methods=['GET', 'POST'])
@requires_auth
def driver_status(driver_id):

    if request.method == 'GET':
        driver = [driver for driver in drivers if driver['driverId'] == driver_id]
        if len(driver) == 0:
            raise InvalidUsage('Driver not found', status_code=404)
        return jsonify({'driver': driver})

    elif request.method == 'POST':
        # validation
        # which parameters should be required??
        if not request.json:
            raise InvalidUsage('Missing parameters', status_code=400)
        if 'latitude' and 'longitude' and 'driverAvailable' not in request.json.keys():
            raise InvalidUsage('Missing parameters', status_code=400)
        if not _is_number(request.json['longitude']) or not _is_number(request.json['latitude']):
            raise InvalidUsage('Invalid coordinates', status_code=400)
        if not isinstance(request.json['driverAvailable'], bool):
            raise InvalidUsage('Invalid driver status', status_code=400)

        driver_found = False
        for index, driver in enumerate(drivers):
            if driver['driverId'] == driver_id:
                driver_found = True
                drivers[index] = {
                    "driverId": driver_id,
                    "latitude": float(request.json['latitude']),
                    "longitude": float(request.json['longitude']),
                    "driverAvailable": request.json['driverAvailable']
                }

                return ('', 204)
        if not driver_found:
            raise InvalidUsage('Driver not found', status_code=404)


@app.route('/drivers/inArea', methods=['GET'])
@requires_auth
def who_is_active_here():

    # validation
    try:
        sw = tuple([float(i) for i in request.args.get('sw').split(',')])
        ne = tuple([float(i) for i in request.args.get('ne').split(',')])
    except:
        raise InvalidUsage('Invalid coordinates', status_code=400)

    active_drivers_in_rectangle = []
    for driver in drivers:
        driver_pos = (driver['latitude'], driver['longitude'])
        driver_available = driver['driverAvailable']
        if _is_inside_rectangle(sw, ne, driver_pos) and driver_available:
            active_drivers_in_rectangle.append(driver)

    return make_response(jsonify({'active_drivers_in_rectangle': active_drivers_in_rectangle}), 200)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'message': 'Bad Request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'Not found'}), 404)


if __name__ == '__main__':
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    app.debug = True
    # app.debug = False
    app.run()
