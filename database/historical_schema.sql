
CREATE TABLE historical_data.station_performance(
    station_performance_id SERIAL PRIMARY KEY,
    station_id INT REFERENCES historical_schema.stations(station_id),
    date TIMESTAMP NOT NULL,
    cancellation_count INT NOT NULL,
    delay_1m_count INT NOT NULL, 
    delay_5m_count INT NOT NULL, 
    avg_delay DECIMAL(4,2) NOT NULL,
    arrival_count INT NOT NULL, 
    common_cancel_code varchar(2) 
)

CREATE TABLE historical_data.operator_performance(
    operator_performance_id SERIAL PRIMARY KEY,
    operator_id INT REFERENCES historical_schema.operators(operator_id),
    date TIMESTAMP NOT NULL,
    cancellation_count INT NOT NULL,
    delay_1m_count INT NOT NULL, 
    delay_5m_count INT NOT NULL, 
    avg_delay DECIMAL(4,2) NOT NULL,
    arrival_count INT NOT NULL, 
    common_cancel_code varchar(2) 
)
