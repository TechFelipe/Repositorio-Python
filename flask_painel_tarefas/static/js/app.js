(function () {
    const key = "taskpanel-theme";
    const body = document.body;
    const button = document.getElementById("themeToggle");

    function aplicarTema(tema) {
        const escuro = tema === "dark";
        body.classList.toggle("dark-mode", escuro);

        if (button) {
            button.innerHTML = escuro
                ? '<i class="bi bi-sun"></i>'
                : '<i class="bi bi-moon-stars"></i>';
            button.title = escuro ? "Ativar modo claro" : "Ativar modo escuro";
        }
    }

    const salvo = localStorage.getItem(key) || "light";
    aplicarTema(salvo);

    if (button) {
        button.addEventListener("click", () => {
            const novo = body.classList.contains("dark-mode") ? "light" : "dark";
            localStorage.setItem(key, novo);
            aplicarTema(novo);
        });
    }
})();
