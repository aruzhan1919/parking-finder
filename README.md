# Parking Finder

A web app that finds the best parking spots in Astana. The user clicks a
**start** point and a **destination** on a 2GIS map, and the app returns the
**top 5 parkings** ranked by total time = *driving time to the parking* +
*walking time from the parking to the destination*.

For each parking it shows real-world info pulled live from 2GIS: name,
address, price, capacity, and tags (covered / heated / guarded).

This is a learning project focused on building a small but production-shaped
service end-to-end: map UI → REST API → routing logic → external data →
tests → Docker → deployment.

## Live Demo

Deployed on Railway. ([parking-finder-production-ef5c.up.railway.app](https://parking-finder-production-ef5c.up.railway.app/))

## How It Works

1. The frontend shows a 2GIS map (MapGL JS). The user clicks twice to set
   start and destination.
2. On "Find Parking", the browser sends both coordinates to the backend.
3. The backend queries the **2GIS Places API** for parkings within 1 km of
   the destination (sorted by distance).
4. For each parking it computes driving time over the Astana road graph
   (OSMnx + NetworkX, Dijkstra) plus straight-line walking time to the
   destination.
5. It returns the top 5 by combined time, with price/capacity/tags.

One user search = **one** request to the 2GIS Places API.

## Tech Stack

- Python 3.11
- Flask — HTTP API
- 2GIS MapGL JS — interactive map (frontend)
- 2GIS Places API — live parking data
- OSMnx + NetworkX — road graph and shortest path
- Geopy — geodesic (walking) distance
- Pydantic — request/response validation
- Pytest — tests
- Docker — packaging
- Railway — deployment

## Quick Start

This project needs a **2GIS Places API key**. Get one (a free demo key works)
at https://platform.2gis.ru and create a `.env` file in the project root:

```
GIS_CATALOG_KEY=your_places_api_key
```

The map key (MapGL) is set in `static/app.js`. For deployment, restrict that
key to your domain in the 2GIS Platform Manager.

```bash
# Local
pip install -r requirements.txt
python -m src.app

# Docker
docker-compose up
```

The app will be available at `http://localhost:5002`.

## API

### `POST /find-parking`

**Request:**
```json
{
  "start": [51.13, 71.43],
  "dest": [51.12, 71.42]
}
```

**Response:**
```json
{
  "parkings": [
    {
      "id": "70000001057442538",
      "coords": [51.121, 71.425],
      "name": "Паркинг ТРЦ MEGA Silk Way",
      "address": "проспект Кабанбай батыр, 62",
      "capacity": 1700,
      "price": "400 тнг./час",
      "tags": ["Крытая", "Тёплая", "Охраняемая"],
      "drive_time_sec": 180.4,
      "walk_time_sec": 120.7
    }
  ]
}
```

### `GET /health`

Liveness check, returns `{"status": "ok"}`.

## Project Structure

```
src/
├── app.py            # Flask endpoints (HTTP layer only)
├── finder.py         # Business logic: rank parkings by total time
├── routing.py        # OSM road graph + shortest path (driving time)
├── parking_data.py   # Live parking lookup via 2GIS Places API
└── schemas.py        # Pydantic request/response models

static/
├── app.js            # 2GIS MapGL map + UI logic
└── style.css

templates/
└── index.html

scripts/
├── fetch_parkings.py     # One-off: dump all Astana parkings to JSON
└── build_debug_map.py    # One-off: standalone HTML map of those parkings

tests/
├── test_routing.py
├── test_finder.py        # API calls mocked (no quota used)
└── test_app.py
```

## Testing

```bash
pytest -m "not slow"   # fast: validation + parsing, no network
pytest                 # full: also builds the Astana road graph
```

External API calls are mocked in tests, so running them does not consume your
2GIS quota.

## Notes & Limitations

- Walking time is a straight-line approximation (geodesic distance ÷ walking
  speed), not a pedestrian route.
- The 2GIS demo key is limited to 1000 Places requests/month and 10 results
  per request, which is why the app fetches one page (10 nearest) and ranks
  those.
- The road graph is cached after first load; it does not auto-refresh.

## Roadmap

- [x] MVP: hardcoded parkings, basic shortest path
- [x] Live parking data from 2GIS Places API
- [x] Frontend with 2GIS map and clickable points
- [x] Show price, capacity, and tags per parking
- [x] Deploy to Railway
- [ ] Pedestrian routing instead of straight-line walking time
- [ ] Filters (free only / covered / open now)
- [ ] Trip cost calculator (hourly vs daily tariff)
