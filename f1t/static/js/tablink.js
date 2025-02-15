// JavaScript to enable link to tab
document.addEventListener('DOMContentLoaded', function () {
    var url = document.location.toString();
    if (url.match('#')) {
        var tabId = url.split('#')[1];
        var tabTrigger = document.querySelector('.nav-tabs a[href="#' + tabId + '"]');
        if (tabTrigger) {
            var tab = new bootstrap.Tab(tabTrigger);
            tab.show();
        }
    }

    // With HTML5 history API, we can easily prevent scrolling!
    var navTabs = document.querySelectorAll('.nav-tabs a');
    navTabs.forEach(function (tab) {
        tab.addEventListener('shown.bs.tab', function (e) {
            if (history.pushState) {
                history.pushState(null, null, e.target.hash);
            } else {
                window.location.hash = e.target.hash; // Polyfill for old browsers
            }
        });
    });
});
