const createNoteElement = (movieId, userId, rating, comment) => {
    const userNote = document.querySelector(`.note-container[data-kp-id="${movieId}"] .note[data-user-id="${userId}"]`)
    if (userNote) {
        const noteH2 = userNote.querySelector('h2');
        // const noteP = userNote.querySelector('p');
        // noteP.textContent = comment;
        noteH2.textContent = rating;
        return false
    }
    const noteContainer = document.querySelector(`.note-container[data-kp-id="${movieId}"] `);
    const noteDiv = document.createElement('div');
    const noteH2 = document.createElement('h2');
    const noteP = document.createElement('p');


    noteP.textContent = comment;
    noteH2.textContent = rating;
    noteDiv.append(noteH2);
    noteDiv.classList.add('note');
    noteDiv.dataset.userId = userId;

    noteContainer.addEventListener('contextmenu', (e) => {
        noteContainer.remove();
        removeRateRequest(movieId, userId);
    })

    noteContainer.append(noteDiv);
    return true;
}

const removeRateRequest = async (movieId, userId) => {
    const removeUrl = '/movies/rate/remove/';
    const sendData = {
        user: userId,
        film: movieId
    }
    try {
        const response = await fetch(removeUrl, {
            method: "DELETE",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sendData),
        });
        console.log(await response.json());
    } catch (e) {
        console.error(sendData);
        console.error(e);
    }
}


const rateRequest = async (movieId, userId, rating, comment) => {
    const rateUrl = '/movies/rate/';
    const sendData = {
        user: userId,
        movie: movieId,
        rating: rating,
    }

    if (comment) {
        sendData['text'] = comment;
    }


    try {
        const response = await fetch(rateUrl, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sendData),
        });
        console.log(await response.json());
    } catch (e) {
        console.error(sendData);
        console.error(e);
    }
}

export {createNoteElement, rateRequest}