// Функция для создания скриншота элементов страницы
// Используется для создания снимков открыток и их рассылки/архивации


async function sendToServer(blob) {
    const formData = new FormData();
    formData.append('screenshot', blob, 'screenshot.png'); // 'screenshot' is the field name

    const response = await fetch('https://your-server.com/upload', {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('Failed to send screenshot to server');
    }

    const result = await response.json();
    console.log('Server response:', result);
}

async function clientUpload(container, screenName) {
    const dataUrl = await modernScreenshot.domToPng(container);
    const link = document.createElement('a');
    link.download = screenName;
    link.href = dataUrl;
    link.click();
    return dataUrl
}

async function serverUpload(container) {
    const blob = await modernScreenshot.domToBlob(container);
    console.log('Blob created:', blob);
}

async function modernShot(container, direction = '', screenName = 'screenshot.png') {
    try {

        if (direction === 'server') {
            return await serverUpload(container, screenName)
        } else {
            return await clientUpload(container, screenName)
        }


    } catch (error) {
        console.error('Screenshot failed:', error);
    }
}

export {modernShot}