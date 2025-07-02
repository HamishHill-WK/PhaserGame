// consent.js - moved from index.html

function toggleSubmit() {
    const consentYes = document.getElementById('consent-yes').checked;
    const dataYes = document.getElementById('data-yes').checked;
    const button = document.getElementById('agree-btn');
    // Enable button only if both consent questions are answered with "yes"
    button.disabled = !(consentYes && dataYes);
}

document.getElementById('agree-btn').addEventListener('click', function(event) {
    let consentYes = false;
    let dataYes = false;
    if (document.getElementById('consent-yes').checked){
        consentYes = true;
    }
    if (document.getElementById('data-yes').checked){
        dataYes = true;
    }
    if (!consentYes || !dataYes) {
        event.preventDefault();
        alert('You must consent to both participation and data collection to proceed with the study.');
    } 
});

// Set today's date as default

document.addEventListener('DOMContentLoaded', function() {
    const dateField = document.getElementById('date');
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    dateField.value = formattedDate;
});
