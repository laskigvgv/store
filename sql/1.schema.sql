--
-- Store Postgresql Schema
--


CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    public_id TEXT NOT NULL,
    dedicated_upstream VARCHAR(50),
    company TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_onboarded BOOLEAN DEFAULT false
);