Update for the Second-phase deliverables. For the structure of building the app, I separate the original ```STAT418_Final_Project.ipynb``` file into ```optimizer.py``` and ```app.py``` where the first one holds pure logic(data wrangling, optimisation) and second one holds the UI & reactivity. This keeps each file short and testable.

## Data Update 
Based on the EDA, I changed the way of assigning roles to each pokemon. The role Glass Cannon basically serves same functionality as physical sweeper and special sweeper, so I removed it. The project now works with four clear-cut roles:

| Role    | Assign Rule     |
|----------|----------|
| Tank| highest stat is hp/ def/ spdef|
| Physical Sweeper  | attack is highest & speed >= 75   |
| Special Sweeper  | sp. atk is highest & speed >= 75 |
| Support  | rest of pokemons |

Also, legendary Pokémon routinely exceed 600 total base stats and distorted early optimisation tests, so I removed it. The resulting, clean dataset lives at ```pokemon_clean.csv``` and is what both the Flask API and the Shiny dashboard load at runtime.


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
6. Convert the internal set-of-weaknesses column to a human-readable comma-separated string, then emit a tidy DataFrame to the API caller.

## Shiny Dashboard
To use shiny dashboard, I first installed and run shiny locally. Note that every operation should be done under the path ```"Second Part Project"```.
```
python -m pip install -r "Second Part Project/requirements.txt"
python -m pip show shiny      # should print version & location
python -m shiny run --reload app.py
```

## Docker Image
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

## Deploy to Google Cloud Run
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

## Deploy to shinyapps.io
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
rsconnect deploy shiny . --name USERNAME --title pokemon-team-optimiser2 --new
```

These steps can also be found on shinyapps.io --> user guide --> Working with Shiny for Python.


