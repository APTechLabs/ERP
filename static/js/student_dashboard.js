const menuItems = document.querySelectorAll(".menu");
const sections = document.querySelectorAll(".section");

menuItems.forEach(item => {
    item.addEventListener("click", e => {
        e.preventDefault();

        menuItems.forEach(i => i.classList.remove("active"));
        item.classList.add("active");

        sections.forEach(sec => sec.classList.remove("active"));
        document.getElementById(item.dataset.target).classList.add("active");
    });
});
