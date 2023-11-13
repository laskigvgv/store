-- check if a client has already a cart in the database

SELECT * FROM cart WHERE client_id = %(client_id)s;