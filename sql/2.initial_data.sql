-- Insert the 'default_mapping' and 'test-runner' users
INSERT INTO client (
    password,
    email
) 
VALUES (
    'UNHASHED_UNVALID',
    'default@dadeholding.com'
), (
    '$2b$12$t3uW3nvEBOj0wAbu5GDvBuFa2ZxjfB93.cjyRXkF8SLxWpk3K.UOm',
    'test@dadeholding.com'
);

-- Insert into cart
INSERT INTO cart(
	client_id,
	items
)
VALUES (
	2,
	'[{"id": "654edf8c050f29f5537b7070", "quantity": 2}]'
);

