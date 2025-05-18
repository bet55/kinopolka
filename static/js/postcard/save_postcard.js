import {createToast} from "../utils/create_toast.js";
import {screenshot} from "./screenshot.js";
import {getNextSaturday} from "../utils/next_saturday.js";


// Сохраняем открытку в базе
export async function savePostcard() {
    const saveButton = document.querySelector('#postcard-save-button');
    const postcard = document.querySelector('#postcard-container');
    const title = document.querySelector('#invitation-title');

    if (!saveButton) {
        return null;
    }

    let isPending = false;

    // Предположение, что будет в следующую субботу
    title.innerText = getNextSaturday('text');

    saveButton.addEventListener('click', async e => {

        // Всё еще исполняется предыдущее действие
        if (isPending) {
            return null;
        }

        // Есть ли дата в заголовке открытки
        const postcardFilled = (title.innerText.replace(/\D/g, '')) && document.querySelector('.poster');

        if (!postcardFilled) {
            createToast('Заполните открытку', 'error')
            return null;
        }

        // Отображаем выполнение
        saveButton.classList.add('active_option')
        isPending = true;

        // Делаем скриншот текущей открытки и отправляем его
        title.contentEditable = false;
        const posters = document.querySelectorAll('.poster');
        const posters_ids = Array.from(posters).map(p => p.dataset.kpId);
        const screenSuccess = await screenshot(postcard, posters_ids, title.innerText, getNextSaturday('iso'));

        // Перезагрузим страницу, если успешно
        if (screenSuccess) {
            setTimeout(() => window.location.reload(), 1000);
        }

        // Возвращаем изначальное положение
        isPending = false;
        saveButton.classList.remove('active_option')

    })


}