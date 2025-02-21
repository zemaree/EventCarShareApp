// Enable tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Get all forms that need validation
    var forms = document.querySelectorAll('.needs-validation')

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            form.classList.add('was-validated')
        }, false)
    });

    // Handle modal reset on close
    var modals = document.querySelectorAll('.modal')
    modals.forEach(function(modal) {
        modal.addEventListener('hidden.bs.modal', function () {
            var forms = this.querySelectorAll('form')
            forms.forEach(function(form) {
                form.reset()
                form.classList.remove('was-validated')
            })
        })
    })
});