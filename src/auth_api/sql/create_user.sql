INSERT INTO client (
	email,
	password
)
VALUES (
	%(email)s,
	%(password)s

)
RETURNING *
