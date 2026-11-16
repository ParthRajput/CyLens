async function  loadThreats() {
    const container = document.getElementById("threat-container");

    try {
        const response = await fetch("/api/threats");

        if (!response.ok) {
            throw new Error("Failed to load threats");
        }

        const threats = await response.json();
        plotThreatsOnMap(threats);
        updateAnalytics(threats);
        
        // Calculate dashboard statistics
        const totalThreats = threats.length;

        const highRiskThreats = threats.filter(
            (threat) => 
                threat.severity === "High"  ||
            threat.severity === "Critical"
).length;

        const countries = new Set(
            threats
                .map((threat) => threat.source_country)
                .filter((country) => country)
        );

        const dataSources = new Set(
            threats
                .map((threat) => threat.data_source)
                .filter((source) => source)
        );

        document.getElementById("total-threats").textContent = totalThreats;
        document.getElementById("high-risk-threats").textContent = highRiskThreats;
        document.getElementById("countries-count").textContent = countries.size;
        document.getElementById("sources-count").textContent = dataSources.size;

        container.innerHTML = "";

        if (threats.length == 0) {
            container.innerHTML = "<p>No threats found.</p>";
            return;
        }

        threats.forEach((threat) => {
            const threatCard = document.createElement("div");

            threatCard.classList.add("threat-card");

            threatCard.innerHTML = `
            <h3>${threat.threat_type}</h3>
            <p><strong>Severity:</strong> ${threat.severity}</p>
            <p><strong>Source IP:</strong> ${threat.source_ip}</p>
            <p><strong>Country:</strong> ${threat.source_country}</p>
            <p><strong>Confidence:</strong> ${threat.confidence_score}%</p>
            <p>${threat.description}</p>
            `;

            container.appendChild(threatCard);
        });
    } catch (error) {
        console.error("Error loading threats:", error);

        container.innerHTML = "<p>Unable to load threat data. Please try again later.</p>";
    }
}

let threatMap;

function initialiseThreatMap() {
    threatMap = L.map("threat-map", {
        worldCopyJump: false,
        minZoom: 2,
        maxZoom: 18,
    }).setView([20, 0], 2);

L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    {
        attribution: "&copy; Esri and its contributors",
        maxZoom: 18,
        noWrap: true,
        bounds: [[-85.0511, -180], [85.0511, 180]],
        className: "dark-map-tiles"
    }
).addTo(threatMap);
}

const countryCoordinates = {
    US: [39.8283, -98.5795],
    GB: [55.3781, -3.4360],
    IN: [20.5937, 78.9629],
    DE: [51.1657, 10.4515],
    FR: [46.2276, 2.2137],
    CN: [35.8617, 104.1954],
    JP: [36.2048, 138.2529],
    AU: [-25.2744, 133.7751],
    CA: [56.1304, -106.3468],
    BR: [-14.2350, -51.9253],

    // Additional countries from AbuseIPDB
    KR: [35.9078, 127.7669],
    NL: [52.1326, 5.2913],
    HK: [22.3193, 114.1694],
    RS: [44.0165, 21.0059],
    MX: [23.6345, -102.5528],
    CL: [-35.6751, -71.5430],
    VN: [14.0583, 108.2772]
};

function plotThreatsOnMap(threats) {
    //Remove markers from the previous refresh
    if (threatMap.threatMarkers) {
        threatMap.removeLayer(threatMap.threatMarkers);
    }

    threatMap.threatMarkers = L.layerGroup().addTo(threatMap);

    threats.forEach((threat) => {
        const countryCode = (threat.source_country || "").toUpperCase();
        const coordinates = countryCoordinates[countryCode];

        if (!coordinates) {
            return;
        }

        const severity = (threat.severity || "Unknown").toLowerCase();

        let markerColor;

        switch (severity) {
            case "critical":
            case "high":
                markerColor = "#ef4444"; // Red
                break;

            case "medium":
                markerColor = "#f97316";
                break;

            case "low":
                markerColor = "#3b82f6";
                break;

            default:
                markerColor = "#9ca3af"; // Grey
        }

        const marker = L.circleMarker(coordinates, {
            radius: 8,
            color: markerColor,
            fillColor: markerColor,
            fillOpacity: 0.85,
            weight: 2
        });

        marker.bindPopup(`
            <strong>${threat.threat_type || "Threat record"}</strong><br>
            Country: ${countryCode}<br>
            Source IP: ${threat.source_ip || "Unknown"}<br>
            Severity: ${threat.severity || "Unknown"}<br>
            Confidence: ${threat.confidence_score ?? "Unknown"}%<br>
            Data source: ${threat.data_source || "Unknown"}<br>
        `);

        marker.addTo(threatMap.threatMarkers);
    });
}
function addThreatLegend() {
    const legend = L.control({position: "bottomleft"});

    legend.onAdd = function () {
        const div = L.DomUtil.create("div", "threat-legend");

        div.innerHTML = `
                     <h4>THREAT SEVERITY</h4>

            <div class="legend-item">
                <span class="legend-dot critical"></span>
                Critical / High
            </div>

            <div class="legend-item">
                <span class="legend-dot medium"></span>
                Medium
            </div>

            <div class="legend-item">
                <span class="legend-dot low"></span>
                Low
            </div>

            <div class="legend-item">
                <span class="legend-dot unknown"></span>
                Unknown
            </div>
        `;

        return div;
    };
    legend.addTo(threatMap);
}

initialiseThreatMap();
addThreatLegend();
loadThreats();

let severityChart;
let countryChart;

function updateAnalytics(threats) {
    // Count threats by severity
    const severityCounts = {};

    threats.forEach((threat) => {
        const severity = threat.severity || "Unknown";

        severityCounts[severity] = (severityCounts[severity] || 0) + 1;
    });

    // Count threats by country
    const countryCounts = {};

    threats.forEach((threat) => {
        const country = threat.source_country || "Unknown";

        countryCounts[country] = (countryCounts[country] || 0) + 1;
    });

    // Sort countries by threat count and show the top 8
    const topCountries = Object.entries(countryCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);

    // Remove previous charts before refreshing
    if (severityChart) {
        severityChart.destroy();
    }

    if (countryChart) {
        countryChart.destroy();
    }

    // Severity doughnut chart
    severityChart = new Chart(
        document.getElementById("severity-chart"),
        {
            type: "doughnut",
            data: {
                labels: Object.keys(severityCounts),
                datasets: [{
                    data: Object.values(severityCounts),
                    backgroundColor: [
                        "#ef4444",
                        "#f97316",
                        "#3b82f6",
                        "#22c55e",
                        "#9ca3af"
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        }
    );

    // Country bar chart
    countryChart = new Chart(
        document.getElementById("country-chart"),
        {
            type: "bar",
            data: {
                labels: topCountries.map(([country]) => country),
                datasets: [{
                    label: "Threat Records",
                    data: topCountries.map(([, count]) => count),
                    backgroundColor: "#3b82f6",
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        }
    );
}