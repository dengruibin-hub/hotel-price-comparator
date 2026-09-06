-- PostgreSQL schema for canonical hotels, platform mappings, and price history.

CREATE TABLE IF NOT EXISTS hotels (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    phone TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hotel_sources (
    id BIGSERIAL PRIMARY KEY,
    hotel_id BIGINT NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    source TEXT NOT NULL CHECK (source IN ('qunar', 'zhixing', 'amap')),
    source_hotel_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_address TEXT,
    source_latitude DOUBLE PRECISION,
    source_longitude DOUBLE PRECISION,
    source_phone TEXT,
    match_score NUMERIC(5,4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source, source_hotel_id)
);

CREATE INDEX IF NOT EXISTS idx_hotel_sources_hotel_id ON hotel_sources(hotel_id);

CREATE TABLE IF NOT EXISTS price_snapshots (
    id BIGSERIAL PRIMARY KEY,
    hotel_id BIGINT NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    source TEXT NOT NULL CHECK (source IN ('qunar', 'zhixing', 'amap')),
    room_type TEXT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    guests INTEGER NOT NULL CHECK (guests >= 1),
    rooms INTEGER NOT NULL CHECK (rooms >= 1),
    room_price NUMERIC(12,2) NOT NULL CHECK (room_price >= 0),
    tax NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (tax >= 0),
    fees NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (fees >= 0),
    total_price NUMERIC(12,2) NOT NULL CHECK (total_price >= 0),
    currency CHAR(3) NOT NULL DEFAULT 'CNY',
    breakfast BOOLEAN NOT NULL DEFAULT FALSE,
    cancelable BOOLEAN NOT NULL DEFAULT FALSE,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (check_out > check_in)
);

CREATE INDEX IF NOT EXISTS idx_price_snapshots_lookup
    ON price_snapshots(hotel_id, check_in, check_out, guests, rooms, checked_at DESC);
