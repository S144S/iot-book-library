$(document).ready(function() {
    $('#date').persianDatepicker({
        format: 'YYYY/MM/DD',
        onSelect: function (unixDate) {
            sendReservationData();
        }
    });

    firstInit();

    $('#time').on('change', function() {
        sendReservationData();
    });


    function firstInit() {
        sendReservationData();
    }


    function sendReservationData() {
        resetTableSelection();

        let date = $('#date').val();
        let time = $('#time').val();

        if (date && time) {  // Ensure both fields are selected before sending
            $.ajax({
                url: '/check-table',
                type: 'POST',
                contentType: 'application/json',  // Set content type to JSON
                data: JSON.stringify({ date: date, time: time }),  // Send data as JSON
                success: function(response) {
                    updateTableAvailability(response);
                },
                error: function(error) {
                    console.log('Error sending reservation data:', error);
                }
            });
        }
    }


    function updateTableAvailability(data) {
        if (data.table1 === true) {
            $('#table1').removeClass('reserved').addClass('pointer-cursor').addClass('available-table');
        } else {
            $('#table1').removeClass('available-table').removeClass('pointer-cursor').addClass('reserved');
        }
        
        if (data.table2 === true) {
            $('#table2').removeClass('reserved').addClass('pointer-cursor').addClass('available-table');
        } else {
            $('#table2').removeClass('available-table').removeClass('pointer-cursor').addClass('reserved');
        }

        if (data.table3 === true) {
            $('#table3').removeClass('reserved').addClass('pointer-cursor').addClass('available-table');
        } else {
            $('#table3').removeClass('available-table').removeClass('pointer-cursor').addClass('reserved');
        }

        if (data.table4 === true) {
            $('#table4').removeClass('reserved').addClass('pointer-cursor').addClass('available-table');
        } else {
            $('#table4').removeClass('available-table').removeClass('pointer-cursor').addClass('reserved');
        }
    }

    const tables = document.querySelectorAll('.available-table');
    tables.forEach(function(table) {
        table.addEventListener('click', function() {
            selectTable(table);
        });
    });

    function selectTable(table) {
        if ($(table).hasClass('reserved')) return;
        const allTables = document.querySelectorAll('.available-table');
        allTables.forEach(function(t) {
            $(t).removeClass('selected-table');
        });
        if ($(table).hasClass('available-table') && !$(table).hasClass('selected-table')) {
            $(table).addClass('selected-table');
        }
        $('#reservation-message').text('');
        $('#reservation-success-message').text('');
    }

    function resetTableSelection() {
        const allTables = document.querySelectorAll('.available-table');
        allTables.forEach(function(t) {
            $(t).removeClass('selected-table');
        });
        $('#reservation-message').text('');
        $('#reservation-success-message').text('');
    }

    $('#reserve-btn').on('click', function() {
        const selectedTable = $('.selected-table');
        if (selectedTable.length === 0) {
            $('#reservation-message').text('لطفا یک میز را انتخاب کنید.');
            return;
        }
        let date = $('#date').val();
        let time = $('#time').val();
        let tableId = selectedTable.attr('id');
        $.ajax({
            url: 'reserve',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ date: date, time: time, tableId: tableId }),
            success: function(response) {
                $('#reservation-success-message').text(response.message);
            },
            error: function(error) {
                $('#reservation-message').text('خطایی در رزرو میز رخ داد! لطفا با پشنیبانی تماس بگیرید.');
            }
        });
    });
});

