from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import logging
import database as database
import processor as processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TABLE_NAME = "pokemon_abilities"
INSERT_METHOD = "append"

app = FastAPI(title="Pokemon Ability ETL Service")


class ProcessRequest(BaseModel):
    raw_id: str = Field(..., description="Raw ID")
    user_id: str = Field(..., description="User ID")
    pokemon_ability_id: str = Field(..., description="ID of the Pokemon ability to fetch")

class ProcessResponse(BaseModel):
    raw_id: str
    user_id: str
    returned_entries: list[dict]
    pokemon_list: list[str]


@app.post("/process", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED)
def process(request: ProcessRequest):
    logger.info(f"Processing request for ability_id: {request.pokemon_ability_id}")
    
    # 1. Extract and Transform
    try:
        df, pokemon_names, returned_entries = processor.fetch_pokemon_names_and_ability(request.model_dump())
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, 
            detail=f"Failed to extract or transform data from PokeAPI: {str(e)}"
        )
        
    # Check if dataframe is empty
    if df.empty:
        logger.warning(f"No data found for ability_id: {request.pokemon_ability_id}")
        return ProcessResponse(
            raw_id=request.raw_id,
            user_id=request.user_id,
            returned_entries=[],
            pokemon_list=pokemon_names
        )
    
    # 2. Load
    try:
        database.load_to_pg(df, table_name=TABLE_NAME, insert_method=INSERT_METHOD)
    except Exception as e:
        logger.error(f"Loading failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load data into database: {str(e)}"
        )
        
    return ProcessResponse(
        raw_id=request.raw_id, 
        user_id=request.user_id, 
        returned_entries=returned_entries,
        pokemon_list=pokemon_names
    )
