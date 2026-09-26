

document.querySelectorAll(".mood-btn").forEach(button => {
    button.addEventListener("click", () => {
        const mood = button.dataset.mood;

        fetch("/get_songs", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ mood })
        })
        .then(res => res.json())
        .then(data => displaySongs(data));
    });
});