DROP DATABASE IF EXISTS bhl;
CREATE DATABASE bhl;
\c bhl;

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO roles (name) VALUES
    ('admin'),
    ('sensor'),
    ('user');

CREATE TABLE sensors (
    id SERIAL PRIMARY KEY,
    api_key CHAR(24) UNIQUE NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    social_credit INT NOT NULL,
    role_id INT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    user_name CHAR(20) NOT NULL,
    user_surname CHAR(20) NOT NULL,
    rfid CHAR(12) UNIQUE NOT NULL
);

INSERT INTO users (social_credit, role_id, user_name, user_surname, rfid) VALUES
    (-2137, 2, 'Karol', 'Wojtyla', 696969696969);

CREATE TABLE task_types (
    id SERIAL PRIMARY KEY,
    name CHAR(20) UNIQUE NOT NULL
);

INSERT INTO task_types (name) VALUES
    ('koszenie'),
    ('podlewanie');

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    type INT NOT NULL REFERENCES task_types(id) ON DELETE RESTRICT,
    finished BOOLEAN NOT NULL,
    owner INT REFERENCES users(id) ON DELETE RESTRICT
);

INSERT INTO tasks (type, finished, owner) VALUES
    (1, true, 1),
    (1, false, NULL),
    (2, true, 1),
    (2, false, NULL);