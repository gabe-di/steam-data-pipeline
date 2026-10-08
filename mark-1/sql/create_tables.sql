CREATE TABLE games (
    appid INTEGER PRIMARY KEY,
    name VARCHAR,
    developer VARCHAR,
    publisher VARCHAR,
    positive INTEGER,
    negative INTEGER,
    price_cents INTEGER,
    initial_price_cents INTEGER,
    discount INTEGER,
    ccu INTEGER
);
