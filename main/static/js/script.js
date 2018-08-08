$(document).ready(function () {
  $('#id_ph_range').click(function () {
    $('#id_ph').prop('readonly', $('#id_ph_range').is(':checked'))
  });

  $('#id_pdb_search').focus(function () {
    $(this).parent().removeClass('has-error');
    $(this).val('');
  });
  $('#id_pdb_search').change(function () {
    $.LoadingOverlay('show');

    var pdb_search = $(this).val();
    var csrftoken = $('[name=csrfmiddlewaretoken]').val();
    $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
      if (options['type'].toLowerCase() === 'post') {
        jqXHR.setRequestHeader('X-CSRFToken', csrftoken);
      }
    });

    $.post({
      url: '/process_input_pdb',
      data: {
        'pdb_search': pdb_search
      },
      dataType: 'json',
      success: function (data) {
        $('#id_chains').empty();
        data.chains.forEach((chain, i) => {
          $('#id_chains').append(
            '<li><label for="id_chains_' + i + '"><input type="checkbox" name="chains" value="' + chain + '" class="form-check" id="id_chains_' + i + '">' + chain + '</label></li>'
          );
        });
        $('#div_chains').show();
      }
    }).
      fail(function () {
        $('#id_pdb_search').parent().addClass('has-error');
        alertify.alert("Couldn't find any results for " + '"' + pdb_search + '"');
      })
      .always(function () {
        $.LoadingOverlay('hide');
      });
  });
});
