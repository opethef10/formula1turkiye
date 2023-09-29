function setLanguage(button, languageCode) {
    var languageForm = document.querySelector('.form-inline');
    var languageInput = document.createElement('input');
    languageInput.type = 'hidden';
    languageInput.name = 'language';
    languageInput.value = languageCode;

    // Check if the button is disabled before submitting the form
    if (!button.hasAttribute('disabled')) {
        languageForm.appendChild(languageInput);
        languageForm.submit();
    }
}
