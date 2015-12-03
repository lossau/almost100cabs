# almost100cabs


## Overview

**almost100cabs** is an API providing services related to taxi drivers.

### Endpoints

GET    /drivers

POST   /drivers

GET    /drivers/[driver_id]/status

POST   /drivers/[driver_id]/status

GET    /drivers/inArea


### Usage

All comunications are done using JSON.
Here are some example requests to each endpoint, using **curl**.

**Get all drivers**

`$ curl -i 'saulomendes.pythonanywhere.com/drivers' --user admin:admin`

**Get a driver's status**

`$ curl -i 'saulomendes.pythonanywhere.com/drivers/2/status' --user admin:admin`

**Update a driver's status**

`$ curl -i 'saulomendes.pythonanywhere.com/drivers/2/status' -H "Content-Type: application/json" --data '{"latitude": 123, "longitude": 432, "driverAvailable": "true"}' --user admin:admin -X POST`

**Create a new driver**

`$ curl -i 'saulomendes.pythonanywhere.com/drivers' --user admin:admin -X POST --data '{"carPlate": "GRJ-2123", "name": "John"}' -H "Content-Type: application/json"`

**Get all available drivers in area**

`$ curl -i 'saulomendes.pythonanywhere.com/drivers/inArea?sw=-23.612474,-46.702746&ne=-23.589548,-46.673392' --user admin:admin`
