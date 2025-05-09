// Переводим минуты в человекочитаемый формат

function hoursFormated(hours) {
    const hoursDictionary = {
        0: "часов", 1: "час", 2: "часа", 3: "часа", 4: "часа",
        5: "часов", 6: "часов", 7: "часов", 8: "часов", 9: "часов",
        10: 'часов', 11: "часов", 12: "часов", 13: "часов", 14: "часов",
        15: "часов", 16: "часов", 17: "часов", 18: "часов", 19: "часов",
    }
    if (hoursDictionary[hours]) {
        return `${hours} ${hoursDictionary[hours]}`
    }
    const lastDigit = hours % 10;
    return `${hours} ${hoursDictionary[lastDigit]}`

}

function minutesFormated(minutes) {
    const minutesDictionary = {
        0: "минут", 1: "минута", 2: "минуты", 3: "минуты", 4: "минуты",
        5: "минут", 6: "минут", 7: "минут", 8: "минут", 9: "минут",
        10: "минут", 11: "минут", 12: "минут", 13: "минут", 14: "минут",
        15: "минут", 16: "минут", 17: "минут", 18: "минут", 19: "минут",
    }
    if (minutesDictionary[minutes]) {
        return `${minutes} ${minutesDictionary[minutes]}`
    }
    const lastDigit = minutes % 10;
    return `${minutes} ${minutesDictionary[lastDigit]}`


}

export const formatTime = (mins) => {
    mins = parseInt(mins);
    const hours = Math.trunc(mins / 60);
    const minutes = mins % 60;

    const hourStr = hoursFormated(hours);
    const minuteStr = minutesFormated(minutes);

    return `${hourStr} ${minuteStr}`;
}