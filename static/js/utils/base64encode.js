// Функция для замены атрибута "src" тэга "img" со ссылочного на кодовый
// Нужно, чтобы делать корректные скриншоты

const getBase64FromUrl = async (url) => {
    const imageData = await fetch(url);
    const blob = await imageData.blob();

    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
            const base64data = reader.result;
            resolve(base64data);
        }
    })
}