CREATE TABLE IF NOT EXISTS ActiveCheckoutSessions (
    payment_id UNIQUE,
    session_id UNIQUE,

    PRIMARY KEY (payment_id, session_id)
);