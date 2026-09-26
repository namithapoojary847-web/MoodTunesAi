/**
 * MoodTunes - HTML5 Native Audio Player & Music Recommendation Deck
 */

let currentTrack = null;
let currentPlaylist = [];
let audioPlayer = null;
let isPlaying = false;

document.addEventListener('DOMContentLoaded', () => {
    audioPlayer = document.getElementById('html5AudioPlayer');
    window.loadRecommendationsForMood = loadRecommendationsForMood;

    const btnPlayPause = document.getElementById('btnPlayPauseAudio');
    const seekSlider = document.getElementById('audioSeekSlider');

    if (btnPlayPause) {
        btnPlayPause.addEventListener('click', toggleAudioPlay);
    }

    if (audioPlayer) {
        audioPlayer.addEventListener('timeupdate', updateAudioProgress);
        audioPlayer.addEventListener('ended', onTrackEnded);
    }

    if (seekSlider) {
        seekSlider.addEventListener('input', (e) => {
            if (audioPlayer && audioPlayer.duration) {
                audioPlayer.currentTime = (e.target.value / 100) * audioPlayer.duration;
            }
        });
    }

    // Default initial mood recommendations load
    loadRecommendationsForMood('Neutral');
});

async function loadRecommendationsForMood(mood) {
    try {
        const response = await fetch(`/api/recommendations/${mood}?t=${Date.now()}`);
        const data = await response.json();

        if (data.success) {
            currentPlaylist = data.tracks;
            renderPlaylistHeader(data);
            renderTrackList(data.tracks, mood);

            // Auto-load top recommended track into Audio Player
            if (data.tracks && data.tracks.length > 0) {
                playTrack(data.tracks[0], false);
            }
        }
    } catch (err) {
        console.error("Error fetching recommendations:", err);
    }
}

function renderPlaylistHeader(data) {
    const genreTag = document.getElementById('genreTag');
    const moodDesc = document.getElementById('moodDesc');

    if (genreTag) {
        genreTag.textContent = data.genre;
        genreTag.style.background = data.badge_color || '#7c3aed';
    }
    if (moodDesc) moodDesc.textContent = data.description;
}

function renderTrackList(tracks, mood) {
    const trackListContainer = document.getElementById('trackList');
    if (!trackListContainer) return;

    trackListContainer.innerHTML = '';

    tracks.forEach((track) => {
        const card = document.createElement('div');card.className =
`track-card ${
currentTrack &&
currentTrack.title === track.title &&
currentTrack.artist === track.artist
? 'active'
: ''
}`;
        card.setAttribute(
    'data-id',
    `${track.id}-${track.artist}-${track.title}`
);
        card.innerHTML = `
            <div class="track-left">
                <img src="${track.album_art}" alt="${track.title}" />
                <div class="track-info">
                    <h3>${track.title}</h3>
                    <p>${track.artist} • ${track.album || mood}</p>
                </div>
            </div>
            <div class="track-actions">
                <div class="track-like" title="Save to Favourites" onclick="event.stopPropagation(); handleFavToggle('${track.id}')">
                    ${track.is_favourite ? '❤️' : '🤍'}
                </div>
                <div class="track-play" onclick="event.stopPropagation(); playTrackById('${track.id}')">▶</div>
            </div>
        `;

        card.addEventListener('click', () => playTrack(track, true));
        trackListContainer.appendChild(card);
    });
}

function playTrackById(trackId) {
    const track = currentPlaylist.find(t => t.id === trackId);
    if (track) playTrack(track, true);
}

function playTrack(track, autoStart = true) {
    currentTrack = track;

    // Highlight active track card
    document.querySelectorAll('.track-card').forEach(card => {
        card.classList.toggle('active', card.getAttribute('data-id') === track.id);
    });

    // Update Player Info Banner & Links
    const nowPlayingTitle = document.getElementById('nowPlayingTitle');
    const nowPlayingArtist = document.getElementById('nowPlayingArtist');
    const nowPlayingArt = document.getElementById('nowPlayingArt');
    const youtubeDirectBtn = document.getElementById('youtubeDirectBtn');

    if (nowPlayingTitle) nowPlayingTitle.textContent = track.title;
    if (nowPlayingArtist) nowPlayingArtist.textContent = track.artist;
    if (nowPlayingArt) nowPlayingArt.src = track.album_art;

    if (youtubeDirectBtn && track.youtube_id) {
        youtubeDirectBtn.href = `https://www.youtube.com/watch?v=${track.youtube_id}`;
    }

    if (audioPlayer && track.preview_url) {
        audioPlayer.src = track.preview_url;
        if (autoStart) {
            audioPlayer.play().then(() => {
                isPlaying = true;
                updatePlayPauseButton();
            }).catch(err => console.error("Audio playback error:", err));
        } else {
            isPlaying = false;
            updatePlayPauseButton();
        }
    }
}

function toggleAudioPlay() {
    if (!audioPlayer || !audioPlayer.src) return;

    if (isPlaying) {
        audioPlayer.pause();
        isPlaying = false;
    } else {
        audioPlayer.play();
        isPlaying = true;
    }
    updatePlayPauseButton();
}

function updatePlayPauseButton() {
    const btnPlayPause = document.getElementById('btnPlayPauseAudio');
    if (btnPlayPause) {
        btnPlayPause.textContent = isPlaying ? '⏸' : '▶';
    }
}

function updateAudioProgress() {
    if (!audioPlayer || isNaN(audioPlayer.duration)) return;

    const currentTime = audioPlayer.currentTime;
    const duration = audioPlayer.duration;
    const seekSlider = document.getElementById('audioSeekSlider');
    const timeDisplay = document.getElementById('audioCurrentTime');
    const durationDisplay = document.getElementById('audioTotalDuration');

    if (seekSlider) {
        seekSlider.value = (currentTime / duration) * 100;
    }
    if (timeDisplay) {
        timeDisplay.textContent = formatTime(currentTime);
    }
    if (durationDisplay) {
        durationDisplay.textContent = formatTime(duration);
    }
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function onTrackEnded() {
    isPlaying = false;
    updatePlayPauseButton();
    // Auto-advance to next track in playlist
    if (currentPlaylist && currentPlaylist.length > 0) {
        const currentIndex = currentPlaylist.findIndex(t => t.id === currentTrack.id);
        const nextIndex = (currentIndex + 1) % currentPlaylist.length;
        playTrack(currentPlaylist[nextIndex], true);
    }
}

async function handleFavToggle(trackId) {
    const track = currentPlaylist.find(t => t.id === trackId);
    if (!track) return;

    try {
        const response = await fetch('/api/favourites/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                song_id: track.id,
                title: track.title,
                artist: track.artist,
                mood: currentTrack ? currentTrack.mood || 'Neutral' : 'Neutral',
                youtube_id: track.youtube_id,
                album_art: track.album_art
            })
        });

        const data = await response.json();
        if (data.success) {
            track.is_favourite = data.is_favourite;
            renderTrackList(currentPlaylist, 'Neutral');
        } else if (response.status === 401) {
            alert("Please log in or register to save songs to your Favourites!");
            if (window.openAuthModal) window.openAuthModal('login');
        }
    } catch (err) {
        console.error("Error toggling favourite:", err);
    }
}