$(document).ready(function() {
  $('#id_ph_range').click(function() {
    $('#id_ph').prop('readonly', $('#id_ph_range').is(':checked'))
  })
});
