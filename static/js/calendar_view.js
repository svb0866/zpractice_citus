

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        eventClick: function(info) {

            $.get("api/"+info.event.id, function(data){
                $("#client").text(data['client']).attr("href",data['client_url']);
                $("#appointment_datetime").text(data['appointment_datetime']);
                $("#appointment_reason").text(data['appointment_reason']);
                $("#assigned_to").text(data['assigned_to']);
                $("#edit_appointment").attr("href","update"+"/"+data['uuid']+"/");

                $("#show").attr("href",data['show_url']);
                $("#no_show").attr("href",data['no_show_url']);
                $("#scheduled").attr("href",data['scheduled_url']);
                $("#canceled").attr("href",data['canceled_url']);
                $("#late_canceled").attr("href",data['late_canceled_url']);
                console.log(data['appointment_datetime'])
                });

            $('#modalCenter').modal();

        },

        height: 500,
        plugins: [ 'dayGrid','timeGrid', ],
        defaultView: 'dayGridMonth',
        header: {
                left: 'prev, today, next',
                center: 'title',
                right: 'timeGrid, dayGridMonth'
            },
        buttonText:{
            today: 'Today',
            month: 'Month',
            week: 'Week',
            day: 'Day',
            list: 'List',
        },
        eventSources: [
            // your event source
            {
              url: '/appointments/api/list/',
              method: 'GET',
              extraParams: {
                custom_param2: 'poin'
              },
              failure: function() {
                alert('there was an error while fetching events!');
              },}],
         eventLimit: true, // for all non-TimeGrid views
          views: {
            dayGridMonth: {
              eventLimit: 5 // adjust to 6 only for timeGridWeek/timeGridDay
            }
          },

    });

    calendar.render();

    $(".fc-timeGrid-button").html("Day");

    var selection = document.getElementById("selection");
    selection.onchange = function() {
    console.log(selection.value);
    console.log(calendar.getEventSources());
    calendar.getEventSources()[0].remove();
    if (selection.value !== 'All Appointments'){
    calendar.addEventSource(
        {
              url: '/appointments/api/list/'+selection.value+"/",
              method: 'GET',
              extraParams: {
              },
              failure: function() {
                alert('there was an error while fetching events!');
              },

    });} else {
        calendar.addEventSource(
        {
              url: '/appointments/api/list/',
              method: 'GET',
              extraParams: {
              },
              failure: function() {
                alert('there was an error while fetching events!');
              },

    });
    }};
});


