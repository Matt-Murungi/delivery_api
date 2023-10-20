# bdeliv APIs

Welcome, The bdeliv API is the backend that controls the flow of package delivery in all locations in the country.
This API currently covers the following
- User, Admin and Driver registration, verification, and authorisation
- Partner registration
- Booking and Order Management
- Job assignment to drivers
- Price and Distance calculation
- Job tracking


## Set up

1. Clone the project.
2. Run `pipenv shell` to activate virtualenv.
3. Create an `.env` to cater for the environment variables.
4. Run `python3 app/manage.py runserver` to start project
5. In the url provided, append `/docs` to view the swagger endpoint documentation.
