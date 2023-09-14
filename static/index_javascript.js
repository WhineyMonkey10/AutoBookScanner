document.addEventListener("DOMContentLoaded", function () {
    const modalTriggers = document.querySelectorAll("[data-toggle='modal']");
    const closeButtons = document.querySelectorAll(".close-modal");

    modalTriggers.forEach((trigger) => {
        trigger.addEventListener("click", () => {
            const modalId = trigger.getAttribute("data-target");
            const modal = document.querySelector(modalId);
            modal.style.display = "block";
        });
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const modal = button.parentElement;
            modal.style.display = "none";
        });
    });

    window.addEventListener("click", (event) => {
        if (event.target.classList.contains("modal")) {
            event.target.style.display = "none";
        }
    });
});
