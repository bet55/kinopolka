// Функция для создания скриншота элементов страницы
// Используется для создания снимков открыток и их рассылки/архивации

// meeting date
// movies
// background picture

async function sendToServer(picture, posters, meeting_date, screenName) {
    // добавляем временную метку, чтобы в папке были файлы с разными названиями
    const date = new Date();
    const timestampScreenName = screenName.replace('.', date.getTime() + '.')

    const url = document.baseURI.split('/', 3).join('/');
    const myHeaders = new Headers();
    myHeaders.append("Authorization", "Token 943297fcddf785fc56da07c131e20e9d1d449629");

    const formdata = new FormData();
    formdata.append("meeting_date", meeting_date);
    formdata.append("background_picture", picture, timestampScreenName);
    posters.forEach(p => formdata.append("movies", p));


    const requestOptions = {
        method: "POST",
        headers: myHeaders,
        body: formdata,
        redirect: "follow"
    };

    console.log('Отправляем открытку ...')


    fetch(url, requestOptions)
        .then((response) => response.text())
        .then((result) => console.log(result))
        .catch((error) => console.error(error));
}


async function clientUpload(container, screenName) {
    const dataUrl = await modernScreenshot.domToPng(container);
    const link = document.createElement('a');
    link.download = screenName;
    link.href = dataUrl;
    link.click();
    return dataUrl
}

async function serverUpload(container, posters, meeting_date, screenName) {
    const blob = await modernScreenshot.domToBlob(container);
    await sendToServer(blob, posters, meeting_date, screenName)
}

async function screenshot(container, posters, meeting_date = '2001-09-11', screenName = 'screenshot.png', direction = 'server') {
    try {

        if (direction === 'server') {
            return await serverUpload(container, posters, meeting_date, screenName)
        } else {
            return await clientUpload(container, screenName)
        }


    } catch (error) {
        console.error('Screenshot failed:', error);
    }
}

export {screenshot}