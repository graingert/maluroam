/*! maluroam github.com/graingert/maluroam/ | github.com/graingert/maluroam/raw/master/COPYING */
$(function () {
    "use strict";
    $('#paginate a').pjax('#paginate', {"fragment":"#paginate", "scrollTo":false});
    //$('a:not(#paginate a)').pjax('#main', {"fragment":"#main", "scrollTo":false});
});
