(function () {
    const STORAGE_KEY = 'selectedLanguage';
    const LANGUAGES = [
        ['en', 'English'],
        ['hi', 'हिन्दी'],
        ['te', 'తెలుగు'],
        ['mr', 'मराठी']
    ];
    const FALLBACK = 'en';

    function readLanguage() {
        const value = window.localStorage.getItem(STORAGE_KEY);
        return LANGUAGES.some(([code]) => code === value) ? value : FALLBACK;
    }

    function selectors() {
        return Array.from(document.querySelectorAll(
            '#languageSelector, #portalLanguageSelector, #langSelector, #languageSelect, select.lang-select, select.language-selector, select.lang-selector'
        ));
    }

    function ensureSelector() {
        let controls = selectors();
        if (controls.length) return controls;

        const select = document.createElement('select');
        select.id = 'siteLanguageSelector';
        select.className = 'site-language-selector';
        select.setAttribute('aria-label', 'Select language');
        select.style.cssText = 'position:fixed;top:16px;right:16px;z-index:3000;padding:8px 10px;border:1px solid #d0d5dd;border-radius:8px;background:#fff;color:#172033;font:600 13px sans-serif;';
        document.body.appendChild(select);
        controls = [select];
        return controls;
    }

    function populate(control) {
        if (!control.options.length || !Array.from(control.options).some(option => option.value === 'en')) {
            control.innerHTML = LANGUAGES.map(([code, label]) => `<option value="${code}">${label}</option>`).join('');
        }
        control.value = readLanguage();
    }

    function applyPageDictionary(language) {
        const translator = window.updateLanguage || window.changeLanguage;
        if (typeof translator === 'function' && translator !== window.AarogyaLanguage.apply) {
            try { translator(language); } catch (error) { console.warn('Page translation failed:', error); }
        }
        document.documentElement.lang = language;
    }

    function apply(language) {
        const normalized = LANGUAGES.some(([code]) => code === language) ? language : FALLBACK;
        window.localStorage.setItem(STORAGE_KEY, normalized);
        ensureSelector().forEach(populate);
        applyPageDictionary(normalized);
        ensureSelector().forEach(control => { control.value = normalized; });
    }

    function initialize() {
        const controls = ensureSelector();
        controls.forEach(control => {
            populate(control);
            control.addEventListener('change', event => apply(event.target.value));
        });
        apply(readLanguage());
        window.addEventListener('storage', event => {
            if (event.key === STORAGE_KEY && event.newValue) apply(event.newValue);
        });
    }

    window.AarogyaLanguage = { apply, initialize };
    document.addEventListener('DOMContentLoaded', initialize, { once: true });
})();
