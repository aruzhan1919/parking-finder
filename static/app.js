// // ===== Map initialization =====
// const ASTANA_CENTER = [51.128, 71.430];

// const map = L.map('map').setView(ASTANA_CENTER, 14);

// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//     attribution: '© OpenStreetMap contributors',
// }).addTo(map);

// // ===== State =====
// let startCoords = null;
// let destCoords = null;
// let startMarker = null;
// let destMarker = null;
// let parkingMarkers = [];

// // ===== UI refs =====
// const findBtn = document.getElementById('find-btn');
// const resetBtn = document.getElementById('reset-btn');
// const startStatus = document.getElementById('start-status');
// const destStatus = document.getElementById('dest-status');
// const resultsDiv = document.getElementById('results');

// // ===== Custom icons =====
// function makeIcon(color) {
//     return L.divIcon({
//         className: 'custom-marker',
//         html: `<div style="
//             background: ${color};
//             width: 24px;
//             height: 24px;
//             border-radius: 50%;
//             border: 3px solid white;
//             box-shadow: 0 2px 6px rgba(0,0,0,0.3);
//         "></div>`,
//         iconSize: [24, 24],
//         iconAnchor: [12, 12],
//     });
// }

// const greenIcon = makeIcon('#16a34a');
// const redIcon = makeIcon('#dc2626');
// const orangeIcon = makeIcon('#f97316');

// // ===== Map click handler =====
// map.on('click', function(e) {
//     const coords = [e.latlng.lat, e.latlng.lng];

//     if (!startCoords) {
//         startCoords = coords;
//         startMarker = L.marker(coords, { icon: greenIcon })
//             .addTo(map)
//             .bindPopup('Start');
//         startStatus.textContent = `${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}`;
//     } else if (!destCoords) {
//         destCoords = coords;
//         destMarker = L.marker(coords, { icon: redIcon })
//             .addTo(map)
//             .bindPopup('Destination');
//         destStatus.textContent = `${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}`;
//         findBtn.disabled = false;
//     }
// });

// // ===== Find parking =====
// findBtn.addEventListener('click', async () => {
//     if (!startCoords || !destCoords) return;

//     resultsDiv.innerHTML = '<p class="loading">Searching for parking spots...</p>';
//     findBtn.disabled = true;

//     try {
//         const response = await fetch('/find-parking', {
//             method: 'POST',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify({
//                 start: startCoords,
//                 dest: destCoords,
//             }),
//         });

//         const data = await response.json();

//         if (!response.ok) {
//             resultsDiv.innerHTML = `<div class="error">Error: ${data.error || 'Unknown'}</div>`;
//             return;
//         }

//         renderResults(data.parkings);

//     } catch (err) {
//         resultsDiv.innerHTML = `<div class="error">Network error: ${err.message}</div>`;
//     } finally {
//         findBtn.disabled = false;
//     }
// });

// // ===== Render results =====
// function renderResults(parkings) {
//     // Clear previous parking markers
//     parkingMarkers.forEach(m => map.removeLayer(m));
//     parkingMarkers = [];

//     // Add new markers
//     parkings.forEach((p, idx) => {
//         const marker = L.marker(p.coords, { icon: orangeIcon })
//             .addTo(map)
//             .bindPopup(`
//                 <strong>#${idx + 1} — ${p.id}</strong><br>
//                 Drive: ${Math.round(p.drive_time_sec / 60 * 10) / 10} min<br>
//                 Walk: ${Math.round(p.walk_time_sec / 60 * 10) / 10} min
//             `);
//         parkingMarkers.push(marker);
//     });

//     // Build sidebar list
//     resultsDiv.innerHTML = '<h3 style="margin-bottom:8px; font-size:15px;">Top 3 parkings:</h3>' +
//         parkings.map((p, idx) => {
//             const driveMin = (p.drive_time_sec / 60).toFixed(1);
//             const walkMin = (p.walk_time_sec / 60).toFixed(1);
//             const totalMin = ((p.drive_time_sec + p.walk_time_sec) / 60).toFixed(1);
//             return `
//                 <div class="result-card">
//                     <span class="rank">#${idx + 1}</span>
//                     <strong>${p.id}</strong>
//                     <div class="times">
//                         🚗 ${driveMin} min · 🚶 ${walkMin} min · ⏱️ total ${totalMin} min
//                     </div>
//                 </div>
//             `;
//         }).join('');

//     // Fit map to show all markers
//     const allCoords = [startCoords, destCoords, ...parkings.map(p => p.coords)];
//     map.fitBounds(allCoords, { padding: [50, 50] });
// }

// // ===== Reset =====
// resetBtn.addEventListener('click', () => {
//     if (startMarker) map.removeLayer(startMarker);
//     if (destMarker) map.removeLayer(destMarker);
//     parkingMarkers.forEach(m => map.removeLayer(m));

//     startCoords = null;
//     destCoords = null;
//     startMarker = null;
//     destMarker = null;
//     parkingMarkers = [];

//     startStatus.textContent = 'not set';
//     destStatus.textContent = 'not set';
//     resultsDiv.innerHTML = '';
//     findBtn.disabled = true;

//     map.setView(ASTANA_CENTER, 14);
// });

// ===== 2GIS MapGL =====
// ВСТАВЬ СЮДА СВОЙ КЛЮЧ КАРТЫ (MapGL JS API):
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

    // новые маркеры (p.coords приходит как [lat, lon] -> для карты [lng, lat])
    parkings.forEach((p) => {
        const lngLat = [p.coords[1], p.coords[0]];
        const marker = makeMarker(lngLat, '#f97316');
        parkingMarkers.push(marker);
    });

    // список в сайдбаре
    resultsDiv.innerHTML = '<h3 style="margin-bottom:8px; font-size:15px;">Top 3 parkings:</h3>' +
        parkings.map((p, idx) => {
            const driveMin = (p.drive_time_sec / 60).toFixed(1);
            const walkMin = (p.walk_time_sec / 60).toFixed(1);
            const totalMin = ((p.drive_time_sec + p.walk_time_sec) / 60).toFixed(1);
            return `
                <div class="result-card">
                    <span class="rank">#${idx + 1}</span>
                    <strong>${p.id}</strong>
                    <div class="times">
                        🚗 ${driveMin} min · 🚶 ${walkMin} min · ⏱️ total ${totalMin} min
                    </div>
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