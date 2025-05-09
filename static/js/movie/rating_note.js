import {Request} from "../utils/request.js";

// Создаём новый стикер с оценкой фильма
const createNoteElement = (movieId, userId, rating, comment) => {

    // Если стикер уже есть, просто меняем значение оценки
    const userNote = document.querySelector(`.note-container[data-kp-id="${movieId}"] .note[data-user-id="${userId}"]`)
    if (userNote) {
        const noteH2 = userNote.querySelector('h2');
        // const noteP = userNote.querySelector('p');
        // noteP.textContent = comment;
        noteH2.textContent = rating;
        return false
    }

    // Создаём новый стикер
    const noteContainer = document.querySelector(`.note-container[data-kp-id="${movieId}"] `);
    const noteDiv = document.createElement('div');
    const noteH2 = document.createElement('h2');
    const noteP = document.createElement('p');

    noteP.textContent = comment;
    noteH2.textContent = rating;
    noteDiv.append(noteH2);
    noteDiv.classList.add('note');
    noteDiv.dataset.userId = userId;

    // Создаём обработчик удаления стикера
    noteContainer.addEventListener('contextmenu', async (e) => {
        noteContainer.remove();
        await removeRateRequest(movieId, userId);
    })

    noteContainer.append(noteDiv);
    return true;
}

// Удаляем запись с оценкой фильма
const removeRateRequest = async (movieId, userId) => {
    const url = '/movies/rate/remove/';
    const sendData = {
        user: userId,
        film: movieId
    }

    const requestOption = {method: 'delete', url: url, body: sendData}
    await Request.send(requestOption);
}


// Создаём запись с оценкой фильма
const rateRequest = async (movieId, userId, rating, comment) => {
    const url = '/movies/rate/';
    const sendData = {
        user: userId,
        movie: movieId,
        rating: rating,
    }

    if (comment) {
        sendData['text'] = comment;
    }

    const requestOption = {method: 'post', url: url, body: sendData}
    await Request.send(requestOption);
}

export {createNoteElement, rateRequest}