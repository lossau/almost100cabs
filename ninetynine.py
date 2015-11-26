from flask import Flask, request, jsonify, abort
app = Flask(__name__)


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


@app.route('/drivers/<driverId>/status', methods=['GET', 'POST'])
def driver_status(driverId):

    if request.method == 'GET':
        driver = [driver for driver in drivers if driver['driverId'] == driverId]
        if len(driver) == 0:
            abort(404)
        return jsonify({'driver': driver})

        # add sqlite3 database
        driver_data = {
            "latitude": -23.60810717,
            "longitude": -46.67500346,
            "driverId": driverId,
            "driverAvailable": True}
        # return http status too
        return driver_data

    elif request.method == 'POST':
        return


if __name__ == '__main__':
    # remember to turn this off!!!!!!
    app.debug = True
    app.run()
