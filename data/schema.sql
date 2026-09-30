PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS source_metadata (
    key TEXT PRIMARY KEY, value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS block_groups (
    row_id INTEGER PRIMARY KEY,
    median_value_usd REAL NOT NULL CHECK(median_value_usd > 0),
    median_income REAL NOT NULL CHECK(median_income > 0),
    housing_age REAL NOT NULL CHECK(housing_age > 0),
    total_rooms REAL NOT NULL CHECK(total_rooms > 0),
    total_bedrooms REAL NOT NULL CHECK(total_bedrooms > 0),
    population REAL NOT NULL CHECK(population > 0),
    households REAL NOT NULL CHECK(households > 0),
    latitude REAL NOT NULL, longitude REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS split_membership (
    row_id INTEGER PRIMARY KEY REFERENCES block_groups(row_id),
    split TEXT NOT NULL CHECK(split IN ('train','validation','test'))
);
CREATE INDEX IF NOT EXISTS idx_split ON split_membership(split);
CREATE VIEW IF NOT EXISTS housing_features AS
SELECT b.row_id, median_income AS MedInc, housing_age AS HouseAge,
    total_rooms / households AS AveRooms,
    total_bedrooms / households AS AveBedrms,
    population AS Population, population / households AS AveOccup,
    latitude AS Latitude, longitude AS Longitude,
    median_value_usd / 100000.0 AS MedHouseVal, s.split
FROM block_groups b JOIN split_membership s USING(row_id);
