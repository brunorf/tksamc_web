$(document).ready(function() {
  $('#pH_range').click(function() {
    $('#pH').prop('disabled', $('#pH_range').is(':checked'))
  })
});
