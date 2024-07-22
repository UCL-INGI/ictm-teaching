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
    let column = $(this).data('column');
    let value = $(this).val().toLowerCase();
    $('table tbody tr').filter(function () {
        $(this).toggle($(this).find('td').eq(column).text().toLowerCase().indexOf(value) > -1);
    });
});

/*
$('#filterIcon').click(function () {
    $('#filterRow').toggle();
});
*/

/*
$('#filterRow input').on('keyup', function () {
    let column = $(this).data('column');
    let value = $(this).val().toLowerCase();
    $('table tbody tr').filter(function () {
        $(this).toggle($(this).find('td').eq(column).text().toLowerCase().indexOf(value) > -1);
    });
});
 */

