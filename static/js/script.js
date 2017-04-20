$(document).ready(function() {
  $('form#submit_job_form').submit(function(event) {
    var form_data = new FormData();
    form_data.append('pH', $('input[name=pH]').val());
    form_data.append('temperature', $('input[name=temperature]').val());
    form_data.append('input_file', $('input[name=input_file]')[0].files[0]);
    // $.post($(this).attr('action'), form_data ,function(data) {
    //   alert(data);
    // });
    $.ajax({
      url: $(this).attr('action'),
      data: form_data,
      type: 'POST',
      contentType: false, // NEEDED, DON'T OMIT THIS (requires jQuery 1.6+)
      processData: false, // NEEDED, DON'T OMIT THIS
      success: function(data) {
        alert(data);
      },
    });
    return false;
  });
});
