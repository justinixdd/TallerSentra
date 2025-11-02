// =======================
// NAVBAR INTERACTIVO SENTRA
// =======================

// ----- ABRIR/CERRAR MENÚ LATERAL -----
const body = document.querySelector("body"),
  nav = document.querySelector("nav"),
  sidebarOpen = document.querySelector(".sidebarOpen"),
  sidebarClose = document.querySelector(".siderbarClose"),
  darkLight = document.querySelector(".dark-light"),
  darkLightLogo = document.querySelector(".darkLightLogo");

// abrir menú móvil
sidebarOpen.addEventListener("click", () => {
  nav.classList.add("active");
});

// cerrar menú móvil
sidebarClose.addEventListener("click", () => {
  nav.classList.remove("active");
});

// cerrar menú si se hace clic fuera
body.addEventListener("click", e => {
  let clickedElm = e.target;
  if (!clickedElm.classList.contains("sidebarOpen") && !clickedElm.closest(".menu")) {
    nav.classList.remove("active");
  }
});

// =======================
// MODO OSCURO / CLARO
// =======================
const currentTheme = localStorage.getItem("theme");

if (currentTheme === "dark") {
  body.classList.add("dark");
  darkLight.classList.add("active");
  darkLightLogo.classList.add("active");
}

darkLight.addEventListener("click", () => {
  darkLight.classList.toggle("active");
  body.classList.toggle("dark");
  darkLightLogo.classList.toggle("active");

  if (body.classList.contains("dark")) {
    localStorage.setItem("theme", "dark");
  } else {
    localStorage.setItem("theme", "light");
  }
});

// =======================
// DESPLEGAR LOGIN / REGISTER
// =======================
const searchToggle = document.querySelector(".searchToggle");
const searchField = document.querySelector(".search-field");

// al hacer clic en el ícono de usuario
searchToggle.addEventListener("click", (e) => {
  e.stopPropagation(); // evita cerrar al hacer clic dentro
  searchToggle.classList.toggle("active");
});

// cerrar el menú si se hace clic fuera
document.addEventListener("click", (e) => {
  if (!searchToggle.contains(e.target) && !searchField.contains(e.target)) {
    searchToggle.classList.remove("active");
  }
});
