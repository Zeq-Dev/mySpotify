document.addEventListener("DOMContentLoaded", function() {
    function updateSongCover() {
        fetch("/current_song_cover/")
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                } else {
                    const songCoverElement = document.getElementById("song-cover");
                    const songNameElement = document.getElementById("song-name");
                    const songAristElement = document.getElementById("artist");
                    const songProgElement = document.getElementById("current-time");
                    const progressBar = document.getElementById('prog-bar')

                    // songProgElement.innerHTML = data.song_prog;

                    if (data.song_cover && songCoverElement.src !== data.song_cover) {
                        songCoverElement.src = data.song_cover;
                    }
                    if (data.song_name && songNameElement.innerHTML !== data.song_name) {
                        songNameElement.innerHTML = data.song_name;
                        songAristElement.innerHTML = data.song_artist;
                    }

                    progress_percent = (Number(data.song_prog_ms) / Number(data.song_duration)) * 100;
                    if (progress_percent > 100) {return progress_percent=100}
                    console.log(progress_percent)
                    progressBar.style.width = progress_percent + '%';
                }
            })
            .catch(error => console.error('Error fetching song cover:', error));
    }

    // Update song cover every 5 seconds
    setInterval(updateSongCover, 1000);
});