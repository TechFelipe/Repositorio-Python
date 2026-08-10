let progressChart;

function classeStatus(status) {
    return status.toLowerCase()
        .replaceAll(" ", "-")
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function escaparHtml(texto) {
    const div = document.createElement("div");
    div.textContent = texto ?? "";
    return div.innerHTML;
}

function renderTasks(tasks) {
    const list = document.getElementById("taskList");

    if (!tasks.length) {
        list.innerHTML = `
            <div id="emptyState" class="text-center py-5 text-secondary">
                <i class="bi bi-inbox display-5"></i>
                <p class="mt-2 mb-0">Nenhuma tarefa encontrada para este filtro.</p>
            </div>`;
        return;
    }

    list.innerHTML = tasks.map(task => `
        <div class="task-card status-${classeStatus(task.status)}" data-task-id="${task.id}">
            <div class="d-flex justify-content-between align-items-start gap-3">
                <div>
                    <h5 class="fw-bold mb-1">${escaparHtml(task.titulo)}</h5>
                    <p class="text-secondary mb-2">${escaparHtml(task.descricao || "Sem descrição.")}</p>
                    <span class="badge status-badge">${escaparHtml(task.status)}</span>
                </div>
                <div class="d-flex gap-1">
                    <a href="/editar/${task.id}" class="btn btn-sm btn-outline-primary" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </a>
                    <button class="btn btn-sm btn-outline-danger" title="Excluir"
                            onclick="excluirPorApi(${task.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join("");
}

async function carregarTarefas(status = "") {
    const loading = document.getElementById("filterLoading");
    loading.classList.remove("d-none");

    try {
        const url = status
            ? `/api/tarefas?status=${encodeURIComponent(status)}`
            : "/api/tarefas";

        const resposta = await fetch(url);
        if (!resposta.ok) throw new Error("Falha ao carregar tarefas.");

        const tarefas = await resposta.json();
        renderTasks(tarefas);
    } catch (erro) {
        console.error(erro);
        document.getElementById("taskList").innerHTML =
            '<div class="alert alert-danger">Não foi possível carregar as tarefas.</div>';
    } finally {
        loading.classList.add("d-none");
    }
}

async function excluirPorApi(id) {
    if (!confirm("Excluir esta tarefa?")) return;

    const resposta = await fetch(`/api/tarefas/${id}`, {
        method: "DELETE"
    });

    if (resposta.ok) {
        const filtro = document.getElementById("statusFilter").value;
        await carregarTarefas(filtro);
        await carregarProgresso();
    } else {
        alert("Não foi possível excluir a tarefa.");
    }
}

async function carregarProgresso() {
    const resposta = await fetch("/api/progresso");
    if (!resposta.ok) return;

    const dados = await resposta.json();

    const ctx = document.getElementById("progressChart");
    if (progressChart) progressChart.destroy();

    progressChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Pendente", "Em andamento", "Concluída"],
            datasets: [{
                label: "Quantidade de tarefas",
                data: [
                    dados["Pendente"],
                    dados["Em andamento"],
                    dados["Concluída"]
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const filtro = document.getElementById("statusFilter");

    if (filtro) {
        filtro.addEventListener("change", () => {
            carregarTarefas(filtro.value);
        });
    }

    carregarProgresso();
});
