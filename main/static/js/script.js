$(document).ready(function() {
  $('#id_ph_range').click(function() {
    $('#id_ph').prop('disabled', $('#id_ph_range').is(':checked'))
  })
});
