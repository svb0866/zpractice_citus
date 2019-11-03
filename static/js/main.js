
$('[data-toggle="datepicker"]').datepicker({
    format: 'yyyy-mm-dd',
    autoHide: true,
});

$('.timepicker').timepicker({
    timeFormat: 'h:mm p',
    interval: 15,
    defaultTime: '6:00am',
    dynamic: true,
    dropdown: true,
    scrollbar: true
});

$('input').attr('autocomplete','off');