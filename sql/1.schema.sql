--
-- Store Postgresql Schema
--


CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart (
    id SERIAL PRIMARY KEY,
	client_id INTEGER NOT NULL REFERENCES client(id),
	items JSONB
);