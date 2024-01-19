-- Stores Table
CREATE TABLE stores (
    id UUID PRIMARY KEY
);

INSERT INTO stores (id) VALUES
    ('e07a25d0-1e2e-42a7-9cd9-6db2886da0ab');

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY
);

INSERT INTO users (id) VALUES
    ('ccacaff7-2ecb-4498-a931-ddff57e7bca7');

-- Orders Table
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    store_id UUID NOT NULL,
    user_id UUID NOT NULL,
    created TIMESTAMP,
    name TEXT,
    surname TEXT,
    phone TEXT,
    address TEXT,
    CONSTRAINT fk_store FOREIGN KEY(store_id) REFERENCES stores(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Items Table
CREATE TABLE items (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL,
    quantity INT,
    price DECIMAL,
    CONSTRAINT fk_order FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
); 