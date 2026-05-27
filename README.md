# Parking Finder
 
Simple REST API that finds the 3 nearest parking spots in Astana given a driver's start position and destination.
 
For each parking spot, the API returns:
- driving time from start to the parking
- walking time from the parking to the destination
This is a learning project focused on building a small but production-shaped service end-to-end: API → routing logic → tests → Docker → deployment.
 
## Tech Stack
 
- Python 3.11
- Flask — HTTP API
- NetworkX + OSMnx — road graph and shortest path
- Geopy — geodesic distances
- Pydantic — request/response validation
- Pytest — tests
- Docker — packaging
## Quick Start
 
```bash
# Local
pip install -r requirements.txt
python -m src.app
 
# Docker
docker-compose up
```
 
API will be available at `http://localhost:5000`.
 
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
      "coords": [51.121, 71.425],
      "drive_time_sec": 180,
      "walk_time_sec": 120
    }
  ]
}
```
 
## Project Structure
 
```
src/
├── app.py            # Flask endpoint
├── finder.py         # Business logic: find 3 nearest parkings
├── routing.py        # OSM graph + shortest path
├── parking_data.py   # Hardcoded parking spots (MVP)
└── schemas.py        # Pydantic request/response models
 
tests/
├── test_routing.py
├── test_finder.py
└── test_app.py
```
 
## Roadmap
 
- [x] MVP: hardcoded parkings, basic shortest path
- [ ] Load parkings from OSM tags
- [ ] Add traffic multipliers
- [ ] Frontend with map visualization
- [ ] Deploy to Railway