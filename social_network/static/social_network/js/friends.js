$(function(){
    var body =  $('body');
    body.delegate('.accept_request_link', 'click', function(e){
        e.preventDefault();
        var $this = $(this);
        $.ajax($this.attr('href'), {
            type: 'POST',
            success:function(response, status){
                $.addNotification($.TOP_LAYOUT, $.SUCCESS, response['successMsg'])
                var container = $('#friendsTab');
                if (container.length)
                    container.load(container.data('url'));
            },
            error: function(response, status){
                $.addNotification($.TOP_LAYOUT, $.ERROR, $.SERVER_ERROR_MESSAGE)
            }
        })
    });
});

var friendRequestModal = $("#modal_add_friend_request");
friendRequestModal.on('shown.bs.modal', function() {
    var modalForm = $('#friend_request_form');
    if (modalForm.length){

        modalForm.on('success.cp.form', function(e) {
            // Adding success notification
            $.addNotification($.TOP_LAYOUT, $.SUCCESS, e.response['successMsg']);
            var container = $('#friendsTab');
            if (container.length)
                container.load(container.data('url'));

            var btnsContainer = $('#buttonsContainer');
            if (btnsContainer.length)
                btnsContainer.load(btnsContainer.data('url'));
        });

        modalForm.on('error.cp.form', function(e) {
            // Adding server error notification
            $.addNotification($.TOP_LAYOUT, $.ERROR, $.SERVER_ERROR_MESSAGE)
        });
    }
});