var modalGroupCreate = $('#modal_add_social_group');
modalGroupCreate.on('shown.bs.modal', function() {
    var modalForm = $('#group_create_form');
    if (modalForm.length){
        $(modalForm).find('.selectpicker').selectpicker();
        $.initUniformFields(null);

        modalForm.validate({
            rules: {
                name: {
                    required: true
                },
                description: {
                    required: true
                },
                image: {
                    required: true
                }
            },
            messages: {
                name: {
                    required: $.REQUIRED
                },
                description: {
                    required: $.REQUIRED
                },
                image: {
                    required: $.REQUIRED
                }
            }
        });

        modalForm.on('success.cp.form', function(e) {
            // Adding success notification
            $.addNotification($.TOP_LAYOUT, $.SUCCESS, $.SERVER_SUCCESS_MESSAGE);
            var container = $('#groupTab');
            if (container.length)
                container.load(container.data('url'));
        });

        modalForm.on('error.cp.form', function(e) {
            // Adding server error notification
            $.addNotification($.TOP_LAYOUT, $.ERROR, $.SERVER_ERROR_MESSAGE)
        });
    }

});