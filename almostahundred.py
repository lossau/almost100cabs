from flask import Flask, request, jsonify, make_response
from functools import wraps

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


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'admin'


def authenticate():
    raise InvalidUsage('Not authorized', status_code=401)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/drivers/', methods=['GET'])
@requires_auth
def get_drivers():
    return jsonify({"drivers": drivers})


@app.route('/drivers/<driver_id>/status', methods=['GET', 'POST'])
@requires_auth
def driver_status(driver_id):

    # GET /drivers/73456/status
    if request.method == 'GET':
        driver = [driver for driver in drivers if driver['driverId'] == driver_id]
        if len(driver) == 0:
            raise InvalidUsage('Driver not found', status_code=404)
        return jsonify({'driver': driver})

    # POST /drivers/8475/status
    # {"latitude": -23.60810717, "longitude": -46.67500346, "driverId": 5997, "driverAvailable": true}
    elif request.method == 'POST':

        # validation
        # should allow which paramenters???????????????????????????????????
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


# GET /drivers/inArea?sw=-23.612474,-46.702746&ne=-23.589548,-46.673392
@app.route('/drivers/inArea', methods=['GET'])
@requires_auth
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
        driver_available = driver['driverAvailable']
        print sw, ne, driver_pos
        print driver_available
        if _is_inside_rectangle(sw, ne, driver_pos) and driver_available:
            drivers_in_rectangle.append(driver)

    return make_response(jsonify({'drivers_in_rectangle': drivers_in_rectangle}), 200)


# Error Handlers
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


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'message': 'Bad Request'}), 400)


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
    # app.debug = False
    app.run()
