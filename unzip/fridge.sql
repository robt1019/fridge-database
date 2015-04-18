pragma foreign_keys=ON; 
CREATE TABLE IF NOT EXISTS products(
    ID INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    weight REAL
);

CREATE UNIQUE INDEX unique_product
on products (name, manufacturer, weight);

CREATE TABLE IF NOT EXISTS fridge_contents(
    item_id INT PRIMARY KEY NOT NULL,      
    product_id INT NOT NULL,
    count INT NOT NULL,
    expiration_date TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(ID)
);

CREATE TABLE IF NOT EXISTS favourites(
    product_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Products(ID)
);

CREATE TABLE IF NOT EXISTS external_information(
    current_date DATE NOT NULL
);
