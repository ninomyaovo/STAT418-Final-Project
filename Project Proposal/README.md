## Scraping Process
1. Data Source:
  Used the PokéAPI to gather structured data about Pokémon.

2. Final Evolution Filtering: For each Pokémon, accessed its /pokemon-species/ endpoint to get the evolution chain. Traversed the evolution chain recursively to find and keep only final-form Pokémon.

3. Stat & Type Extraction: For each final evolution Pokémon, retrieved base stats: HP, Attack, Defense, Sp. Atk, Sp. Def, Speed. Retrieved types: e.g., "ground", "fire"

4. Weakness Calculation: For each Pokémon's type(s), fetched its /type/{type} endpoint. From the "damage_relations" section, collected all types that deal double damage (i.e., weaknesses). Combined weaknesses across all types of that Pokémon.

5. Data Cleaning: Converted weaknesses and types to Python set objects for easy computation. Stored everything in a Pandas DataFrame. Exported the final dataset as final_evolution_pokemon.csv.


## Simple Exploratory Data Analysis:

6. Optional Enhancements: Calculated coverage score: how many other Pokémon a type is strong against. Assigned roles (Tank, Sweeper, etc.) based on stat distributions. Identified and optionally excluded Legendary Pokémon.

