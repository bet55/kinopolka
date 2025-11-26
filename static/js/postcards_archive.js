// postcards_archive2.js
import { Request } from "./utils/request.js";
import { confirmModalAction } from "./utils/confirm_modal_action.js";

// УДАЛЕНИЕ ОТКРЫТКИ
async function removePostcard(postcardNode, postcardId) {
    const response = await Request.delete({ url: '/', body: { id: postcardId } });
    if (response !== null) {
        const tooltip = document.querySelector('.tooltip.show');
        if (tooltip) tooltip.remove();
        postcardNode.remove();
    }
}

// Подключаем удаление
document.querySelectorAll('.postcard:not(.active)').forEach(postcard => {
    const img = postcard.querySelector('.postcard-normal img');
    const confirmContainer = postcard.querySelector('.confirmation');

    if (img && confirmContainer) {
        confirmModalAction({
            triggerNode: img,
            modalNode: confirmContainer,
            confirmAction: () => removePostcard(postcard, postcard.dataset.postcardId)
        });
    }
});

// ПЕРЕКЛЮЧЕНИЕ РЕЖИМА ОЦЕНОК
document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("rate-toggle");
    if (!toggleBtn) return;

    const postcards = document.querySelectorAll(".postcard");

    toggleBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const isActive = document.body.classList.toggle("ratings-mode");
        postcards.forEach(card => {
            card.classList.toggle("show-ratings", isActive);
        });
    });

});