DROP TABLE IF EXISTS archive.station_performance;
DROP TABLE IF EXISTS archive.operator_performance;

CREATE TABLE archive.station_performance(
    station_performance_id SERIAL PRIMARY KEY,
    station_id INT REFERENCES public.stations(station_id),
    day DATE NOT NULL,
    delay_1m_count INT DEFAULT 0, 
    delay_5m_count INT DEFAULT 0, 
    avg_delay_min DECIMAL(4,2) DEFAULT 0,
    arrival_count INT NOT NULL, 
    cancellation_count INT DEFAULT 0
);

CREATE TABLE archive.operator_performance(
    operator_performance_id SERIAL PRIMARY KEY,
    operator_id INT REFERENCES public.operators(operator_id),
    day DATE NOT NULL,
    delay_1m_count INT DEFAULT 0, 
    delay_5m_count INT DEFAULT 0, 
    avg_delay_min DECIMAL(4,2) DEFAULT 0,
    arrival_count INT NOT NULL, 
    cancellation_count INT DEFAULT 0
);