
CREATE TABLE IF NOT EXISTS games (
    appid INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    developer TEXT,
    publisher TEXT
);

CREATE TABLE IF NOT EXISTS game_snapshots (
    appid INTEGER NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    positive INTEGER,
    negative INTEGER,
    price INTEGER,
    initialprice INTEGER,
    discount INTEGER,
    ccu INTEGER,
    PRIMARY KEY (appid, collected_at),
    FOREIGN KEY (appid) REFERENCES games(appid)
);
