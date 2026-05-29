"""
app.py
======
HTTP API layer + frontend.

Правило: тут почти нет бизнес-логики.
Только парсинг запроса, вызов finder, отдача JSON, обработка ошибок.
"""

import os
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from pydantic import ValidationError

from src.finder import find_nearest_parkings
from src.schemas import FindParkingRequest, FindParkingResponse, ParkingResult

# Папки считаем от корня проекта, не от src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Радиус поиска парковок вокруг точки назначения (метры)
SEARCH_RADIUS_M = 1000
# Сколько парковок показывать
TOP_N = 5

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


@app.route("/")
def index():
    """Главная страница."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Проверка живости для деплоя."""
    return jsonify({"status": "ok"})


@app.route("/find-parking", methods=["POST"])
def find_parking():
    """
    Найти топ-N парковок для пары start/dest.

    Запрос:  {"start": [lat, lon], "dest": [lat, lon]}
    Ответ:   {"parkings": [{id, coords, name, address, capacity,
                            price, tags, drive_time_sec, walk_time_sec}, ...]}
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "empty_body"}), 400

    try:
        req = FindParkingRequest(**data)
    except ValidationError as e:
        return jsonify({"error": "invalid_input", "details": e.errors()}), 400

    try:
        results = find_nearest_parkings(
            req.start, req.dest, top_n=TOP_N, radius_m=SEARCH_RADIUS_M
        )
    except Exception as e:
        # Например, упал запрос к 2GIS или не задан ключ
        return jsonify({"error": "lookup_failed", "message": str(e)}), 502

    response = FindParkingResponse(parkings=[ParkingResult(**r) for r in results])
    return jsonify(response.model_dump())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
