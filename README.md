# SZLG-Alumni
Egy oldal a Kőbányai Szent László Gimnázium alumni közösségének építésére.

# Contribute to the backend
Clone the repo:
```
git clone https://github.com/tlozs/szlg-alumni.git
```

Create virtual environment inside the project root:
```
py -m virtualenv -p python3 venv
```

Activate venv and download dependencies:
```
.\venv\Scripts\activate
pip install -r requirements.txt
```

Build and create database inside the ``restapi`` folder:
```
py manage.py makemigrations
py manage.py migrate
```

You are ready to contribute.