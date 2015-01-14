$(function() {

    /* Default configuration for toggle user interactions */
    var basicToggleUserInteraction = new ToggleUserInteraction();
    basicToggleUserInteraction.config();

    /*
    // Advanced configuration [Example]

    // Extends the ToggleUserInteraction class behavior
    var MyToggleUserInteractionClass = iClazz(ToggleUserInteraction, {
        // Overrides a super class method
        success: function(response, status, xhr, context) {
            // Overrides completely the method, or override calling the supper class method too
            ToggleUserInteraction.prototype.success(response, status, xhr, context);
        }
    });

    // Creates a new instance of MyToggleUserInteractionClass
    var advancedToggleUserInteraction = new MyToggleUserInteractionClass();
    // config the instance with specific data
    advancedToggleUserInteraction.config({
        // Redefines the options
        container: $('selector')
    });

    */
});