import sqlite3
from contextlib import closing
from functools import wraps
from flask import Flask, request, jsonify, make_response, g


app = Flask(__name__)

# TODO: think about input parameters requirements
# it should allow availability only, or both lat and lon
# TODO: create endpoint to add driver
# TODO: send to the cloud
# TODO: create another way to find available drivers
# TODO: take care of error 500
# TODO: properly divide app into files. Use Blueprints


# ----- Error Handling ------------------------------------
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


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': 'Not found'}), 404)


@app.errorhandler(301)
def moved_permanently(error):
    return make_response(jsonify({'message': 'Moved Permanently'}), 301)


# ----- Authentication ------------------------------------
USERNAME = 'admin'
PASSWORD = 'admin'


def _check_auth(username, password):
    return username == USERNAME and password == PASSWORD


def _authenticate():
    raise InvalidUsage('Not authorized', status_code=401)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not _check_auth(auth.username, auth.password):
            return _authenticate()
        return f(*args, **kwargs)
    return decorated


# ----- Persistence ---------------------------------------
DATABASE = 'database/drivers.db'
SECRET_KEY = 'admin'


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('database/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_db()
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# ----- Custom Functions ----------------------------------
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


def _dict_from_row(row):
    return dict(zip(row.keys(), row))


# ----- Routes --------------------------------------------
@app.route('/drivers', methods=['GET', 'POST'])
@requires_auth
def get_drivers():

    if request.method == 'GET':
        db = get_db()
        db.row_factory = sqlite3.Row
        drivers = []
        for driver in query_db('select driverId, latitude, longitude, driverAvailable, carPlate, name from Drivers'):
            drivers.append(_dict_from_row(driver))
        return make_response(jsonify({'drivers': drivers}), 200)

    if request.method == 'POST' and request.headers['Content-Type'] == 'application/json':

        if not request.json:
            raise InvalidUsage('Missing parameters', status_code=400)
        if ('name' or 'carPlate') not in request.json.keys():
            raise InvalidUsage('Missing parameters', status_code=400)

        db = get_db()
        db.row_factory = sqlite3.Row

        # TODO: allow either of the parameters and insert accordingly
        created = db.execute('INSERT INTO Drivers (name, carPlate) VALUES (?, ?)', (request.json['name'], request.json['carPlate']))
        db.commit()
        if created.rowcount == 1:
            return ('', 201)
        else:
            raise InvalidUsage('Invalid driver status', status_code=400)


@app.route('/drivers/<driver_id>/status', methods=['GET', 'POST'])
@requires_auth
def driver_status(driver_id):

    if request.method == 'GET':
        db = get_db()
        db.row_factory = sqlite3.Row
        driver = query_db('select driverId, latitude, longitude, driverAvailable from drivers where driverId = ?;', [driver_id], one=True)
        if driver is None:
            raise InvalidUsage('Driver not found', status_code=404)
        else:
            return make_response(jsonify({'driver': _dict_from_row(driver)}), 200)

    elif request.method == 'POST' and request.headers['Content-Type'] == 'application/json':
        if not request.json:
            raise InvalidUsage('Missing parameters', status_code=400)
        if 'latitude' and 'longitude' and 'driverAvailable' not in request.json.keys():
            raise InvalidUsage('Missing parameters', status_code=400)
        if not _is_number(request.json['longitude']) or not _is_number(request.json['latitude']):
            raise InvalidUsage('Invalid coordinates', status_code=400)
        if request.json['driverAvailable'] not in ['true', 'false']:
            raise InvalidUsage('Invalid driver status', status_code=400)

        driver = query_db('select driverId, latitude, longitude, driverAvailable from drivers where driverId = ?;', [driver_id], one=True)
        if driver is None:
            raise InvalidUsage('Driver not found', status_code=404)
        else:
            db = get_db()
            db.row_factory = sqlite3.Row
            db.execute('UPDATE Drivers SET latitude = ?, longitude = ?, driverAvailable = ? WHERE driverId = ?', (request.json['latitude'], request.json['longitude'], request.json['driverAvailable'], driver_id))
            db.commit()
            return ('', 204)


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

    db = get_db()
    db.row_factory = sqlite3.Row

    for driver in query_db('select driverId, latitude, longitude, driverAvailable from Drivers'):
        dict_driver = _dict_from_row(driver)
        driver_pos = (dict_driver['latitude'], dict_driver['longitude'])
        driver_available = dict_driver['driverAvailable']
        if _is_inside_rectangle(sw, ne, driver_pos) and driver_available == 'true':
            active_drivers_in_rectangle.append(dict_driver)

    drivers = []
    for driver in query_db('select driverId, latitude, longitude, driverAvailable from Drivers'):
        drivers.append(_dict_from_row(driver))

    return make_response(jsonify({'active_drivers_in_rectangle': active_drivers_in_rectangle}), 200)


# ----- App Startup ---------------------------------------
if __name__ == '__main__':
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    app.debug = True
    # app.debug = False
    app.config.from_object(__name__)
    init_db()
    app.run()
