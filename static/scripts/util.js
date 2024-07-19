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
function handleYearSelectChange(params) {
    $('#yearSelect').change(function () {
        const selectedYear = $(this).val();
        window.location.href = params.current_endpoint.replace('/0', `/${selectedYear}`);
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
                organizations = $(this).data('organizations').split(',');
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


