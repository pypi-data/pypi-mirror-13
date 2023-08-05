
if (typeof(gocept.validation) == 'undefined') {
    gocept.validation = {};
}


gocept.validation.ErrorReporter = gocept.Class.extend({
    
    construct: function(element, message) {
        this.element = element;
        this.message = message;
        if (typeof(this.get_error_div()) == 'undefined') {
            this.visible = false;
        } else {
            this.visible = true;
        }
    },

    show: function() {
        if (this.visible)
            return;
        this.visible = true;
        addElementClass(this.get_widget_div(), 'error');
        MochiKit.DOM.insertSiblingNodesBefore(
            this.get_input_div(),
            DIV({class: 'error'},
                SPAN({class: 'error'}, this.message)));
    },
    
    hide: function() {
        if (!this.visible)
            return;
        removeElementClass(this.get_widget_div(), 'error');
        MochiKit.DOM.removeElement(this.get_error_div())
        this.visible = false;
    },

    get_widget_div: function() {
        return this.get_input_div().parentNode
    },
    
    get_input_div: function() {
        return $(this.element).parentNode
    },


    get_error_div: function() {
        return MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', 'error', this.get_widget_div());
    },
});


gocept.validation.MaxLength = gocept.Class.extend({

    construct: function(element, max_length, message) {
        this.element = $(element);
        this.max_length = max_length;
        this.reporter = new gocept.validation.ErrorReporter(element, message)
        connect(element, 'onkeyup', this, 'checklength');
        connect(element, 'onchange', this, 'checklength');
    },
    
    checklength: function(event) {
        if (this.element.value.length > this.max_length) {
            this.reporter.show();
        } else {
            this.reporter.hide();
        }
    },

});
