import {Request} from "../utils/request.js";

// Отправляем приглашение с открыткой (email, telegram)

export async function sendPostcard() {

    const sendButton = document.querySelector('#postcard-send-button');

    if (!sendButton) {
        return null;
    }

    let isPending = false;

    sendButton.addEventListener('click', async () => {

        // Всё еще исполняется предыдущее действие
        if (isPending) {
            return null;
        }

        // Отображаем выполнение запроса
        isPending = true;
        sendButton.classList.add('active_option');

        // Запрос на отправку открытки
        const url = '/invitation/';
        await Request.send({method: 'post', url:url});

        // Отображаем выполнение запроса
        isPending = false;
        sendButton.classList.remove('active_option');

    })
}
