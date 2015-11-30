CREATE TABLE IF NOT EXISTS Drivers(
   driverId INTEGER PRIMARY KEY,
   latitude REAL,
   longitude REAL,
   driverAvailable CHAR(5),
   carPlate CHAR(10),
   name CHAR(150)
);

-- INSERT INTO Drivers (latitude, longitude, driverAvailable, carPlate, name)
-- VALUES 
--     (-23.54981095, -46.69982655, "false", "GJP-9592", "Roberto Leal"),
--     (-23.60810717, -46.67500346, "true", "IUC-3289", "Sandra Sa"),
--     (-23.60810734, -46.67500322, "true", "JAC-0093", "Sidney Magal"),
--     (-23.98287476, -46.11236872, "true", "GUI-1127", "Sergio Malandro"),
--     (-23.60810711, -46.67500309, "false", "ZXA-9033", "Renato Aragao");
