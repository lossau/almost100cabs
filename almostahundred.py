from flask import Flask, request, jsonify, make_response
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
            raise InvalidUsage('Driver not found', status_code=404)
        return jsonify({'driver': driver})

    elif request.method == 'POST':

        # validation
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
                    "latitude": request.json['latitude'],
                    "longitude": request.json['longitude'],
                    "driverAvailable": request.json['driverAvailable']
                }

                return ('', 204)
        if not driver_found:
            raise InvalidUsage('Driver not found', status_code=404)


# GET /drivers/inArea?sw=-23.612474,-46.702746&ne=-23.589548,-46.673392
@app.route('/drivers/inArea', methods=['GET'])
def who_is_active_here():

    # validation
    try:
        sw = tuple([float(i) for i in request.args.get('sw').split(',')])
        ne = tuple([float(i) for i in request.args.get('ne').split(',')])
    except:
        raise InvalidUsage('Invalid coordinates', status_code=400)

    drivers_in_rectangle = []
    for driver in drivers:
        driver_pos = (driver['latitude'], driver['longitude'])
        driver_availability = driver['driverAvailable']
        if _is_inside_rectangle(sw, ne, driver_pos) and driver_availability == 'true':
            drivers_in_rectangle.append(driver)

    return make_response(jsonify({'drivers_in_rectangle': drivers_in_rectangle}), 200)


# Error Handler
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


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


if __name__ == '__main__':
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    app.debug = True
    app.run()
