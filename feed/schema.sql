-- The six entities of docs/design.md. Dates are ISO text, so text order is date order.

CREATE TABLE IF NOT EXISTS source (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    url           TEXT NOT NULL,
    access_path   TEXT NOT NULL,
    owner_rank    INTEGER NOT NULL,   -- 1 organiser or operator, 2 ticketing, 3 listing
    place         TEXT NOT NULL,
    default_town  TEXT,               -- only for a source of one town
    default_category TEXT
);

CREATE TABLE IF NOT EXISTS page (
    id            INTEGER PRIMARY KEY,
    source_id     TEXT NOT NULL REFERENCES source (id),
    url           TEXT NOT NULL,
    content_hash  TEXT NOT NULL,
    fetched_at    TEXT NOT NULL,
    http_status   INTEGER,
    text          TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS item (
    id            INTEGER PRIMARY KEY,
    kind          TEXT NOT NULL CHECK (kind IN ('event', 'season', 'experience')),
    title         TEXT NOT NULL,
    town          TEXT NOT NULL,
    time_shape    TEXT NOT NULL,
    repeats_yearly INTEGER NOT NULL DEFAULT 0,
    category      TEXT NOT NULL DEFAULT 'other',
    status        TEXT NOT NULL DEFAULT 'live'
                  CHECK (status IN ('live', 'needs review', 'cancelled', 'rejected')),
    venue         TEXT,
    price_text    TEXT,
    about         TEXT,
    action_link   TEXT,
    source_link   TEXT NOT NULL,
    first_seen    TEXT NOT NULL,
    last_seen_at  TEXT NOT NULL,
    last_verified TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS occurrence (
    id            INTEGER PRIMARY KEY,
    item_id       INTEGER NOT NULL REFERENCES item (id),
    start_date    TEXT NOT NULL,
    end_date      TEXT NOT NULL,
    precision     TEXT NOT NULL CHECK (precision IN ('day', 'month')),
    time_text     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS occurrence_dates ON occurrence (start_date, end_date);

CREATE TABLE IF NOT EXISTS evidence (
    id            INTEGER PRIMARY KEY,
    item_id       INTEGER NOT NULL REFERENCES item (id),
    field         TEXT NOT NULL,
    value         TEXT NOT NULL,
    quote         TEXT NOT NULL,
    page_id       INTEGER NOT NULL REFERENCES page (id),
    model         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS change (
    id            INTEGER PRIMARY KEY,
    item_id       INTEGER NOT NULL REFERENCES item (id),
    field         TEXT NOT NULL,
    old_value     TEXT,
    new_value     TEXT,
    found_at      TEXT NOT NULL,
    actor         TEXT NOT NULL CHECK (actor IN ('ingest', 'review'))
);
