$(function() {

    /* Default configuration for toggle user interactions */
    var basicToggleSocialInteraction = new ToggleSocialInteraction();
    basicToggleSocialInteraction.config();

    /*
    // Advanced configuration [Example]

    // Extends the ToggleSocialInteraction class behavior
    var MyToggleSocialInteractionClass = iClazz(ToggleSocialInteraction, {
        // Overrides a super class method
        success: function(response, status, xhr, context) {
            // Overrides completely the method, or override calling the supper class method too
            ToggleSocialInteraction.prototype.success(response, status, xhr, context);
        }
    });

    // Creates a new instance of MyToggleSocialInteractionClass
    var advancedToggleSocialInteraction = new MyToggleSocialInteractionClass();
    // config the instance with specific data
    advancedToggleSocialInteraction.config({
        // Redefines the options
        container: $('selector')
    });

    */

    // Extends the FormSocialInteraction class behavior
    var MyFormSocialInteractionClass = iClazz(FormSocialInteraction, {

        // Defines the super class method
        eventImpl: function(eventTrigger) {
            // --------------
        }
    });

    var formSocialInteraction = new MyFormSocialInteractionClass();
    // config the instance with specific data
    formSocialInteraction.config({
        // Redefines the options
        selector: '.selector',
        eventType: 'shown.bs.modal'
    });

});