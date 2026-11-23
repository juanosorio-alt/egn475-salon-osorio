DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'client'
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    price_cents INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    service_id INTEGER NOT NULL,
    client_name TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'requested',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (service_id) REFERENCES services (id)
);

INSERT INTO services (id, name, description, duration_minutes, price_cents)
VALUES
    (1, 'Haircut', 'Haircut and basic styling', 30, 3500),
    (2, 'Hairstyling', 'Wash and blow-dry', 45, 4500),
    (3, 'Hair Coloring', 'Single-process hair color', 90, 8500),
    (4, 'Deep Conditioning', 'Moisturizing treatment for dry hair', 30, 2500),
    (5, 'Root Touch-Up', 'Color touch-up for new growth', 60, 6000),
    (6, 'Special Occasion Updo', 'Pinned hairstyle for special events', 60, 7000);

INSERT INTO appointments (user_id, service_id, client_name, date, time, status, notes)
VALUES
    (NULL, 1, 'Sofia Martinez', '2026-11-24', '10:00', 'requested', NULL),
    (NULL, 2, 'Maya Rivera', '2026-11-25', '11:30', 'confirmed', NULL),
    (NULL, 3, 'Lena Diaz', '2026-11-27', '14:00', 'requested', 'Single-process color consultation');
