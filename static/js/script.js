$(document).ready(function() {
  $('form#submit_job_form').submit(function(event) {
    var form_data = new FormData();
    modal_body = $('#output .modal-body');
    close_button = $('#output button');
    modal_body.html('Please wait while your job is running...');
    // close_button.hide();
    $('#output').modal('show');


    form_data.append('pH', $('input[name=pH]').val());
    form_data.append('temperature', $('input[name=temperature]').val());
    form_data.append('input_file', $('input[name=input_file]')[0].files[0]);

    $.ajax({
      url: $(this).attr('action'),
      data: form_data,
      type: 'POST',
      contentType: false, // NEEDED, DON'T OMIT THIS (requires jQuery 1.6+)
      processData: false, // NEEDED, DON'T OMIT THIS
      success: function(data) {
        modal_body.html("Output file: <a href='" + data.job_dir + '/' + data.output + "' target='_blank'>" + data.output + "</a><br/><br/>" +
        "<img widht='332' height='249' src=" + data.job_dir + "/" + data.image + "><br/><br/>" +
        "<a data-toggle='collapse' href='#collapseExample' aria-expanded='false' aria-controls='collapseExample'>" +
        "Show script output" +
        "</a>" +
        "<div class='collapse' id='collapseExample'>" +
        "<div class='card card-block'>" +
        data.stdout +
        "</div>" +
        "</div>"
        );
        $('#output').modal('show');
        close_button.show();


      },
    });
    data = {"image":"Fig_MC_5vab_pH_3.4_T_20.0.jpg","job_dir":"jobs/2017-04-20_15:42:46:700784","output":"Output_MC_5vab_pH_3.4_T_20.0.dat","stdout":"klajsdlask"};



    return false;
  });
});
