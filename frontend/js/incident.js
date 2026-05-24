document.getElementById('new-incident-form').addEventListener('submit', function(event) {
    event.preventDefault();
    alert('New incident added successfully!');
    // Add logic to save new incident to database
});

document.getElementById('old-incident-form').addEventListener('submit', function(event) {
    event.preventDefault();
    alert('Old incident updated successfully!');
    // Add logic to update old incident in database
});
