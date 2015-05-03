pragma foreign_keys=ON; 

CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    brand TEXT DEFAULT NULL,
    measurement_type TEXT NOT NULL,
    use_within INT DEFAULT NULL,
    -- default expiry date warning is 2 days
    expiry_date_warning INT DEFAULT 2,
    CHECK (measurement_type IN ("quantity", "weight", "volume"))
);

CREATE UNIQUE INDEX unique_product
on products (name, brand);

CREATE TABLE IF NOT EXISTS fridge_contents(
    item_id INTEGER PRIMARY KEY NOT NULL,      
    product_id INT NOT NULL,
    quantity INT DEFAULT NULL, 
    weight INT DEFAULT NULL,
    volume INT DEFAULT NULL,
    expiration_date TEXT DEFAULT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS favourites(
    product_id INTEGER PRIMARY KEY NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
