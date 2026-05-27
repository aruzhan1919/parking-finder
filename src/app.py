"""
app.py
======
HTTP API layer. Thin wrapper over finder.py.

Rule: this file should contain almost no business logic.
Only request parsing, calling finder, returning JSON, handling errors.
"""

from flask import Flask, jsonify, request
from pydantic import ValidationError

from src.finder import find_nearest_parkings
from src.schemas import FindParkingRequest, FindParkingResponse, ParkingResult

app = Flask(__name__)


@app.route("/health")
def health():
    """Liveness check for deployment platforms."""
    return jsonify({"status": "ok"})


@app.route("/find-parking", methods=["POST"])
def find_parking():
    """
    Find the 3 nearest parkings for a given start and destination.

    Request:
        {"start": [lat, lon], "dest": [lat, lon]}

    Response:
        {"parkings": [{id, coords, drive_time_sec, walk_time_sec}, ...]}
    """
    try:
        req = FindParkingRequest(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "invalid_input", "details": e.errors()}), 400

    results = find_nearest_parkings(req.start, req.dest, top_n=3)

    response = FindParkingResponse(parkings=[ParkingResult(**r) for r in results])
    return jsonify(response.model_dump())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
