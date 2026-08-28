async function  loadThreats() {
    const container = document.getElementById("threat-container");

    try {
        const response = await fetch("/api/threats");

        if (!response.ok) {
            throw new Error("Failed to load threats");
        }

        const threats = await response.json();

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

loadThreats();