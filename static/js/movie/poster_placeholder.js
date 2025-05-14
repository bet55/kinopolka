
// Пока не загрузились постеры с апихи держим заглушку
export function posterLoadingPlaceholder() {
    document.addEventListener('DOMContentLoaded', function () {
        const lazyImages = document.querySelectorAll('.poster-img');

        lazyImages.forEach(img => {
            const actualSrc = img.getAttribute('data-src');
            if (actualSrc) {
                const tempImg = new Image();
                tempImg.src = actualSrc;
                tempImg.onload = function () {
                    img.src = actualSrc;
                };
                tempImg.onerror = function () {
                    img.src = '/static/img/poster_placeholder.jpg';
                };
            }
        });
    });
}