-- Insert the 'default_mapping' and 'test-runner' users
INSERT INTO client (
    username,
    password,
    email,
    public_id,
    company
) 
VALUES (
    'default_mapping',
    'UNHASHED_UNVALID',
    'default@dadeholding.com',
    'cea7797c-7863-47e0-8fdd-7fc239aec050',
    'DadeHolding'
), (
    'test-runner',
    '$2b$12$t3uW3nvEBOj0wAbu5GDvBuFa2ZxjfB93.cjyRXkF8SLxWpk3K.UOm',
    'test@dadeholding.com',
    '055ef876-ce25-4944-ab75-8a1f4a8046c6',
    'DadeHolding'
);