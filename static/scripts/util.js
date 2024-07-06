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
    $('#yearSelect').change(function () {
        params.selected_year = $(this).val();
        let updatedUrl = "/config/update_current_year";

        console.log("updateCurrentYearUrl:", updatedUrl);
        console.log('Params:', params);

        sendPostRequest(
            updatedUrl,
            params,
            function (response) {
                window.location.href = response;
            },
            function (error) {
                console.error('Error updating the year:', error);
            }
        );
    });
}

function addBadge(selectElement, containerSelector) {
    var selectedOption = $(selectElement).find('option:selected');
    var selectedValue = selectedOption.val();
    var selectedText = selectedOption.text();

    console.log("Selected value:", selectedValue);
    console.log("Selected text:", selectedText);

    if (selectedValue) {
        // Check if the organization is already added

        var alreadyExists = $(containerSelector).find('div[data-id="' + selectedValue + '"]').length > 0;

        console.log("Already exists:", alreadyExists)

        if (!alreadyExists) {
            var tagHtml = $('<div>', {
                class: 'badge bg-primary d-inline-block',
                'data-id': selectedValue
            });

            $(tagHtml).text(selectedText);
            $('<a>', {
                href: '#',
                class: 'remove-tag ms-1',
                html: '&times;'
            }).appendTo(tagHtml);
            $('<input>', {
                type: 'hidden',
                name: 'organization_code[]',
                value: selectedValue
            }).appendTo(tagHtml);

            $(containerSelector).append(tagHtml);
            console.log("Badge added:", tagHtml);
        } else {
            console.log("Organization already added:", selectedText);
        }

        // Reset the select input
        $(selectElement).val('');

        console.log("Container content after adding badge:", $(containerSelector).html());
    }
}

// Event listener for removing the organization tag
$(document).on('click', '.remove-tag', function (e) {
    e.preventDefault();
    $(this).parent('.badge').remove();
    console.log("Tag removed");
});

