## Initial setup
1. For the hacky "db file mapping" to work, you need to create an empty file first:
```
touch db.sqlite3
```
2. Start the project
```
docker-compose up -d
```
3. Initialize the memodrop
```
docker-compose exec memodrop ./manage.py createsuperuser
```
Create superuser `root` with password `rootroot`
4. Log in and create "German" category in memodrop
5. Run the script add.py on host to add new words

