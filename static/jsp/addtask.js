$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				name : $('#name').val(),
                description : $('#description').val(),
                time : $('#time').val(),
                taskdate : $('#taskdate').val(),
                tasklabels : $('#tasklabels').val(),
			},
			type : 'POST',
			url : '/add'
		})
		.done(function(data) {
			if (data.error) {
				$('#errorAlert').text(data.error).show();
				$('#successAlert').hide();
			}
			else {
				$('#successAlert').text(data.name).show();
				$('#errorAlert').hide();
			}

		});

		event.preventDefault();

	});

});