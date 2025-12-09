Evacuation Routing Service
Inteligentne wyznaczanie trasy ewakuacyjnej z uwzględnieniem stref zagrożeń (np. flood zones)

Projekt implementuje usługę backendową + prosty frontend mapowy, który:

- ładuje graf dróg z pliku GeoJSON,

- ładuje warstwy hazardowe (flood zones) także z pliku GeoJSON (polygony),

- wyznacza trasę ewakuacyjną między dwoma punktami,

- unika krawędzi oznaczonych jako „flooded” (modyfikowany Dijkstra),

- zwraca wynik jako GeoJSON + metadane,

- pokazuje trasę na mapie (frontend: Leaflet.js).

Jak uruchomić backend

1️⃣ Zainstaluj zależności
pip install -r requirements.txt
lub jeśli używasz venv:
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows

pip install -r requirements.txt

2️⃣ Uruchom serwer FastAPI

uvicorn app.main:app --reload

Serwer będzie dostępny pod:

👉 http://127.0.0.1:8000

Dokumentacja Swagger:

👉 http://127.0.0.1:8000/docs

🗺️ Jak uruchomić frontend mapowy

W przeglądarce otwórz:

👉 http://127.0.0.1:8000/static/map.html

Frontend pozwala:

- kliknąć lewym — ustawić punkt startowy,

- kliknąć prawym — ustawić punkt końcowy,

- kliknąć Compute route — pobrać i wyświetlić trasę.
- 
🔌 Endpoint API

Przykład:
/api/evac/route?start_lat=50.061&start_lon=19.94&end_lat=50.067&end_lon=19.945
🧪 Testy jednostkowe

Uruchom:
pytest

Testują:

- zapis algorytmu,

- zwracane metadane,

- działanie endpointu API.
📝 Logowanie

Projekt używa Python logging, definiowanego w logging_conf.py:

INFO – start serwera, wczytanie danych

DEBUG – szczegółowe dane tras

WARNING – wykryte błędy danych

ERROR – błędy trasowania







