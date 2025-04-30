const rateToggler = document.querySelector('#rate-toggle');

const changeNotesVisibility = () => {
    const rateNotes = document.querySelectorAll('.note-container')
    let visibility = localStorage.getItem('ratingVisibility') || 'hidden';

    // Отображаем оценки, если в локал стораже нужный флаг и мы на странице архива
    if (visibility === 'visible' && window.location.href.includes('archive')) {
        rateNotes.forEach(note => {
            note.style.visibility = visibility;
        })
    }


    return () => {

        visibility = (visibility === 'visible') ? 'hidden' : 'visible';

        localStorage.setItem('ratingVisibility', visibility);

        rateNotes.forEach(note => {
            note.style.visibility = visibility
        })
    }
}

// Функция смены видимости
const visibilityToggler = changeNotesVisibility()

export function showRatingNotesHandler() {
    if (!rateToggler) {
        return ''
    }

    rateToggler.addEventListener('click', (event) => {
        visibilityToggler();
    })

}
