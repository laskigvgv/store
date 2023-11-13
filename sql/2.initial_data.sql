-- Insert the 'default_mapping' and 'test-runner' users
INSERT INTO client (
    username,
    password,
    email,
    company
) 
VALUES (
    'default_mapping',
    'UNHASHED_UNVALID',
    'default@dadeholding.com',
    'DadeHolding'
), (
    'test-runner',
    '$2b$12$t3uW3nvEBOj0wAbu5GDvBuFa2ZxjfB93.cjyRXkF8SLxWpk3K.UOm',
    'test@dadeholding.com',
    'DadeHolding'
);

-- Insert into cart
INSERT INTO cart(
	client_id,
	items
)
VALUES (
	2,
	'[{"item_name": "item1", "quantity": 2}, {"item_name": "item2", "quantity": 1}]'
);