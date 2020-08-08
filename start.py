# quickly start dev env
import os

os.system('start cmd /k "redis-server"')
os.system('start cmd /k "mongod"')
os.system('start cmd /k "pipenv run py app.py"')
