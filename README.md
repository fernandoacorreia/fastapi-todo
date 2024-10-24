# fastapi-todo

Sample TODO service with FastAPI.

## Setup

```shell
python -m venv myenv
source ./myenv/bin/activate
pip install -r ./requirements.txt
```

## Running

```shell
python main.py
```

## Usage

### Register a user

```shell
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secretpassword"
  }'
```

### Login and get token

```shell
export ACCESS_TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secretpassword" \
  | jq -r .access_token)
```

### Create a TODO

```shell
curl -X POST "http://localhost:8000/todos/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Complete the tutorial"}'
```

### List all TODOs

```shell
curl -X GET "http://localhost:8000/todos/" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Update a TODO

```shell
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Only Title and Priority Updated",
    "description": null,
    "priority": 4
  }'
```

### Mark TODO as complete

```shell
curl -X PATCH "http://localhost:8000/todos/1/complete" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```
