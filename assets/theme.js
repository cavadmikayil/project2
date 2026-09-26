(function () {
    var STORAGE_KEY = 'edu-portal-theme';

    function getStored() {
        try {
            return localStorage.getItem(STORAGE_KEY) || 'light';
        } catch (e) {
            return 'light';
        }
    }

    function setStored(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            /* private mode və s. hallarda sakitcə keç */
        }
    }

    function apply(theme) {
        document.body.classList.toggle('dark-mode', theme === 'dark');
        var buttons = document.querySelectorAll('.theme-toggle-btn');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    function init() {
        apply(getStored());
        var buttons = document.querySelectorAll('.theme-toggle-btn');
        buttons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var next = getStored() === 'dark' ? 'light' : 'dark';
                setStored(next);
                apply(next);
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
