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

### Create a TODO

```shell
curl -X POST "http://localhost:8000/todos/" -H "Content-Type: application/json" -d '{"title": "Learn FastAPI", "description": "Complete the tutorial"}'
```

### List all TODOs

```shell
curl "http://localhost:8000/todos/"
```

### Mark TODO as complete

```shell
curl -X PATCH "http://localhost:8000/todos/1/complete"
```
