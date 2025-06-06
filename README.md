# STAT418-Final-Project
Building a strong team with only 6 slots in a Pokémon team takes a lot to consider. This app allows users to filter by basic stats such as HP, Attack, Speed, etc., and then generates a team that minimizes overlapping type weaknesses.

The data was obtained using an API called pokeapi.co, which provides detailed information on each Pokémon’s stats, types, and evolutionary chain. To ensure quality, only final-evolution Pokémon were included in the pool.

There is also a shiny app that can be accessed at https://ninomyaovo122.shinyapps.io/pokemon-team-optimiser/

For the structure of building the app, I separate the original ```STAT418_Final_Project.ipynb``` file into ```optimizer.py``` and ```app.py``` where the first one holds pure logic(data wrangling, optimisation) and second one holds the UI & reactivity. This keeps each file short and testable.

## Role Assigning Feature
The project works with four clear-cut roles:

| Role    | Assign Rule     |
|----------|----------|
| Tank| highest stat is hp/ def/ spdef|
| Physical Sweeper  | attack is highest & speed >= 75   |
| Special Sweeper  | sp. atk is highest & speed >= 75 |
| Support  | rest of pokemons |


## Model Implementation
The greedy algorithm serves as the model to select team with least amount of repetitive weaknesses and take roles into consideration by including at least one of each role in the team. It follows these rules:
1. Respect the user’s starters – any Pokémon the user picks must appear, even if it violates stat floors or overlaps weaknesses.
2. Full role coverage – at least one Tank, one Physical Sweeper, one Special Sweeper, and one Support.
3. Minimise shared type-weaknesses across the final six.
Because the problem is combinatorial (≈ 10³⁰ possible teams in the full dex!), I use a greedy heuristic that runs in milliseconds but still produces balanced teams in practice.

### The algorithms steps are:
1. force-add user-selected starters to the team and track their weaknesses.
2. From the remaining Pokémon, drop any whose base stats fall below the user’s HP/Atk/Def/SpAtk/SpDef/Speed floors.
3. For each missing role, pick the candidate that introduces zero new weaknesses. Ties are broken by higher total_stat.
4. Fill the remaining slots with candidates that add the fewest new weaknesses (marginal cost), again favouring higher stats on ties.
5. If the pool empties before the team has six members (rare under high stat floors) choose the best-stat leftovers even if they overlap weaknesses.

## Reproduce the Project

### Clone Github Repository
```
git clone https://github.com/ninomyaovo/STAT418-Final-Project
```

### Shiny Dashboard
To use shiny dashboard, I first installed and run shiny locally. Note that every operation should be done under the path ```"Second Part Project"```.
```
python -m pip install -r "Second Part Project/requirements.txt"
python -m pip show shiny      # should print version & location
python -m shiny run --reload app.py
```

### Docker Image
After making sure the dashboard runs locally, the next step is to build a docker image and push to docker hub.
```
docker build -t ninomya/stat418-final-project:latest .
docker push ninomya/stat418-final-project:latest
```

If you’re on Apple Silicon (M1/M2), use docker buildx to build an amd64 image that Cloud Run can pull.
```
docker buildx create --use
docker buildx build --platform linux/amd64 -t docker.io/ninomya/stat418-final-project:latest . --push
```

### Deploy to Google Cloud Run
After creating the google cloud run server, you can run a health check using the API url.
```
curl https://stat418-final-project-696925248391.europe-west1.run.app/health
```

Example test to run
```
#local
curl -X POST http://localhost:9000/build-team \
-H "Content-Type: application/json" \
-d '{"starters":["Raichu"],"hp_floor":80}'

#google cloud run
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"starters":["Raichu"],"hp_floor":100}' \
  https://stat418-final-project-696925248391.europe-west1.run.app/build-team
```
The Flask app auto-reads $PORT, so no --set-env-vars required.
The resulting base URL is used in app.py → API_URL so user can trace the connection.

### Deploy to shinyapps.io
To deploy the app to shinyapps.io, you can obtain your token and use the following code.
```
pip install rsconnect-python           # installs the publisher
rsconnect add --account USERNAME \
--name USERNAME \
--token YOUR-TOKEN \
--secret YOUR-SECRET
```

Generate a manifest & deploy. The ```--new``` ensures you to deploy successfully if you try to redeploy.
```
rsconnect write-manifest shiny .       
rsconnect deploy shiny . --name USERNAME --title pokemon-team-optimiser --new
```

These steps can also be found on shinyapps.io --> user guide --> Working with Shiny for Python.

# Notes
The process of obtaining the data and exploratory data analysis can be found in the "Project Proposal" folder.

The actual data ```pokemon_clean.csv``` can be found in the "Second Part Project" folder.

This project was done mainly for personal use.
