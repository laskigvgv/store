INSERT INTO cart(
    client_id,
    items
)
VALUES (
    %(client_id)s,
    %(items)s
)
RETURNING *