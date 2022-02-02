$('#starttime').calendar({
    ampm: true  ,
    type: 'time',
    onChange: function (time, text) {
      var newValue = text;
    },
  });

$(document).ready(function() {
    $('form').on('submit', function(event){

        $.ajax({
            data:{
                name : $('#name').val(),
            },
            type : 'POST',
            url : '/add'
        })
        .done(function(data){
            if (data.error) {
				$('#errorAlert').text(data.error).show();
			}
			else {
				$('#errorAlert').hide();
			}
        });
        event.preventDefault();
    });
});

