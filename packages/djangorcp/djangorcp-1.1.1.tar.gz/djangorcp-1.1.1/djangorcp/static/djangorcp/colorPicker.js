$(document).ready(function() {
    $('.color-box').colorPicker();
});

$.fn.colorPicker = function() {
    return this.each(function() {
        $(this).click(function(event) {
            var fieldId = $(this)[0].dataset['field'];
            var hex = $(this)[0].dataset['hex'];
            var $field = $('#'+fieldId);

            $field.val(hex);
            $field.css('border-color', hex);
        });
    });
};
