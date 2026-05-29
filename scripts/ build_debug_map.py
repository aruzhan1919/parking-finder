"""
scripts/build_debug_map.py

Делает автономный HTML с картой 2GIS и всеми точками парковок —
данные встроены прямо в файл. Открываешь двойным кликом, никакого сервера.

Запуск:
    python -m scripts.build_debug_map
"""

import json
from pathlib import Path

# ВСТАВЬ СЮДА СВОЙ КЛЮЧ КАРТЫ (MapGL, тот же что в app.js):
MAPGL_KEY = "7cfbbf43-15e8-478c-a8e6-30237405fa48"


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Парковки Астаны — debug</title>
    <style>
        html, body { margin: 0; height: 100%; font-family: sans-serif; }
        #map { width: 100%; height: 100vh; }
        #info {
            position: absolute; top: 12px; left: 12px; z-index: 10;
            background: white; padding: 10px 14px; border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2); font-size: 14px;
        }
        #popup {
            position: absolute; bottom: 12px; left: 12px; right: 12px;
            max-width: 500px; background: white; padding: 12px 16px;
            border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            font-size: 13px; display: none; max-height: 40vh; overflow: auto;
        }
        #popup pre { white-space: pre-wrap; word-break: break-word; }
        #popup .close {
            float: right; cursor: pointer; font-size: 18px;
            color: #888; margin-left: 8px;
        }
    </style>
</head>
<body>
    <div id="info">Парковок на карте: <span id="count">…</span></div>
    <div id="map"></div>
    <div id="popup"></div>

    <script src="https://mapgl.2gis.com/api/js/v1"></script>
    <script>
        const MAPGL_KEY = "__KEY__";
        const PARKINGS = __DATA__;

        const map = new mapgl.Map('map', {
            center: [71.430, 51.128],
            zoom: 12,
            key: MAPGL_KEY,
        });

        const popup = document.getElementById('popup');
        document.getElementById('count').textContent = PARKINGS.length;

        PARKINGS.forEach(p => {
            if (!p.point) return;
            const marker = new mapgl.Marker(map, {
                coordinates: [p.point.lon, p.point.lat],
            });
            marker.on('click', () => {
                popup.style.display = 'block';
                popup.innerHTML =
                    '<span class="close" onclick="document.getElementById(\'popup\').style.display=\'none\'">×</span>' +
                    '<strong>' + (p.name || '(без названия)') + '</strong><br>' +
                    '<small>' + (p.address_name || '') + '</small>' +
                    '<pre>' + JSON.stringify(p, null, 2) + '</pre>';
            });
        });
    </script>
</body>
</html>
"""


def main():
    project_root = Path(__file__).resolve().parent.parent
    json_path = project_root / "data" / "parkings.json"
    if not json_path.exists():
        raise SystemExit(f"❌ Нет файла {json_path}. Сначала запусти fetch_parkings.")

    with json_path.open(encoding="utf-8") as f:
        parkings = json.load(f)

    if not MAPGL_KEY or MAPGL_KEY != "7cfbbf43-15e8-478c-a8e6-30237405fa48":
        raise SystemExit("❌ Впиши свой MAPGL_KEY в начале этого файла")

    html = HTML_TEMPLATE.replace("__KEY__", MAPGL_KEY).replace(
        "__DATA__", json.dumps(parkings, ensure_ascii=False)
    )

    out_path = project_root / "parkings_debug.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"✓ Готово: {out_path}")
    print(f"  Парковок встроено: {len(parkings)}")
    print(f"  Открой файл в браузере (двойной клик).")


if __name__ == "__main__":
    main()
