$(function () {
    "use strict";
    $('#paginate a').pjax('#paginate', {"fragment":"#paginate", "scrollTo":false});
    
    $('#paginate').on('pjax:beforeSend', function(){
        $('#paginate').hide('slow');
    });
    
    $('#paginate').on('pjax:end', function(){
        $('#paginate').show('slow');
    });
    //$('a:not(#paginate a)').pjax('#main', {"fragment":"#main", "scrollTo":false});
});
