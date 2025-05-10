## Scraping Process
Data Source: Used the PokéAPI to gather structured data about Pokémon. ```get``` method in Request Library in python was used to make HTTP GET requests to the PokéAPI endpoints. Then each API response returns data in JSON format, which is structured like a nested dictionary. The final data include 254 pokemons from 500 pokemons in order to be more comparable and will not have repetitive types showing for multiple times.

The scrapped data included:

1. Final Evolution Filtering: For each Pokémon, accessed its ```/pokemon-species/{name}``` endpoint to get the evolution chain. Traversed the evolution chain recursively to find and keep only final-form Pokémon.

2. Stat & Type Extraction: For each final evolution Pokémon, retrieved base stats: HP, Attack, Defense, Sp. Atk, Sp. Def, Speed. Retrieved types: e.g., "ground", "fire"

3. Weakness Calculation: For each Pokémon's type(s), fetched its ```/type/{type}``` endpoint. From the ```["damage_relations"]["double_damage_from"]``` section, collected all types that deal double damage (i.e., weaknesses).

4. Roles Assigning: I used a rule-based approach based on their base stats, including HP, Attack, Defense, Special Attack, Special Defense, and Speed. Each Pokémon was categorized into one of several roles—Tank, Physical Sweeper, Special Sweeper, Glass Cannon, or Support—depending on which stat thresholds they met. These thresholds were chosen based on the actual distribution of stats in the dataset. For example, Pokémon with high HP and strong defenses were labeled as Tanks. If a Pokémon didn’t meet the criteria for any specialized role, it was labeled as Support.



For data cleaning, I converted weaknesses and types to Python set objects for easy computation. Then I stored everything in a Pandas DataFrame, and exported the final dataset as final_evolution_pokemon.csv.


## Simple Exploratory Data Analysis:

6. Optional Enhancements: Calculated coverage score: how many other Pokémon a type is strong against. Assigned roles (Tank, Sweeper, etc.) based on stat distributions. Identified and optionally excluded Legendary Pokémon.

