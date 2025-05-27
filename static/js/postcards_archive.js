import {Request} from "./utils/request.js";
import {confirmModalAction} from "./utils/confirm_modal_action.js";

// Функция удаления открытки
async function removePostcard(postcardNode, postcardId) {

    const response = await Request.delete({url: 'archive/', body: {id: postcardId}})

    if (response !== null) {

        // удаляем подсказку
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove()
        }

        postcardNode.remove();
    }

}

// Для каждой открытки создаем слушателя на удаление
const postcards = document.querySelectorAll('.postcard:not(.active)');

postcards.forEach(p => {

    const img = p.querySelector('img');  //
    const confirmContainer = p.querySelector('.confirmation');   // Окно подтверждения удаления

    // Отображаем окно подтверждения удаления
    const confirmModalOptions = {
        triggerNode: img,
        modalNode: confirmContainer,
        confirmAction: async () => await removePostcard(p, p.dataset.postcardId)
    }
    confirmModalAction(confirmModalOptions);

})

