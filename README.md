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

**How is this database formatted?**

Aside from the User and Role table for restricted access, the questions are stored as follows.

- **Show** - this table will group questions under a single show. It has a self-referencing o2m relationship allowing multiple shows to grouped under a parent show. Ex. parent = harry potter, children = sorcerer's stone, chamber of secrets, etc.
  - ShowTitle - the show's titles are stored in this table to account for shows that have multiple titles. As the database was originally made for anime shows, it meant japanese titles and abbreviated titles.

- **Question** - each row simply stores the text for a question and a difficulty level
  - QuestionLink
    - type - can designate the purpose of the url. It can be used to indicate a video, picture, audio, etc. that can be processed accordingly
    - url - this should be self explanatory
  - QuestionTag - the purpose of this table is to allow categorizations for each questions. For example a tag could be used to indicate a show that it falls under, the genre(s) of the question, etc. This table shares a m2m relationship with the Question table and so each tag can be shared amonst many questions.

- **Answer** - This table has a self-referencing relationship with itself. This table was made to allow for the creation of answer sets where each set would have a main answer and several other acceptable answers. There were 2 main reason for this. 1) to make it easier to determine if a related answer was acceptable or not (ex. lord voldemort vs voldemort) and 2) to make autocomplete during a trivia game more user-friendly. A user can type a related answer that they know is correct and have an autocomplete show them the actual answer. Of course this feature can be turned off my marking the "autocomplete_answer" on the question as False. This table has a m2m relationship with the Question table also allowing answers to be shared across multiple questions.
  - AnswerLink - works in exactly the same was as the QuestionLink table



