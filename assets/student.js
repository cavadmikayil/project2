(function () {
    var PROFILES_KEY = 'edu-portal-profiles';
    var CURRENT_KEY = 'edu-portal-current';
    var memory = {};

    // localStorage əlçatmaz olduqda (private rejim və s.) səhifə daxilində yaddaşa keçir
    function read(key, fallback) {
        var raw;
        try {
            raw = localStorage.getItem(key);
        } catch (e) {
            raw = key in memory ? memory[key] : null;
        }
        if (raw === null || raw === undefined) return fallback;
        try {
            var value = JSON.parse(raw);
            return value === null ? fallback : value;
        } catch (e) {
            return fallback;
        }
    }

    function write(key, value) {
        var raw = JSON.stringify(value);
        try {
            localStorage.setItem(key, raw);
        } catch (e) {
            memory[key] = raw;
        }
    }

    function remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            delete memory[key];
        }
    }

    function idFor(name) {
        return name.trim().toLocaleLowerCase('az').replace(/\s+/g, '-');
    }

    window.Student = {
        read: read,
        write: write,

        profiles: function () {
            return read(PROFILES_KEY, {});
        },

        current: function () {
            var id = read(CURRENT_KEY, null);
            var all = this.profiles();
            if (!id || !all[id]) return null;
            return { id: id, name: all[id].name };
        },

        login: function (name) {
            var id = idFor(name);
            var all = this.profiles();
            var existing = all[id];
            all[id] = { name: existing ? existing.name : name.trim() };
            write(PROFILES_KEY, all);
            write(CURRENT_KEY, id);
            return this.current();
        },

        switchTo: function (id) {
            write(CURRENT_KEY, id);
        },

        logout: function () {
            remove(CURRENT_KEY);
        },

        // Hər tələbənin məlumatı ayrıca açarda saxlanılır
        key: function (base) {
            var c = this.current();
            return c ? base + ':' + c.id : base;
        }
    };
})();
