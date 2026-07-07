// Рубильник тёмной темы. Анимация — спрайт-лента из кадров gif-переключателя
// (см. static/img/light_switch_sprite.webp), классы to-dark/to-light запускают
// CSS-анимацию, is-dark/is-light — статичные крайние положения.

const DARK_KEY = 'dark-mode';

const isDark = () => document.documentElement.classList.contains('dark-mode');

export function themeToggleHandler() {
    const switcher = document.querySelector('#light-switch');
    if (!switcher) {
        return;
    }

    // Стартовое положение рубильника без анимации (тема уже применена в <head>)
    switcher.classList.add(isDark() ? 'is-dark' : 'is-light');

    switcher.addEventListener('click', () => {
        const goingDark = !isDark();

        document.documentElement.classList.toggle('dark-mode', goingDark);
        if (goingDark) {
            localStorage.setItem(DARK_KEY, '1');
        } else {
            localStorage.removeItem(DARK_KEY);
        }

        switcher.classList.remove('is-dark', 'is-light', 'to-dark', 'to-light');
        switcher.classList.add(goingDark ? 'to-dark' : 'to-light');
    });

    // После щелчка фиксируем крайнее положение
    switcher.addEventListener('animationend', () => {
        switcher.classList.remove('to-dark', 'to-light');
        switcher.classList.add(isDark() ? 'is-dark' : 'is-light');
    });
}
