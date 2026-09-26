const moodButtons = document.querySelectorAll(".mood-btn");

moodButtons.forEach(button => {

    button.addEventListener("click", () => {

        moodButtons.forEach(btn =>
            btn.classList.remove("active")
        );

        button.classList.add("active");

        const mood = button.dataset.mood;

        loadRecommendationsForMood(mood);

    });

});