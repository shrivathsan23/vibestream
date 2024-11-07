function sortVideos() {
    const sortBy = document.getElementById('sortBy').value;
    const videoList = document.getElementById('videoList');
    const videos = Array.from(videoList.getElementsByClassName('video-item'));

    let sortedVideos;

    if (sortBy === 'newest') {
        sortedVideos = videos.sort((a, b) => new Date(b.dataset.upload) - new Date(a.dataset.upload));
    } else if (sortBy === 'oldest') {
        sortedVideos = videos.sort((a, b) => new Date(a.dataset.upload) - new Date(b.dataset.upload));
    } else if (sortBy === 'popular') {
        sortedVideos = videos.sort((a, b) => parseInt(b.dataset.views) - parseInt(a.dataset.views));
    }

    videoList.innerHTML = '';
    sortedVideos.forEach(video => videoList.appendChild(video));
}