import pandas as pd
import requests
import logging
import json


def extract_pokemon_names(raw_data: list[dict]) -> list[str]:
    pokemon_list = []
    for pokemon in raw_data:
        pokemon_name = pokemon['pokemon']['name']
        pokemon_list.append(pokemon_name)
    return pokemon_list


def process_response(raw_data: list[dict], user_id: str, raw_id: str, ability_id: str) -> pd.DataFrame:
    df = pd.DataFrame(raw_data)

    if not df.empty:
        df['raw_id'] = raw_id
        df['user_id'] = user_id
        df['pokemon_ability_id'] = ability_id
        df['language'] = df['language'].apply(json.dumps)
    else:
        # Define expected schema even if empty
        df = pd.DataFrame(columns=['effect', 'language', 'short_effect', 'raw_id', 'user_id', 'pokemon_ability_id'])
    
    return df


def fetch_pokemon_names_and_ability(input_data: dict) -> tuple[pd.DataFrame, list[str], list[dict]]:
    # Extract the JSON input
    user_id = input_data['user_id']
    raw_id = input_data['raw_id']
    ability_id = input_data['pokemon_ability_id']
    
    url = f'https://pokeapi.co/api/v2/ability/{ability_id}'

    try:
        response = requests.get(url=url)
        
        response.raise_for_status() 
        json_response = response.json()

        effect_entries_raw = json_response.get('effect_entries', [])
        pokemon_names_raw = json_response.get('pokemon', [])
    except Exception as e:
        logging.error(f"Failed to fetch data from PokeAPI: {e}")
        # Re-raise to abort the transaction in the caller
        raise
    
    # Process response and get dataframe and pokemon name list
    df = process_response(effect_entries_raw, user_id, raw_id, ability_id)
    pokemon_names = extract_pokemon_names(pokemon_names_raw)

    return df, pokemon_names, effect_entries_raw