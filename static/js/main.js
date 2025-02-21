// Enable tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

// Form validation
document.addEventListener('submit', function(event) {
    if (!event.target.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
    }
    event.target.classList.add('was-validated');
}, false);
