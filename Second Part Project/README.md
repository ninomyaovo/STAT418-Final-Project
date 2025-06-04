This file provides some updates from the project proposal. For the structure of building the app, I separate the original ```STAT418_Final_Project.ipynb``` file into ```optimizer.py``` and ```app.py``` where the first one holds pure logic(data wrangling, optimisation) and second one holds the UI & reactivity. This keeps each file short and testable.

## Data Update 
Based on the EDA, I changed the way of assigning roles to each pokemon. The role Glass Cannon basically serves same functionality as physical sweeper and special sweeper, so I removed it.

Also, legendary Pokémon routinely exceed 600 total base stats and distorted early optimisation tests, so I removed it. The resulting, clean dataset lives at ```pokemon_clean.csv``` and is what both the Flask API and the Shiny dashboard load at runtime.
