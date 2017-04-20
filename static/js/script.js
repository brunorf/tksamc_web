$(document).ready(function() {
  $('form#submit_job_form').submit(function(event) {
    // var formData = new FormData($(this)[0]);
    var data = {
      pH: 3,
    }
    $.post($(this).attr('action'), data ,function(data) {

    });
    return false;
  });
});
