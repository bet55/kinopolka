import {Request} from "../utils/request.js";


// Архивируем предыдущую открытку и выводим пустой бланк
export async function createPostcard() {
    const createButton = document.querySelector('#postcard-create-button');

    if (!createButton) {
        return null;
    }

    let isPending = false;

    createButton.addEventListener('click', async () => {

        // Всё еще исполняется предыдущее действие
        if (isPending) {
            return null;
        }

        createButton.classList.add('active_option')

        const url = document.baseURI.split('/', 3).join('/') + '/';

        const requestOptions = {
            method: "PUT",
            redirect: "follow"
        };

        isPending = true;

        const response = await Request.send({method: 'put', url: url});

        // Ошибка при выполнении запроса
        if (response === null) {
            isPending = false;
            return null;
        }

        createButton.classList.remove('active_option')

        // Перезагружаем страницу
        setTimeout(() => window.location.reload(), 1000);


    })


}