(function () {
    // Tab-lar: <div data-tabs> içindəki .tab-btn[data-pane] düymələri id-si data-pane olan paneli göstərir
    document.querySelectorAll('[data-tabs]').forEach(function (bar) {
        var buttons = Array.prototype.slice.call(bar.querySelectorAll('.tab-btn'));
        bar.setAttribute('role', 'tablist');

        function activate(target) {
            buttons.forEach(function (btn) {
                var on = btn === target;
                btn.classList.toggle('active-tab', on);
                btn.classList.toggle('inactive-tab', !on);
                btn.setAttribute('aria-selected', String(on));
                var pane = document.getElementById(btn.dataset.pane);
                if (pane) pane.classList.toggle('hidden', !on);
            });
        }

        buttons.forEach(function (btn) {
            btn.setAttribute('role', 'tab');
            btn.addEventListener('click', function () { activate(btn); });
        });
        activate(bar.querySelector('.active-tab') || buttons[0]);
    });

    function fallbackCopy(text) {
        var area = document.createElement('textarea');
        area.value = text;
        area.style.position = 'fixed';
        area.style.opacity = '0';
        document.body.appendChild(area);
        area.select();
        try { document.execCommand('copy'); } catch (e) { /* kopyalama dəstəklənmir */ }
        document.body.removeChild(area);
    }

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.copy-btn');
        if (!btn) return;
        var text = btn.closest('.code-block').querySelector('code').innerText;
        var done = function () {
            btn.textContent = 'Kopyalandı!';
            setTimeout(function () { btn.textContent = 'Kopyala'; }, 2000);
        };
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text); done(); });
        } else {
            fallbackCopy(text);
            done();
        }
    });
})();
