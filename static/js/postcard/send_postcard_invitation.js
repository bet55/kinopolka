import {Request} from "../utils/request.js";

// Кнопка для отправки приглашения
const sendButton = document.querySelector('#postcard-send-button');

// Отправляем приглашение с открыткой (email, telegram)
async function sendPostcard() {

    // Отображаем выполнение запроса
    sendButton.classList.add('active_option');

    // Запрос на отправку открытки
    const url = '/invitation/';
    await Request.send({method: 'post', url: url});
    // await new Promise(resolve => setTimeout(resolve, 3000));

    sendButton.classList.remove('active_option');
}


// Запрашиваем подтверждение на отправку приглашения
export async function confirmSaving() {

    // Не нашли кнопку
    if (!sendButton) {
        return null;
    }

    // Контейнер с подтверждением отправления
    const confirmContainer = document.querySelector('.confirmation');
    const confirmYes = confirmContainer.querySelector('#confirm-yes');
    const confirmNo = confirmContainer.querySelector('#confirm-no');

    // Флаг выполнения запроса
    let isPending = false;


    // Отрисовка формы подтверждения
    sendButton.addEventListener('click', () => {
        if (isPending) {
            return null;
        }
        confirmContainer.classList.toggle('active');
    })


    // Отправка
    confirmYes.addEventListener('click', async () => {

        if (isPending) {
            return null;
        }
        confirmContainer.classList.remove('active');

        isPending = true;

        await sendPostcard(isPending);

        isPending = false;
    })

    // Отмена отправки
    confirmNo.addEventListener('click', () => {
        confirmContainer.classList.remove('active');
    })

}


