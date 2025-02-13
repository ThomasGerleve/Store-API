# Store-API
Simple store REST API built with Django REST Framework.

# Setup
- Make sure you are in a python virtual environment.
- Run the following commands:
  - `pip install -r requirements.txt`
  - `python manage.py migrate`
- Seed database with:
`python manage.py seed`
- Start a local server with:
`python manage.py runserver`

# Using the API
If you are using Visual Studio Code, you can easily test the API by installing the extension "REST Client"
(humao.rest-client) and opening the `api.http` file. There you can click on "Send request" to make an API call of
your choice.

Otherwise use a tool of your choice (like [Postman](https://www.postman.com/downloads/)) to make API calls.

You first have to get an access token as a user.

If you have seeded the database, you can use your choice of
- store user: (username: store, password: store)
- manager user: (username: manager, password: manager) or
- superuser (username: admin, password: admin)

to make a call to the ( /api/token ) route and copy the access token. You will need to provide this access token for your
other API calls as an authorization bearer token.

If you have not seeded the database create a superuser with `python manage.py createsuperuser` and log in to the admin
panel ( /admin ) where you can create other users and stores yourself. If you want to create a manager user you have to create a
group named "manager" and add it to the user.

Users without the manager role can only view stores.
Users with the manager role can also create, update and delete stores.

You can find the detailed API documentation on ( /schema/swagger-ui ) or ( /schema/redoc/ ).
