-- update existing cart list with new product and quantity client_id provided

UPDATE cart 
SET items = %(items)s
WHERE client_id = %(client_id)s
RETURNING *