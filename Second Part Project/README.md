For the stat filtering, made sure to exclude legendary pokemons as outliers.

For building the app, I separate the original STAT418_Final_Project.ipynb file into optimizer.py and app.py where the first one holds pure logic(data wrangling, optimisation, helper plots) and app.py holds the UI & reactivity. This keeps each file short and testable.
