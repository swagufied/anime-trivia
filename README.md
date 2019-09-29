**Anime Trivia Question Server**

This is the home of the code of the server that manages questions and users for a trivia application. It can be interacted through the API described [here](https://docs.google.com/spreadsheets/d/1XjEC3IpQrn4yuho1F6aFb_QaQSmsdBgSqrs62Yvak7U/edit?usp=sharing) or through the [admin portal](https://anime-trivia-api.herokuapp.com/admin/login/). Authentication is doen with JWT tokens. This server will eventually be ported over to the server that actually runs the trivia games, mainly due to the availability of better administration tools on Django, the basic framework of which can be found [here](https://github.com/swagufied/trivia-app).

**Instructions**

This server can serve as a database for other question applications. To run...

- Make necessary modifications to the config file. You probably only need to change the link to the database. This server runs on a PostgreSQL database.

- Create the database then run the line below to create the tables.
```
python db_create.py
```
- Install requirements.
```
pip install -r requirements.txt file
```
- Run the server.
```
python run.py
```
