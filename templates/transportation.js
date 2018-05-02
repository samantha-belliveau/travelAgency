$(function() {
    $('#searchTransportation').click(function() {
        $.ajax({
            url: '/searchTransportation',
            type: 'POST',
            success: function(response) {


                console.log(response);
                list = JSON.parse(response);
                console.log(list.result)
                if (list.result == 0){

                } else if (list.result == -1) {

                } else {
                    var data = "";
                    for (var i = 0; i<list.options.length; i++) {
                      id = list.options[i][0];
                      cost  = list.options[i][1];
                      method = list.options[i][2];
                      data += ("<tr><td>"+id+"</td><td>"+cost+"</td><td>"+method+"</td><tr>");
                      console.log(data);
                    }
                    var result = '<table class="table"><thead><tr><th scope="col">#</th><th scope="col">Name</th><th scope="col">Age</th><th scope="col">Gender</th></tr></thead><tbody>'+data+'</tbody></table>';
                    $("#TransportOptions").html(result);
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});
