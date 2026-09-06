-- Price alerts for a hotel and stay combination.

CREATE TABLE IF NOT EXISTS price_alerts (
    id BIGSERIAL PRIMARY KEY,
    hotel_id BIGINT NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    guests INTEGER NOT NULL CHECK (guests >= 1),
    rooms INTEGER NOT NULL CHECK (rooms >= 1),
    target_price NUMERIC(12,2) NOT NULL CHECK (target_price >= 0),
    currency CHAR(3) NOT NULL DEFAULT 'CNY',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    triggered_at TIMESTAMPTZ,
    CHECK (check_out > check_in)
);

CREATE INDEX IF NOT EXISTS idx_price_alerts_lookup
    ON price_alerts(hotel_id, check_in, check_out, guests, rooms, enabled);
