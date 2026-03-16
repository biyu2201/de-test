# Pokemon Ability ETL Service

A containerized micro-batch ETL (Extract, Transform, Load) service built with FastAPI, Pandas, SQLAlchemy, and PostgreSQL. It fetches Pokemon ability data from PokeAPI, transforms it into a tabular structure, inserts it into a relational database, and immediately returns the data as a structured JSON response.

---

## Technical Components

The ETL pipeline consists of three core scripts working together:

### 1. `main.py`
This script serves as the API gateway and orchestrator. It uses FastAPI to expose a single POST endpoint (`/process`).
- **Input Validation:** I use Pydantic `ProcessRequest` to validate incoming JSON request to make sure its contains the needed parameters.
- **Output Validation:** I use Pydantic `ProcessResponse` to format the JSON output accroding to the requirement.
- **Workflow:** JSON Request -> `processor` -> `database` -> JSON Output

### 2. `processor.py`
This script handles the Extraction and Transformation phases of the pipeline. It reaches out to the PokeAPI and cleans the payload. It is broken down into 3 functions for separation of concerns
- `fetch_pokemon_names_and_ability` acts as the main execution function, calling out to the PokeAPI using the `requests` library.
- `process_response` which transforms the ability array into a Pandas DataFrame and convert JSON column to string. 
- `extract_pokemon_names` which parses out all the pokemon names from the API response.
- The "main" function then bundles and outputs these 3 values (the dataframe, the pokemon names list, and the raw effect entries) back to `main.py`.

### 3. `database.py`
This script handles the Load phase of the pipeline, interfacing with the PostgreSQL container.
- **Engine Creation:** Instantiates a SQLAlchemy engine to establish a connection pool to the database, pulling the credentials securely from the environment variables.
- **Loading Logic:** DataFrame are passed into `df.to_sql()` method to insert rows into the table. Since the data is already cleanly formatted as a DataFrame, using `to_sql()` is the simplest and most efficient way to handle data insertion into Postgres.

---

## Getting Started

### Prerequisites
- Docker and Docker Compose installed on your system.

### Configuration
Update the `.env` file in the root directory with your desired PostgreSQL credentials:

```env
POSTGRES_DB=yourdbname
POSTGRES_USER=yourusername
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Running the Service
To build the images and launch the ETL pipeline locally in the background, run:

```bash
docker-compose up --build -d
```

The FastAPI application will be accessible at:
* **API Documentation (Swagger UI):** `http://localhost:8000/docs`
* **Health/Process Endpoint:** `http://localhost:8000/process`

---

## API Documentation

### `POST /process`

Triggers the ETL pipeline for a specific Pokemon Ability ID.

**Request Payload (JSON):**

| Field | Type | Description |
| :--- | :--- | :--- |
| `raw_id` | string | Unique raw identifier for the request |
| `user_id` | string | ID of the user triggering the request |
| `pokemon_ability_id` | string | The PokeAPI Ability ID (e.g. "150" for Imposter) |

**Example Request:**
```bash
curl -X POST "http://localhost:8000/process" \
     -H "Content-Type: application/json" \
     -d '{"raw_id": "7dsa8d7sa9dsa", "user_id": "5199434", "pokemon_ability_id": "150"}'
```

**Response Payload (JSON):**

Returns the exact data that was extracted and loaded into the database alongside specific nested arrays parsed from the PokeAPI.

**Example Response:**
```json
{
  "raw_id": "7dsa8d7sa9dsa",
  "user_id": "5199434",
  "returned_entries": [
    {
      "effect": "This Pokémon transforms into a random opponent upon entering battle.",
      "language": {
        "name": "en",
        "url": "https://pokeapi.co/api/v2/language/9/"
      },
      "short_effect": "Transforms upon entering battle."
    }
  ],
  "pokemon_list": [
    "ditto"
  ]
}
```
