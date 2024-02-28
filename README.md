### Parsing project.

### get started

git clone project:
```bash
git clone https://github.com/AxmetES/task_1_internship.git
```
got to project rep:
```bash
cd /task_1_internship
```

create environments:
```bash
python3 -m venv .venv
```

install requirements:
```bash
pip install -r requirements.txt
```

### run
you should have DB, for example postgresql running in Docker.

```.env example```
```
POSTGRES_DB = your dbname
POSTGRES_USER = your dbname user name
POSTGRES_PASSWORD = your dbname user password
POSTGRES_PORT = db port
POSTGRES_HOST = db host 

```
```bash
python3 main.py
```

#### logs

```bash
tail -f shopkz.log
```