Update for the Second-phase deliverables.
## Data Update 
Based on the EDA, I changed the way of assigning roles to each pokemon where I removed the role glass cannon since it basically serves same functionality as physical sweeper and special sweeper (now the roles are tank, physical sweeper, special sweeper, support). I change to rules from giving a range to each role to combining the filtering and checking each pokemon's highest stat. Eg. If a Pokémon’s highest stat was Attack and its speed is more than 75, it became a Physical Sweeper.
I have also removed legendary pokemons who has high total stats and act like outliers. I uploaded the cleaned data as pokemon_clean.csv for use.

## Model Implementation
The greedy algorithm serves as the model to select team with least amount of repetitive weaknesses and take roles into consideration by including at least one of each role in the team.

## App
For building the app, I separate the original STAT418_Final_Project.ipynb file into optimizer.py and app.py where the first one holds pure logic(data wrangling, optimisation) and app.py holds the UI & reactivity. This keeps each file short and testable.

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
The resulting base URL is used in shiny/app.py → API_URL so graders can trace the connection.

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


