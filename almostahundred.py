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
        print "-- driver_id GET: {0}".format(driver_id)
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
        if not is_bool(request.json['driverAvailable']):
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
def who_is_here():

    sw = tuple([float(i) for i in request.args.get('sw').split(',')])
    ne = tuple([float(i) for i in request.args.get('ne').split(',')])
    rectangle = get_rectangle(sw, ne)
    # driver_pos = ("-23.592466", "-46.683393")
    # is_driver_in_rectangle = point_in_poly(driver_pos, rectangle)

    drivers_in_rectangle = []

    for driver in drivers:
        driver_pos = (driver['latitude'], driver['longitude'])
        if point_in_poly(driver_pos, rectangle):
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


def point_in_poly(point, poly):

    x = float(point[0])
    y = float(point[1])

    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def get_rectangle(sw, ne):
    nw = (sw[0], ne[1])
    se = (ne[0], sw[1])
    return [sw, se, ne, nw]


if __name__ == '__main__':
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    # remember to leave this off!!!!!!
    app.debug = True
    app.run()
