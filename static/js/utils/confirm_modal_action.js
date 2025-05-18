
// Функция для отображения модального окна подтверждения действия
export function confirmModalAction({
                                 triggerNode,
                                 modalNode,
                                 confirmAction = async () => {
                                 },

                             }) {


    const confirmNode = modalNode.querySelector('.confirm-yes');
    const declineNode = modalNode.querySelector('.confirm-no');

    let isPending = false;

    // Появление окна подтверждения
    triggerNode.addEventListener('click', () => {

        // Заняты
        if (isPending) {
            return null;
        }

        modalNode.classList.toggle('active');
    })

    // Подтверждаем выполнение
    confirmNode.addEventListener('click', async () => {
        modalNode.classList.toggle('active');

        isPending = true;

        await confirmAction();

        isPending = false;
    })

    // Отменяем выполнение
    declineNode.addEventListener('click', () => {
        modalNode.classList.toggle('active');
    })

}