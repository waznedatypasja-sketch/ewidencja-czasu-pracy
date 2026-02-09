# Ewidencja Czasu Pracy (MVP)

Django web-app (PL) z RCP, ręcznymi wpisami, akceptacją przełożonego, wnioskami urlopowymi i raportem do wypłat.

## Uruchomienie lokalnie
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Najważniejsze
- Pracownik widzi tylko swoje dane
- Przełożony widzi tylko swój zespół
- Admin widzi wszystko + raport do wypłat

## Hosting
Ustaw env: SECRET_KEY, DEBUG=0, ALLOWED_HOSTS, DATABASE_URL (Postgres).

