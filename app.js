const API_URL = 'http://127.0.0.1:5000/incidentes';

const form = document.getElementById('incident-form');
const tableBody = document.getElementById('table-body');

form.addEventListener('submit', salvarIncidente);
document.addEventListener('DOMContentLoaded', listarIncidentes);

async function listarIncidentes() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error('Erro ao buscar incidentes');
        
        const incidentes = await response.json();
        renderizarTabela(incidentes);
    } catch (error) {
        console.error(error);
        tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: red;">Erro ao carregar os dados.</td></tr>';
    }
}

async function salvarIncidente(e) {
    e.preventDefault();

    // Removemos o campo status daqui, o backend cuida de forçar "Aberto"
    const payload = {
        titulo: document.getElementById('titulo').value,
        categoria: document.getElementById('categoria').value,
        descricao: document.getElementById('descricao').value
    };

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.erro || 'Erro ao salvar incidente');
        }

        form.reset(); 
        listarIncidentes(); 
    } catch (error) {
        console.error(error);
        alert(`Ocorreu um erro: ${error.message}`);
    }
}

// Nova função para a rota PATCH
async function atualizarStatus(id, novoStatus) {
    if (!novoStatus) return;

    try {
        const response = await fetch(`${API_URL}/${id}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: novoStatus })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.erro || 'Erro ao atualizar status');
        }

        listarIncidentes(); // Recarrega a tabela para atualizar a cor do badge
    } catch (error) {
        console.error(error);
        alert(`Erro ao mudar status: ${error.message}`);
        listarIncidentes(); // Volta a tabela ao estado original se der erro
    }
}

function renderizarTabela(incidentes) {
    tableBody.innerHTML = '';

    if (incidentes.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Nenhum incidente registrado.</td></tr>';
        return;
    }

    incidentes.forEach(incidente => {
        const tr = document.createElement('tr');
        const statusClass = incidente.status.replace(' ', '');

        tr.innerHTML = `
            <td>#${incidente.id}</td>
            <td>${incidente.titulo}</td>
            <td>${incidente.categoria}</td>
            <td style="max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${incidente.descricao}">
                ${incidente.descricao}
            </td>
            <td><span class="badge badge-${statusClass}">${incidente.status}</span></td>
            <td>
                <!-- Chama o PATCH automaticamente ao mudar o valor -->
                <select class="status-select" onchange="atualizarStatus(${incidente.id}, this.value)">
                    <option value="" disabled selected>Alterar status...</option>
                    <option value="Aberto">Aberto</option>
                    <option value="Em Análise">Em Análise</option>
                    <option value="Resolvido">Resolvido</option>
                </select>
            </td>
        `;
        tableBody.appendChild(tr);
    });
}