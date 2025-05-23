// Создаём значок в правом углу со статусом выполнения действия

export function createToast(text, status) {
    const toast = document.querySelector('#toast');

    // Задаем цвет
    const statuses = {
        success: 'toast_success',
        error: 'toast_error',
        info: 'toast_info'
    }
    const toastClassName = statuses[status];
    if (toastClassName) {
        toast.classList.add(toastClassName);
    }

    // Задаём текст
    const toastText = toast.querySelector('.toast-body');
    toastText.innerText = text;

    // Отрисовываем тост
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast, {delay: 1700});
    toastBootstrap.show();

    // Убираем цвет
    toast.addEventListener('hidden.bs.toast', () => {
        if (toastClassName) {
            toast.classList.remove(toastClassName);
        }
    })

}