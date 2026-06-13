
const menuButton = document.getElementById("menuButton");
const navLinks = document.getElementById("navLinks");

if (menuButton) {
    menuButton.addEventListener("click", function () {
        navLinks.classList.toggle("show");
    });
}

function calculateFare(distance, passengers) {
    const baseFare = 30;
    const perKmRate = 18;
    let extraPassengerCharge = 0;

    if (passengers > 1) {
        extraPassengerCharge = (passengers - 1) * 10;
    }

    const totalFare = baseFare + (distance * perKmRate) + extraPassengerCharge;
    return Math.round(totalFare);
}

function updateBookingFarePreview() {
    const distanceInput = document.getElementById("distanceKm");
    const passengerInput = document.getElementById("passengerCount");
    const farePreview = document.getElementById("farePreview");

    if (!distanceInput || !passengerInput || !farePreview) {
        return;
    }

    const distance = parseFloat(distanceInput.value) || 0;
    const passengers = parseInt(passengerInput.value) || 1;
    const fare = calculateFare(distance, passengers);

    farePreview.textContent = "৳" + fare;
}

const distanceKm = document.getElementById("distanceKm");
const passengerCount = document.getElementById("passengerCount");

if (distanceKm && passengerCount) {
    distanceKm.addEventListener("input", updateBookingFarePreview);
    passengerCount.addEventListener("input", updateBookingFarePreview);
    updateBookingFarePreview();
}

function quickFareEstimate() {
    const distance = parseFloat(document.getElementById("quickDistance").value) || 0;
    const passengers = parseInt(document.getElementById("quickPassengers").value) || 1;
    const fare = calculateFare(distance, passengers);
    document.getElementById("quickFareResult").textContent = "Estimated fare: ৳" + fare;
}


window.quickFareEstimate = quickFareEstimate;
