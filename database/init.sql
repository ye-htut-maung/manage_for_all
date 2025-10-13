-- db_init/init.sql

CREATE TABLE rules (
    id SERIAL PRIMARY KEY,
    rule_text TEXT NOT NULL
);

CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(255)
);

CREATE TABLE responsibilities (
    id SERIAL PRIMARY KEY,
    member_id INTEGER NOT NULL,
    responsibility_text TEXT NOT NULL,
    FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    member_id INTEGER,
    task_description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE
);