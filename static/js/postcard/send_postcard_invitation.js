import {Request} from "../utils/request.js";
import {confirmModalAction} from "../utils/confirm_modal_action.js";


// Отправляем приглашение с открыткой (email, telegram)
async function sendPostcard(sendButton) {

    // Отображаем выполнение запроса
    sendButton.classList.add('active_option');

    // Запрос на отправку открытки
    await Request.post({url: '/invitation/'});

    sendButton.classList.remove('active_option');
}


// Запрашиваем подтверждение на отправку приглашения
export async function confirmAndSend() {

    const sendButton = document.querySelector('#postcard-send-button');   // Кнопка для отправки приглашения
    const confirmContainer = document.querySelector('.confirmation');  // Окно подтверждения отправления

    // Не нашли кнопку
    if (!sendButton) {
        return null;
    }

    // Отображаем окно подтверждения отправки
    const confirmModalOptions = {
        triggerNode: sendButton,
        modalNode: confirmContainer,
        confirmAction: async () => {await sendPostcard(sendButton)}
    }

    confirmModalAction(confirmModalOptions);


}


