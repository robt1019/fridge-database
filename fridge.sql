pragma foreign_keys=ON; 

CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    manufacturer TEXT DEFAULT NULL,
    measurement_type TEXT NOT NULL,
    CHECK (measurement_type IN ("quantity", "weight", "volume"))
);

CREATE UNIQUE INDEX unique_product
on products (name);

CREATE TABLE IF NOT EXISTS fridge_contents(
    item_id INTEGER PRIMARY KEY NOT NULL,      
    product_id INT NOT NULL,
    quantity INT DEFAULT NULL, 
    weight INT DEFAULT NULL,
    volume INT DEFAULT NULL,
    expiration_date TEXT DEFAULT NULL,
    FOREIGN KEY(product_id) REFERENCES products(ID)
);

CREATE TABLE IF NOT EXISTS favourites(
    product_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Products(ID)
);

CREATE TABLE IF NOT EXISTS current_date(
    current_date TEXT NOT NULL
);
