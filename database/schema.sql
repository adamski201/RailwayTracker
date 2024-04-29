DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS operator_subscriptions;
DROP TABLE IF EXISTS station_subscriptions;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS arrivals;
DROP TABLE IF EXISTS cancellations;
DROP TABLE IF EXISTS cancellation_types;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS operators;
DROP TABLE IF EXISTS stations;


CREATE TABLE stations (
    station_id SERIAL PRIMARY KEY,
    crs_code VARCHAR(3) UNIQUE NOT NULL,
    station_name VARCHAR(60) NOT NULL
);

CREATE TABLE operators (
    operator_id SERIAL PRIMARY KEY,
    operator_name VARCHAR(60) NOT NULL,
    operator_code VARCHAR(2) UNIQUE
);

CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    service_uid VARCHAR(6) UNIQUE NOT NULL,
    operator_id INT REFERENCES operators(operator_id)
);

CREATE TABLE cancellation_types (
    cancellation_type_id SERIAL PRIMARY KEY,
    cancellation_code VARCHAR(2) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE cancellations (
    cancellation_id SERIAL PRIMARY KEY,
    scheduled_arrival TIMESTAMP NOT NULL,
    cancellation_type_id INT REFERENCES cancellation_types(cancellation_type_id),
    station_id INT REFERENCES stations(station_id),
    service_id INT REFERENCES services(service_id)
);

CREATE TABLE arrivals (
    arrival_id SERIAL PRIMARY KEY,
    scheduled_arrival TIMESTAMP NOT NULL,
    actual_arrival TIMESTAMP NOT NULL,
    station_id INT REFERENCES stations(station_id),
    service_id INT REFERENCES services(service_id)
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(320)
);

CREATE TABLE station_subscriptions (
    station_subscription_id SERIAL PRIMARY KEY,
    is_active BOOLEAN NOT NULL,
    user_id INT REFERENCES users(user_id),
    station_id INT REFERENCES stations(station_id)
);

CREATE TABLE operator_subscriptions (
    operator_subscription_id SERIAL PRIMARY KEY,
    is_active BOOLEAN NOT NULL,
    user_id INT REFERENCES users(user_id),
    operator_id INT REFERENCES operators(operator_id)
);

CREATE TABLE incidents (
    incident_id SERIAL PRIMARY KEY,
    operator_id INT REFERENCES operators(operator_id),
    incident_uuid VARCHAR(32) NOT NULL,
    creation_date TIMESTAMP NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    is_planned BOOLEAN NOT NULL,
    is_cleared BOOLEAN NOT NULL,
    affected_routes TEXT,
    summary TEXT NOT NULL,
    info_link TEXT
);