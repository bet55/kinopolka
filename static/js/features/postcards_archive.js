import {Request} from "../utils/request.js";


// Для каждой открытки создаем слушателя на удаление
const postcards = document.querySelectorAll('.postcard:not(.active)');

postcards.forEach(p => {

    const img = p.querySelector('img');
    img.addEventListener('click', () => {

        // Контейнер с подтверждением отправления
        const confirmContainer = p.querySelector('.confirmation');
        const confirmYes = confirmContainer.querySelector('#confirm-yes');
        const confirmNo = confirmContainer.querySelector('#confirm-no');

        // отображение модалки с подтверждением
        confirmContainer.classList.toggle('active');

        // Удаляем
        confirmYes.addEventListener('click', async () => {
            confirmContainer.classList.remove('active');

            const postcardId = p.dataset.postcardId;
            const response = await Request.send({method: 'delete', url: '/', body: {id: postcardId}})

            if (response !== null) {
                document.querySelector('.tooltip').remove() // удаляем подсказку
                p.remove();
            }

        })

        // Не удаляем
        confirmNo.addEventListener('click', () => {
            confirmContainer.classList.remove('active');
        })

    })

})

