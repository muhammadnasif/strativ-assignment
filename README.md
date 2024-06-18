# Strativ-Assignment

In order to run the project first create a virtual environment in python.

``` bash
virtualenv venv
```

After successfully creating the virtual environment named "venv" we have to activate it and install all the libraries inside the virtual environment. To do this


For Windows,
``` bash
source venv/Scripts/activate
pip install -r requirements.txt
```

For Linux
``` bash
source venv/bin/activate
pip install -r requirements.txt
```

Then we can run the project using the following command
``` bash
python manage.py runserver 
```

## API

### 1. Travel Suggestion

**Endpoint:** `POST /weather/travel-suggestion/`

This endpoint provides travel suggestions based on the weather conditions of the destination.

**Example Request Payload:**

```json
{
    "from": "Dhaka",
    "to": "Rajshahi",
    "at": "2024-06-21"  // YYYY-MM-DD
}
```

### 2. Top 10 Coolest Districts

**Endpoint:** `GET /weather/top-coolest-districts/`

This endpoint provides list of 10 districts which is coolest for the next 10 days 

### POSTMAN COLLECTION
There is also a **postman collection** provided with **postman environment** which can also be imported to postman to run the project