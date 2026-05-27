// ===== Map initialization =====
const ASTANA_CENTER = [51.128, 71.430];

const map = L.map('map').setView(ASTANA_CENTER, 14);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
}).addTo(map);

// ===== State =====
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

// ===== Custom icons =====
function makeIcon(color) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background: ${color};
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
    });
}

const greenIcon = makeIcon('#16a34a');
const redIcon = makeIcon('#dc2626');
const orangeIcon = makeIcon('#f97316');

// ===== Map click handler =====
map.on('click', function(e) {
    const coords = [e.latlng.lat, e.latlng.lng];

    if (!startCoords) {
        startCoords = coords;
        startMarker = L.marker(coords, { icon: greenIcon })
            .addTo(map)
            .bindPopup('Start');
        startStatus.textContent = `${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}`;
    } else if (!destCoords) {
        destCoords = coords;
        destMarker = L.marker(coords, { icon: redIcon })
            .addTo(map)
            .bindPopup('Destination');
        destStatus.textContent = `${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}`;
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
                start: startCoords,
                dest: destCoords,
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
    // Clear previous parking markers
    parkingMarkers.forEach(m => map.removeLayer(m));
    parkingMarkers = [];

    // Add new markers
    parkings.forEach((p, idx) => {
        const marker = L.marker(p.coords, { icon: orangeIcon })
            .addTo(map)
            .bindPopup(`
                <strong>#${idx + 1} — ${p.id}</strong><br>
                Drive: ${Math.round(p.drive_time_sec / 60 * 10) / 10} min<br>
                Walk: ${Math.round(p.walk_time_sec / 60 * 10) / 10} min
            `);
        parkingMarkers.push(marker);
    });

    // Build sidebar list
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

    // Fit map to show all markers
    const allCoords = [startCoords, destCoords, ...parkings.map(p => p.coords)];
    map.fitBounds(allCoords, { padding: [50, 50] });
}

// ===== Reset =====
resetBtn.addEventListener('click', () => {
    if (startMarker) map.removeLayer(startMarker);
    if (destMarker) map.removeLayer(destMarker);
    parkingMarkers.forEach(m => map.removeLayer(m));

    startCoords = null;
    destCoords = null;
    startMarker = null;
    destMarker = null;
    parkingMarkers = [];

    startStatus.textContent = 'not set';
    destStatus.textContent = 'not set';
    resultsDiv.innerHTML = '';
    findBtn.disabled = true;

    map.setView(ASTANA_CENTER, 14);
});