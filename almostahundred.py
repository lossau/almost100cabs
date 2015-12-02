import sqlite3
from contextlib import closing
from functools import wraps
from flask import Flask, request, jsonify, make_response, g


app = Flask(__name__)

# TODO: put it in the cloud


# ----- Error Handling ------------------------------------
def make_error(status_code, message, action):
    response = jsonify({
        "error": {
            "status": status_code,
            "message": message,
            "action": action
        }})
    response.status_code = status_code
    return response


# ----- Authentication ------------------------------------
USERNAME = 'admin'
PASSWORD = 'admin'


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == USERNAME and auth.password == PASSWORD):
            return make_error(401, 'Not Authorized', "Enter valid user/pass")
        return f(*args, **kwargs)
    return decorated


# ----- Persistence ---------------------------------------
DATABASE = 'database/drivers.db'


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
def get_or_create_drivers():

    if request.method == 'GET':
        # list all drivers
        db = get_db()
        db.row_factory = sqlite3.Row
        drivers = []
        try:
            for driver in query_db('SELECT driverId, latitude, longitude, driverAvailable, carPlate, name FROM Drivers'):
                drivers.append(_dict_from_row(driver))
            return make_response(jsonify({'drivers': drivers}), 200)
        except:
            return make_error(500, 'Internal Error', "Something went wrong with the databse")

    if request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':
            # input validation
            if 'name' and 'carPlate' not in request.json:
                return make_error(400, 'Bad Request', "Enter either a 'name' or a 'carPlate' for the new driver")

            # insert new driver into database
            db = get_db()
            db.row_factory = sqlite3.Row
            sql = 'INSERT INTO Drivers ('
            fields = ('name', 'carPlate')
            filtered = filter(lambda x: request.json.get(x), fields)
            sql += ", ".join([x for x in filtered]) + ") VALUES ("
            sql += ", ".join(["?" for x in filtered]) + ")"
            try:
                driver_created = db.execute(sql, tuple(map(request.json.get, filtered)))
            except:
                return make_error(500, 'Internal Error', "Something went wrong with the databse")
            db.commit()
            if driver_created.rowcount == 1:
                return ('', 201)
            else:
                return make_error(500, 'Internal Error', "Driver not created")
        else:
            return make_error(400, 'Bad Request', "Input must be JSON")


@app.route('/drivers/<driver_id>/status', methods=['GET', 'POST'])
@requires_auth
def driver_status(driver_id):

    if request.method == 'GET':
        # get the desired driver's status
        db = get_db()
        db.row_factory = sqlite3.Row
        try:
            driver = query_db('SELECT driverId, latitude, longitude, driverAvailable FROM drivers WHERE driverId = ?;', [driver_id], one=True)
        except:
            return make_error(500, 'Internal Error', "Something went wrong with the databse")
        if driver is None:
            # raise InvalidUsage('Driver not found', status_code=404)
            return make_error(404, 'Not Found', 'Enter an existing driverId')
        else:
            return make_response(jsonify({'driver': _dict_from_row(driver)}), 200)

    elif request.method == 'POST':
        if request.headers['Content-Type'] == 'application/json':

            # input validation
            if not request.json:
                return make_error(400, "Bad Request", "Enter 'latitude', 'longitude' or 'driverAvailable'")
            if 'latitude' in request.json.keys():
                if not _is_number(request.json['latitude']):
                    return make_error(400, "Bad Request", "Invalid 'latitude', must be a float number")
            if 'longitude' in request.json.keys():
                if not _is_number(request.json['longitude']):
                    return make_error(400, "Bad Request", "Invalid 'longitude', must be a float number")
            if 'driverAvailable' in request.json.keys():
                if request.json['driverAvailable'] not in ['true', 'false']:
                    return make_error(400, "Bad Request", "Invalid 'driverAvailable', must be either 'false' or 'true'")

            # check if driver exists
            try:
                driver = query_db('SELECT driverId FROM drivers WHERE driverId = ?;', [driver_id], one=True)
            except:
                return make_error(500, 'Internal Error', "Something went wrong with the databse")
            if driver is None:
                return make_error(404, "Not Found", "Driver not found")
            else:
                # modify driver's status
                db = get_db()
                db.row_factory = sqlite3.Row
                sql = 'UPDATE Drivers SET '
                fields = ('latitude', 'longitude', 'driverAvailable')
                filtered = filter(lambda x: request.json.get(x), fields)
                sql += ",".join(["%s=?" for x in filtered])
                sql += ' WHERE driverId=?'
                sql = sql % filtered
                try:
                    driver_modified = db.execute(sql, tuple(map(request.json.get, filtered) + [driver_id]))
                except:
                    return make_error(500, 'Internal Error', "Something went wrong with the databse")
                db.commit()
                if driver_modified.rowcount == 1:
                    return ('', 204)
                else:
                    return make_error(500, "Internal Error", "Driver not modified")
        else:
            return make_error(400, 'Bad Request', "Input must be JSON")


@app.route('/drivers/inArea', methods=['GET'])
@requires_auth
def who_is_active_here():

    # input validation
    try:
        sw = tuple([float(i) for i in request.args.get('sw').split(',')])
        ne = tuple([float(i) for i in request.args.get('ne').split(',')])
    except:
        return make_error(400, "Bad Request", "Invalid 'latitude' or 'longitude', must be a float number")

    # check for drivers inside rectangle
    active_drivers_in_rectangle = []
    db = get_db()
    db.row_factory = sqlite3.Row

    try:
        for driver in query_db('SELECT driverId, latitude, longitude, driverAvailable FROM Drivers'):
            dict_driver = _dict_from_row(driver)
            driver_pos = (dict_driver['latitude'], dict_driver['longitude'])
            driver_available = dict_driver['driverAvailable']
            if _is_inside_rectangle(sw, ne, driver_pos) and driver_available == 'true':
                active_drivers_in_rectangle.append(dict_driver)

        return make_response(jsonify({'active_drivers_in_rectangle': active_drivers_in_rectangle}), 200)
    except:
        return make_error(500, 'Internal Error', "Something went wrong with the databse")


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
