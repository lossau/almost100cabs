DROP TABLE if exists Drivers;
CREATE TABLE Drivers(
   driverId INT PRIMARY KEY NOT NULL AUTOINCREMENT,
   latitude REAL,
   longitude REAL,
   driverAvailable CHAR(50),
   carPlate CHAR(10),
   name CHAR(150)
);