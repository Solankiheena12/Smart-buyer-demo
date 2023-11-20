#Smart Buyer -BE

1)	Clone the Git Repo from `https://github.com/nkukadiya89/smart-buyer-BE/tree/develop`

2)	Setup Project in local and create virtual environment :- py -m venv .venv This will create a virtual environment for you

3)	Activate the environment 
        1.	`cd .venv` Change your directory to .venv
        2.	and then `\Scripts\activate`

4)	Find requirment.txt file and do the following with pip :- `pip install requirements.txt` This will install all the package required for project

5)	Go to your Postgres Database (PgAdmin) and Create Database :- `smart_buyer_db`

6)	Configure Postgres Database in `.env` file

        1.	DB_NAME = `smart_buyer_db`
        2.	DB_USER = your user name
        3.	DB_PASSWORD = your password
        4.	DB_HOST = localhost
        5.	DB_PORT = 5432

7)	Now run this command :- Migrate with `py manage.py migrate` 
	This will migrate all the models to database

9)	Now run this command :- `py manage.py createsuperuser` using this command create superuser 

10)	Run you Django server :- `py manage.py runserver` This will run you project in localhost

