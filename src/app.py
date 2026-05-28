"""
app.py
======
HTTP API layer + frontend.

Rule: this file should contain almost no business logic.
Only request parsing, calling finder, returning JSON, handling errors.
"""

import os

from flask import Flask, jsonify, render_template, request
from pydantic import ValidationError

from src.finder import find_nearest_parkings
from src.schemas import FindParkingRequest, FindParkingResponse, ParkingResult
from src.routing import get_graph

# Resolve folders relative to project root, not src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


@app.route("/")
def index():
    """Serve the frontend page."""
    return render_template("index.html")


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
    data = request.get_json()
    if not data:
        return jsonify({"error": "empty_body"}), 400

    try:
        req = FindParkingRequest(**data)
    except ValidationError as e:
        return jsonify({"error": "invalid_input", "details": e.errors()}), 400

    results = find_nearest_parkings(req.start, req.dest, top_n=3)

    response = FindParkingResponse(parkings=[ParkingResult(**r) for r in results])
    return jsonify(response.model_dump())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
