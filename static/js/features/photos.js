import {createToast} from "../utils/create_toast.js";
import {Request} from "../utils/request.js";
import {confirmModalAction} from "../utils/confirm_modal_action.js";


document.addEventListener('DOMContentLoaded', () => {
    setupAddForm();

    document.querySelectorAll('.photo-card').forEach(card => {
        setupFlip(card);
        setupEdit(card);
        setupDelete(card);
    });
});

// ============== Загрузка новой фотографии ==============

function setupAddForm() {
    const addButton = document.querySelector('#photos .add');
    const formContainer = document.querySelector('#new-photo-form');
    const form = document.querySelector('#photo-form');
    const imageInput = document.querySelector('#photo-image');
    const imagePreview = document.querySelector('#photo-image-preview');
    const uploadLabel = document.querySelector('#new-photo-form .image-upload-label span');

    addButton.addEventListener('click', () => formContainer.classList.toggle('hide'));
    formContainer.querySelector('.close-btn').addEventListener('click', () => {
        form.reset();
        imagePreview.classList.add('hide');
        uploadLabel.style.display = '';
        formContainer.classList.add('hide');
    });

    // Превью выбранного файла
    imageInput.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                imagePreview.classList.remove('hide');
                uploadLabel.style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
    });

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (!imageInput.files.length) {
            createToast('Сначала выбери фото', 'error');
            return;
        }

        const response = await Request.post({
            url: '/features/photos/',
            body: new FormData(form)
        });

        // Проще перерисовать галерею сервером, чем собирать карточку руками
        if (response) {
            location.reload();
        }
    });
}

// ============== Переворот карточки ==============

function setupFlip(card) {
    const inner = card.querySelector('.photo-inner');

    inner.addEventListener('click', (e) => {
        // Клики по иконкам и форме редактирования — не переворачивают
        if (e.target.closest('.photo-actions, .photo-edit-form')) {
            return;
        }
        inner.classList.toggle('flipped');
    });
}

// ============== Редактирование описания ==============

function setupEdit(card) {
    const inner = card.querySelector('.photo-inner');
    const info = card.querySelector('.photo-info');
    const editForm = card.querySelector('.photo-edit-form');
    const nameNode = card.querySelector('.photo-name');
    const descriptionNode = card.querySelector('.photo-description');

    const closeEditForm = () => {
        editForm.classList.add('hide');
        info.classList.remove('hide');
    };

    // Иконка ✎ — переворачиваем карточку и открываем форму
    card.querySelector('.photo-actions .edit').addEventListener('click', () => {
        editForm.elements.name.value = nameNode.textContent;
        editForm.elements.description.value = descriptionNode.textContent;

        info.classList.add('hide');
        editForm.classList.remove('hide');
        inner.classList.add('flipped');
    });

    editForm.querySelector('.cancel').addEventListener('click', closeEditForm);

    editForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const response = await Request.patch({
            url: `/features/photos/${card.dataset.photoId}/`,
            body: {
                name: editForm.elements.name.value,
                description: editForm.elements.description.value
            }
        });

        if (response) {
            nameNode.textContent = response.name;
            descriptionNode.textContent = response.description;
            closeEditForm();
        }
    });
}

// ============== Удаление ==============

function setupDelete(card) {
    confirmModalAction({
        triggerNode: card.querySelector('.photo-actions .remove'),
        modalNode: card.querySelector('.confirmation'),
        confirmAction: async () => {
            const response = await Request.delete({url: `/features/photos/${card.dataset.photoId}/`});
            if (response !== null) {
                card.remove();
                createToast('Фото удалено', 'success');
            }
        }
    });
}
