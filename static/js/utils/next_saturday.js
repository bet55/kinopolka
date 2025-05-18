// Получаем дату следующей субботы, для генерации открытки

const MONTH_NAMES = [
  'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
];

function getNextSaturday(format = 'text') {
  const today = new Date();
  const daysToAdd = (6 - today.getDay() + 7) % 7 || 7;
  const nextSaturday = new Date(today);
  nextSaturday.setDate(today.getDate() + daysToAdd);
  nextSaturday.setHours(18);
  nextSaturday.setMinutes(0);

  const formats = {
    text: () => {
      const day = nextSaturday.getDate();
      const month = MONTH_NAMES[nextSaturday.getMonth()];
      return `${day} ${month}`;
    },
    iso: () => {
      return nextSaturday.toISOString().split('.')[0].replace('T', ' ');
    },
    full: () => nextSaturday.toLocaleDateString('ru-RU')
  };

  return formats[format] ? formats[format]() : formats.text();
}

export {getNextSaturday}