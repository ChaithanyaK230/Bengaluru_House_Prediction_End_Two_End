const API_BASE = "http://127.0.0.1:8000";

window.onload = async function () {
    const response = await fetch(`${API_BASE}/locations`);
    const data = await response.json();

    const locationSelect = document.getElementById("location");

    data.locations.forEach(loc => {
        const option = document.createElement("option");
        option.value = loc;
        option.text = loc;
        locationSelect.appendChild(option);
    });
};

async function predictPrice() {
    const sqft = document.getElementById("sqft").value;
    const bath = document.getElementById("bath").value;
    const bhk = document.getElementById("bhk").value;
    const location = document.getElementById("location").value;

    const response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            total_sqft: parseFloat(sqft),
            bath: parseFloat(bath),
            bhk: parseInt(bhk),
            location: location
        })
    });

    const data = await response.json();

    document.getElementById("result").innerText =
        "Estimated Price: ₹ " + data.estimated_price + " Lakhs";
}
