$(function () {
    //Initializing ajax tabs
    var detailTabs = $('#detailTabs');
    $.initAjaxTabs(detailTabs);
    detailTabs.find('a:first').tab('show');

    //Adding listener to "accept membership request" link
    var body = $('body');
    body.delegate('.accept_request_link', 'click', function (e) {
        e.preventDefault();
        var $this = $(this);
        $.ajax($this.attr('href'), {
            type: 'POST',
            success: function (response, status) {
                $.addNotification($.TOP_LAYOUT, $.SUCCESS, response['successMsg'])
                var container = $('#membershipRequestsTab');
                if (container.length)
                    container.load(container.data('url'));
            },
            error: function (response, status) {
                $.addNotification($.TOP_LAYOUT, $.ERROR, $.SERVER_ERROR_MESSAGE)
            }
        })
    });

    var joinLink = $('#grou_join_link');
    joinLink.on('click', function (e) {
        e.preventDefault();
        var $this = $(this);
        $.ajax($this.attr('href'), {
            type: 'POST',
            success: function (response, status) {
                $.addNotification($.TOP_LAYOUT, $.SUCCESS, response['successMsg'])
                var container = $('#membersTab');
                if (container.length)
                    container.load(container.data('url'));

                refreshBtns();
            },
            error: function (response, status) {
                $.addNotification($.TOP_LAYOUT, $.ERROR, $.SERVER_ERROR_MESSAGE)
            }
        })
    })
});

var commentCreateModal = $("#modal_add_group_comment");
commentCreateModal.on('shown.bs.modal', function () {
    var modalForm = $('#modal_group_comment_form');
    if (modalForm.length) {

        modalForm.validate({
            rules: {
                comment: {
                    required: true
                }
            },
            messages: {
                comment: {
                    required: $.REQUIRED
                }
            }
        });

        modalForm.on('success.cp.form', function (e) {
            // Adding success notification
            $.addNotification($.TOP_LAYOUT, $.SUCCESS, e.response['successMsg']);
            var container = $('#feedTab');
            container.load(container.data('url'));
        });

        modalForm.on('error.cp.form', function (e) {
            // Adding server error notification
            $.addNotification($.TOP_LAYOUT, $.ERROR, $.SERVER_ERROR_MESSAGE)
        });
    }
});

var photoCreateModal = $("#modal_add_group_photo");
photoCreateModal.on('shown.bs.modal', function () {
    var modalForm = $('#modal_group_photo_form');
    if (modalForm.length) {

        modalForm.validate({
            rules: {
                image: {
                    required: true
                },
                comment: {
                    required: true
                }
            },
            messages: {
                image: {
                    required: $.REQUIRED
                },
                comment: {
                    required: $.REQUIRED
                }
            }
        });

        modalForm.on('success.cp.form', function (e) {
            // Adding success notification
            $.addNotification($.TOP_LAYOUT, $.SUCCESS, e.response['successMsg']);
            var container = $('#feedTab');
            container.load(container.data('url'));
        });

        modalForm.on('error.cp.form', function (e) {
            // Adding server error notification
            $.addNotification($.TOP_LAYOUT, $.ERROR, $.SERVER_ERROR_MESSAGE)
        });
    }
});

var requestCreateModal = $("#modal_group_request_create");
requestCreateModal.on('shown.bs.modal', function () {
    var modalForm = $('#group_request_form');
    if (modalForm.length) {

        modalForm.on('success.cp.form', function (e) {
            // Adding success notification
            $.addNotification($.TOP_LAYOUT, $.SUCCESS, e.response['successMsg']);
            var container = $('#feedTab');
            if (container.length)
                container.load(container.data('url'));

            refreshBtns();
        });

        modalForm.on('error.cp.form', function (e) {
            // Adding server error notification
            $.addNotification($.TOP_LAYOUT, $.ERROR, $.SERVER_ERROR_MESSAGE)
        });
    }
});

var refreshBtns = function () {
    var btnsContainer = $('#buttonsContainer');
    if (btnsContainer.length)
        btnsContainer.load(btnsContainer.data('url'));
};