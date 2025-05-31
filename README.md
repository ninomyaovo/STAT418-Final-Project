# STAT418-Final-Project
Building a strong team with only 6 slots in a Pokémon team takes a lot to consider. This app allows users to filter by basic stats such as HP, Attack, Speed, etc., and then generates a team that minimizes overlapping type weaknesses.

The data was obtained using an API called pokeapi.co, which provides detailed information on each Pokémon’s stats, types, and evolutionary chain. To ensure quality, only final-evolution Pokémon were included in the pool.

To generate a team with the least amount of repetitive weaknesses, I used a greedy algorithm that:

- Scores each Pokémon based on offensive coverage (how many other Pokémon are weak to its type),

- Prefers those with fewer weaknesses,

- Selects team members one by one, avoiding overlap in weaknesses when possible.

If the user chooses, they can even pre-select the first few Pokémon manually, and the algorithm will fill the rest with optimal picks based on type balance and minimal redundancy.
There is also a shiny app that can be accessed at()

# Notes
Detail of data processing can be found in the "Project Proposal" folder.
Detail of team selection methods can be found in the "Second Part Project" folder.
My collected data can be accessed in the pokemon_clean.csv file.
This project was done mainly for personal use.
