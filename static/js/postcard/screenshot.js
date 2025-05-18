import {createToast} from "../utils/create_toast.js";
import {Request} from "../utils/request.js";


async function sendToServer(picture, posters, title, meeting_date, screenName) {

    // добавляем временную метку, чтобы в папке были файлы с разными названиями
    const date = new Date();
    const timestampScreenName = screenName.replace('.', date.getTime() + '.');

    const formdata = new FormData();
    formdata.append("title", title);
    formdata.append("meeting_date", meeting_date);
    formdata.append("screenshot", picture, timestampScreenName);
    posters.forEach(p => formdata.append("movies", p));

    const response = await Request.post({url: '', body: formdata});
    return response !== null; // request is success ?

}

// Сохраняем скриншот на клиенте
async function clientUpload(container, screenName) {
    const dataUrl = await modernScreenshot.domToPng(container);
    const link = document.createElement('a');
    link.download = screenName;
    link.href = dataUrl;
    link.click();
    return dataUrl
}

// Сохраняем скриншот в бд
async function serverUpload(container, posters, title, meeting_date, screenName) {
    const blob = await modernScreenshot.domToBlob(container);
    return await sendToServer(blob, posters, title, meeting_date, screenName)
}

// Функция для создания скриншота элементов страницы
// Используется для создания снимков открыток и их рассылки/архивации
async function screenshot(container, posters, title, meeting_date = '2001-09-11', screenName = 'screenshot.png', direction = 'server') {
    try {

        if (direction === 'server') {
            return await serverUpload(container, posters, title, meeting_date, screenName);
        }

        return await clientUpload(container, screenName);

    } catch (error) {
        createToast('Открытка не сохранилась!', 'error');
        console.error('Screenshot failed:', error);
        return null;
    }
}

export {screenshot}