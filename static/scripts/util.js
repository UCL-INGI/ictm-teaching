// Utility function to send an AJAX POST request

function sendPostRequest(url, data, successCallback, errorCallback) {
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success: successCallback,
        error: errorCallback
    });
}

// Function to handle the change event of the yearSelect dropdown
function handleYearSelectChange() {
    $('#yearSelect').change(function () {
        window.location.href = $(this).find(':selected').data("redirect");
    });
}

function addBadge(selectElement, containerSelector) {
    var selectedOption = $(selectElement).find('option:selected');
    var selectedValue = selectedOption.val();
    var selectedText = selectedOption.text();

    if (selectedValue) {
        // Check if the organization is already added

        var alreadyExists = $(containerSelector).find('div[data-id="' + selectedValue + '"]').length > 0;

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
        }
        // Reset the select input
        $(selectElement).val('');
    }
}

function changeBadgeColorCheckbox(checkboxValue) {
    const badge = $('span.badge', checkboxValue.parent());
    if (checkboxValue.is(':checked')) {
        badge.removeClass('bg-secondary').addClass('bg-primary');
    } else {
        badge.removeClass('bg-primary').addClass('bg-secondary');
    }
}

function filter(page) {
    let activeOrganizations = $('.badge-checkbox:checked').map(function () {
        return $(this).data('id');
    }).get();

    let items;
    if (page === "course") {
        items = $('.course-item')
    } else if (page === "user") {
        items = $('.user-item')
    }

    if (activeOrganizations.length > 0) {
        items.each(function () {
            let organizations;
            let showItem;

            if (page === "course") {
                organizations = $(this).data('organizations').toString().split(',');
                showItem = activeOrganizations.some(org => organizations.includes(org.toString()));
            }
            else if (page === "user") {
                organizations = $(this).data('organizations');
                showItem = activeOrganizations.includes(organizations);
            }

            if (showItem) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    } else {
        // If no organization is selected, hide all courses
        items.hide();
    }
}

// Event listener for removing the organization tag
$(document).on('click', '.remove-tag', function (e) {
    e.preventDefault();
    $(this).parent('.badge').remove();
});

$(document).on('click', '#filterIcon', function (e) {
    e.preventDefault();
    $('#filterRow').toggle();
});

$(document).on('keyup', '#filterRow input', function () {
    // Get the index of the column from the data-column attribute of the input
    let column = $(this).data('column');

    // Get the value entered in the input and convert it to lowercase
    let value = $(this).val().toLowerCase();

    // Iterate through each row in the table body
    $('table tbody tr').each(function () {
        // Get the text content of the cell at the specified column index and convert it to lowercase
        let cellText = $(this).find('td').eq(column).text().toLowerCase();

        // Check if the cell text contains the searched value
        let containsValue = cellText.indexOf(value) > -1;

        // Show or hide the row based on whether the cell text contains the searched value
        $(this).toggle(containsValue);
    });
});