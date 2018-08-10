$(document).ready(function () {
  $('#id_ph_range').click(function () {
    $('#id_ph').prop('readonly', $('#id_ph_range').is(':checked'))
  });


  $('#id_pdb_file').change(function (event) {
    checkPDBChains(event.target);
  });

  $('#id_pdb_search').focus(function () {
    $(this).parent().removeClass('has-error');
    $(this).val('');
  });

  $('#id_pdb_search').change(function (event) {
    checkPDBChains(event.target);
  });
});


function validate() {
  var search = $('#id_pdb_search').val();
  var file = $('#id_pdb_file').val();
  if (!search && !file) {
    alertify.alert("Please, fill out PDB File or RCSB PDB Search fields");
    return false;
  }
}

function checkPDBChains(target) {
  $.LoadingOverlay('show');

  var form = new FormData();
  var csrftoken = $('[name=csrfmiddlewaretoken]').val();
  $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
    if (options['type'].toLowerCase() === 'post') {
      jqXHR.setRequestHeader('X-CSRFToken', csrftoken);
    }
  });
  // user has uploaded a file
  if (target.files) {
    form.append('pdb_file', target.files[0]);
  }
  else {
    form.append('pdb_search', target.value);
  }

  return $.ajax({
    url: '/process_input_pdb',
    data: form,
    processData: false,
    contentType: false,
    type: 'POST',
    success: showChains
  })
    .fail(function () {
      if (!target.files) {
        $('#id_pdb_search').parent().addClass('has-error');
        alertify.alert("Couldn't find any results for " + '"' + target.value + '"');
      }
    })
    .always(function () {
      $.LoadingOverlay('hide');
    });

}

function showChains(data) {
  $('#id_chain').empty();
  data.chains.forEach((chain, i) => {
    $('#id_chain').append(
      '<option value="' + chain + '">' + chain + '</option>'
    );
  });
  $('#div_chain').show();
}