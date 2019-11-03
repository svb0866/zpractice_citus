

$("#administrative_note_form").hide();
$("#administrative_note_edit").click(function(){
  $("#administrative_note").hide();
  $("#administrative_note_form").show();
});


$("#printLink").click(function () {
  uuid = $(this).data('uuid');

  var options = {
  importCSS: true,
  importStyle: true,
  printContainer: true,
  pageTitle: $("#printTitle"+uuid).text(),

  };
  $("#printBody"+uuid).printThis(options);

});