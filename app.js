const API_URL = 'http://127.0.0.1:5000/incidentes';

const form = document.getElementById('incident-form');
const tableBody = document.getElementById('table-body');
const idInput = document.getElementById('incidente-id');
const btnCancelar = document.getElementById('btn-cancelar');
const formTitle = document.getElementById('form-title');

form.addEventListener('submit', salvarIncidente);
btnCancelar.addEventListener('click', resetarFormulario);
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

    const payload = {
        titulo: document.getElementById('titulo').value,
        categoria: document.getElementById('categoria').value,
        status: document.getElementById('status').value,
        descricao: document.getElementById('descricao').value
    };

    const id = idInput.value;
    const isEdicao = id !== "";
    const method = isEdicao ? 'PUT' : 'POST';
    const url = isEdicao ? `${API_URL}/${id}` : API_URL;

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.erro || 'Erro ao salvar incidente');
        }

        resetarFormulario();
        listarIncidentes();
    } catch (error) {
        console.error(error);
        alert(`Ocorreu um erro: ${error.message}`);
    }
}

async function deletarIncidente(id) {
    if (!confirm('Deseja realmente excluir este incidente?')) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Erro ao excluir incidente (Rota DELETE existe no Flask?)');
        
        listarIncidentes();
    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

function prepararEdicao(id, titulo, categoria, status, descricao) {
    formTitle.textContent = 'Editar Incidente';
    idInput.value = id;
    document.getElementById('titulo').value = titulo;
    document.getElementById('categoria').value = categoria;
    document.getElementById('status').value = status;
    document.getElementById('descricao').value = descricao;
    
    btnCancelar.style.display = 'block';
    document.getElementById('titulo').focus();
}

function resetarFormulario() {
    form.reset();
    idInput.value = '';
    formTitle.textContent = 'Registrar Incidente';
    btnCancelar.style.display = 'none';
}

function renderizarTabela(incidentes) {
    tableBody.innerHTML = '';

    if (incidentes.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Nenhum incidente registrado.</td></tr>';
        return;
    }

    incidentes.forEach(incidente => {
        const tr = document.createElement('tr');
        
        tr.innerHTML = `
            <td>#${incidente.id}</td>
            <td>${incidente.titulo}</td>
            <td>${incidente.categoria}</td>
            <td><span class="badge badge-${incidente.status.replace(' ', '')}">${incidente.status}</span></td>
            <td style="max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${incidente.descricao}">
                ${incidente.descricao}
            </td>
            <td>
                <button class="action-btn btn-edit" onclick="prepararEdicao('${incidente.id}', '${incidente.titulo}', '${incidente.categoria}', '${incidente.status}', '${incidente.descricao}')">Editar</button>
                <button class="action-btn btn-delete" onclick="deletarIncidente('${incidente.id}')">Excluir</button>
            </td>
        `;
        tableBody.appendChild(tr);
    });
}
