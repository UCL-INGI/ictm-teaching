// Utility function to send an AJAX POST request
function sendPostRequest(url, data, successCallback, errorCallback) {
    console.log('Sending POST request to:', url);
    console.log('Data:', data);
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success: successCallback,
        error: errorCallback
    });
}

// Function to handle the change event of the yearSelect dropdown
function handleYearSelectChange(params) {
    $('#yearSelect').change(function() {
        params.selected_year = $(this).val();
        let updatedUrl = "/config/update_current_year";

        console.log("updateCurrentYearUrl:", updatedUrl);
        console.log('Params:', params);

        sendPostRequest(
            updatedUrl,
            params,
            function(response) {
                window.location.href = response;
            },
            function(error) {
                console.error('Error updating the year:', error);
            }
        );
    });
}

// Initialization function to set up event handlers
function initializeHandlers() {
    handleYearSelectChange();
}

// Expose the initializeHandlers function to be called from HTML
// window.initializeHandlers = initializeHandlers;
