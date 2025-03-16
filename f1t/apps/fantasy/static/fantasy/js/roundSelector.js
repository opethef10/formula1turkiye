// Get the select elements
const fromRoundSelect = document.getElementById('fromRound');
const toRoundSelect = document.getElementById('toRound');

// Function to filter 'to_round' options based on the selected 'from_round'
function filterToRoundOptions() {
    const fromRoundValue = parseInt(fromRoundSelect.value, 10);

    let selectedToRoundValue = parseInt(toRoundSelect.value, 10);
    let firstValidOptionValue = null;

    // Loop through each option in the 'to_round' dropdown
    Array.from(toRoundSelect.options).forEach(option => {
        const toRoundValue = parseInt(option.value, 10);

        if (toRoundValue < fromRoundValue) {
            option.style.display = 'none'; // Hide options with value less than from_round
        } else {
            option.style.display = 'block'; // Show options with value greater or equal to from_round

            // Set the first valid option (that is greater than or equal to from_round)
            if (!firstValidOptionValue) {
                firstValidOptionValue = toRoundValue;
            }
        }

        // If the selected value is hidden, clear the selection
        if (selectedToRoundValue === toRoundValue && option.style.display === 'none') {
            toRoundSelect.value = firstValidOptionValue; // Reset to the first valid option
        }
    });
}

// Initial filtering when the page loads
filterToRoundOptions();

// Add an event listener to update 'to_round' options when 'from_round' changes
fromRoundSelect.addEventListener('change', filterToRoundOptions);
