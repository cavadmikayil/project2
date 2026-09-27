(function () {
    var STORAGE_KEY = 'edu-portal-theme';
    var ICONS = new URL('icons.svg?v=fc47fef9', document.currentScript.src).href;

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
            /* private rejim və s. hallarda sakitcə keç */
        }
    }

    function apply(theme) {
        var dark = theme === 'dark';
        document.body.classList.toggle('dark-mode', dark);
        var buttons = document.querySelectorAll('.theme-toggle-btn');
        for (var i = 0; i < buttons.length; i++) {
            buttons[i].innerHTML = '<svg class="icon" aria-hidden="true"><use href="' + ICONS + (dark ? '#sun' : '#moon') + '"></use></svg>';
            buttons[i].setAttribute('aria-label', dark ? 'İşıqlı rejimə keç' : 'Qaranlıq rejimə keç');
            buttons[i].setAttribute('aria-pressed', String(dark));
        }
    }

    function init() {
        apply(getStored());
        document.querySelectorAll('.theme-toggle-btn').forEach(function (btn) {
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
