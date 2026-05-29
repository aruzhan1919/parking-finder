const MAPGL_KEY = "7cfbbf43-15e8-478c-a8e6-30237405fa48";

// MapGL хранит координаты как [lng, lat] — наоборот от бэкенда (lat, lon)!
const ASTANA_CENTER = [71.430, 51.128]; // [lng, lat]

const map = new mapgl.Map('map', {
    center: ASTANA_CENTER,
    zoom: 14,
    key: MAPGL_KEY,
});

// ===== State (всё храним как [lng, lat]) =====
let startCoords = null;
let destCoords = null;
let startMarker = null;
let destMarker = null;
let parkingMarkers = [];

// ===== UI refs =====
const findBtn = document.getElementById('find-btn');
const resetBtn = document.getElementById('reset-btn');
const startStatus = document.getElementById('start-status');
const destStatus = document.getElementById('dest-status');
const resultsDiv = document.getElementById('results');

// ===== Маркер с цветом (рисуем кружок через HtmlMarker) =====
function makeMarker(lngLat, color) {
    return new mapgl.HtmlMarker(map, {
        coordinates: lngLat,
        html: `<div style="
            background: ${color};
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        "></div>`,
        anchor: [12, 12],
    });
}

// ===== Клик по карте =====
map.on('click', function (e) {
    const lngLat = e.lngLat; // [lng, lat]

    if (!startCoords) {
        startCoords = lngLat;
        startMarker = makeMarker(lngLat, '#16a34a');
        // показываем как lat, lon — привычный для человека порядок
        startStatus.textContent = `${lngLat[1].toFixed(4)}, ${lngLat[0].toFixed(4)}`;
    } else if (!destCoords) {
        destCoords = lngLat;
        destMarker = makeMarker(lngLat, '#dc2626');
        destStatus.textContent = `${lngLat[1].toFixed(4)}, ${lngLat[0].toFixed(4)}`;
        findBtn.disabled = false;
    }
});

// ===== Find parking =====
findBtn.addEventListener('click', async () => {
    if (!startCoords || !destCoords) return;

    resultsDiv.innerHTML = '<p class="loading">Searching for parking spots...</p>';
    findBtn.disabled = true;

    try {
        const response = await fetch('/find-parking', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                // бэкенд хочет [lat, lon] — переворачиваем
                start: [startCoords[1], startCoords[0]],
                dest: [destCoords[1], destCoords[0]],
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            resultsDiv.innerHTML = `<div class="error">Error: ${data.error || 'Unknown'}</div>`;
            return;
        }

        renderResults(data.parkings);

    } catch (err) {
        resultsDiv.innerHTML = `<div class="error">Network error: ${err.message}</div>`;
    } finally {
        findBtn.disabled = false;
    }
});

// ===== Render results =====
function renderResults(parkings) {
    // убираем старые маркеры парковок
    parkingMarkers.forEach(m => m.destroy());
    parkingMarkers = [];

    // новые маркеры с номерами (p.coords приходит как [lat, lon] -> [lng, lat])
    parkings.forEach((p, idx) => {
        const lngLat = [p.coords[1], p.coords[0]];
        const marker = new mapgl.HtmlMarker(map, {
            coordinates: lngLat,
            html: `<div style="
                background: #f97316;
                color: white;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                border: 3px solid white;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 14px;
                font-family: sans-serif;
            ">${idx + 1}</div>`,
            anchor: [14, 14],
        });
        parkingMarkers.push(marker);
    });

    if (!parkings.length) {
        resultsDiv.innerHTML = '<p class="error">Парковок рядом не найдено. Попробуй другую точку.</p>';
        return;
    }

    // список в сайдбаре
    resultsDiv.innerHTML = '<h3 style="margin-bottom:8px; font-size:15px;">Топ-5 парковок:</h3>' +
        parkings.map((p, idx) => {
            const driveMin = (p.drive_time_sec / 60).toFixed(1);
            const walkMin = (p.walk_time_sec / 60).toFixed(1);
            const totalMin = ((p.drive_time_sec + p.walk_time_sec) / 60).toFixed(1);

            const price = p.price ? `💰 ${p.price}` : '💰 н/д';
            const capacity = p.capacity ? `🅿️ ${p.capacity} мест` : '';
            const tags = (p.tags && p.tags.length)
                ? `<div class="tags">${p.tags.join(' · ')}</div>` : '';
            const addr = p.address ? `<div class="addr">${p.address}</div>` : '';

            return `
                <div class="result-card">
                    <span class="rank">#${idx + 1}</span>
                    <strong>${p.name}</strong>
                    ${addr}
                    <div class="times">
                        🚗 ${driveMin} мин · 🚶 ${walkMin} мин · ⏱️ ${totalMin} мин
                    </div>
                    <div class="meta">${price}${capacity ? ' · ' + capacity : ''}</div>
                    ${tags}
                </div>
            `;
        }).join('');
}

// ===== Reset =====
resetBtn.addEventListener('click', () => {
    if (startMarker) startMarker.destroy();
    if (destMarker) destMarker.destroy();
    parkingMarkers.forEach(m => m.destroy());

    startCoords = null;
    destCoords = null;
    startMarker = null;
    destMarker = null;
    parkingMarkers = [];

    startStatus.textContent = 'not set';
    destStatus.textContent = 'not set';
    resultsDiv.innerHTML = '';
    findBtn.disabled = true;

    map.setCenter(ASTANA_CENTER);
    map.setZoom(14);
});