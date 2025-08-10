function isMobileDevice() {
    const userAgent = navigator.userAgent || navigator.vendor || window.opera;
    if (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent)) {
        return true;
    }
    return false;
}


function navigationToggle() {
    if(isMobileDevice() || true) {
        const title = document.querySelector('.title');
        const navigation = document.querySelector('.nav-column');
        title.addEventListener('click', () => {
            navigation.style.display = (navigation.style.display === 'none') ? 'flex' : 'none';
        })
    }
}

export {navigationToggle}
