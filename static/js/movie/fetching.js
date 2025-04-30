

export const fetchMovies = async () => {
    const baseUrl = document.baseURI.split('/', 3).join('/') + '/movies/';
    const url = (document.baseURI.includes('archive')) ? `${baseUrl}archive/` : `${baseUrl}`;

    const getMoviesUrl = `${url}?format=json`.replace('#', '');
    const response = await fetch(getMoviesUrl);

    if (!response.ok) {
        const message = `Movies request error: ${response.status}`;
        console.error(message);
    }

    const responseJson = await response.json();

    if(responseJson['success'] != true) {
        console.error(responseJson['error'])
    }

    return responseJson['data'];
}

