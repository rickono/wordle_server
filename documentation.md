# Documentation

## API Endpoints

### Authentication

- POST: `/register` register a new user.
  - body:
    ```json
    {
      "username": String,
      "password": String,
      "name": String
    }
    ```
  - returns
- POST: `/login` login user.

  - body:
    ```json
    {
      "username": String,
      "password": String
    }
    ```
  - returns:
    ```json
    {
      "msg": String,
      "token"?: String
    }
    ```

### Games

- GET: `/games`
  - Query Parameters: `user` (user id)
    - returns only games that the user has played
