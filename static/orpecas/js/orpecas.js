document.addEventListener('DOMContentLoaded', function() {
    console.log('=== ORPECAS JS CARREGADO ===');

    // --- ELEMENTOS DO DOM ---
    const form = document.getElementById('orpecasForm');
    if (!form) return;

    const formTitle = document.getElementById('formTitle');
    const submitBtn = document.getElementById('submitBtn');
    const orpecasIdField = document.getElementById('orpecas_id');
    const cancelBtn = document.getElementById('cancelEdit');
    const limparBtn = document.getElementById('limparForm');
    const addItemBtn = document.getElementById('adicionar-item');
    const itensContainer = document.getElementById('itens-container');
    const descontoInput = document.getElementById('valor_desconto');
    const listContainer = document.getElementById('orpecas-list-container');
    
    const CREATE_URL = form.action;
    const UPDATE_URL_TEMPLATE = listContainer.dataset.updateUrlTemplate;
    const GET_ORPECAS_URL_TEMPLATE = listContainer.dataset.getUrlTemplate;

    // --- FUNÇÕES ---

    /**
     * Reseta o formulário para o estado inicial.
     */
    function resetFormToCreateMode() {
        form.reset();
        orpecasIdField.value = '';
        formTitle.textContent = 'Novo Orçamento de Peças';
        submitBtn.textContent = 'Salvar';
        cancelBtn.style.display = 'none';
        form.action = CREATE_URL;
        itensContainer.innerHTML = '';
        addItemBtn.click(); // Adiciona uma linha inicial
        calculateTotals();
        form.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Calcula os totais do orçamento.
     */
    function calculateTotals() {
        let total = 0;
        const itemRows = itensContainer.querySelectorAll('.item-row');
        itemRows.forEach(row => {
            const qtd = parseFloat(row.querySelector('.item-qtd').value) || 0;
            const valor = parseFloat(row.querySelector('.item-valor').value) || 0;
            const itemTotal = qtd * valor;
            row.querySelector('.item-total').textContent = itemTotal.toFixed(2);
            total += itemTotal;
        });
        
        const totalInput = document.getElementById('valor_total');
        const totalComDescontoInput = document.getElementById('valor_total_com_desconto');
        
        totalInput.value = total.toFixed(2);
        const desconto = parseFloat(descontoInput.value) || 0;
        totalComDescontoInput.value = (total - desconto).toFixed(2);
    }

    /**
     * Cria uma nova linha de item no formulário.
     */
    function createItemRow(item = {}) {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'item-row grid grid-cols-12 gap-2 items-center mb-2';
        itemDiv.innerHTML = `
            <div class="col-span-1">
                <input type="number" name="quantidade[]" value="${item.quantidade || 1}" class="item-qtd w-full p-1 border border-gray-300 rounded-md text-sm" placeholder="Qtd">
            </div>
            <div class="col-span-6">
                <input type="text" name="produto[]" value="${item.produto || ''}" class="w-full p-1 border border-gray-300 rounded-md text-sm" placeholder="Produto" required>
            </div>
            <div class="col-span-2">
                <input type="number" step="0.01" name="valor_unitario[]" value="${item.valor_unitario || ''}" class="item-valor w-full p-1 border border-gray-300 rounded-md text-sm" placeholder="Vlr. Unit.">
            </div>
            <div class="col-span-2 text-center">
                <span class="item-total font-semibold">0.00</span>
            </div>
            <div class="col-span-1 flex justify-center">
                <button type="button" class="remover-item text-red-500 hover:text-red-700">✖</button>
            </div>
        `;

        itemDiv.querySelector('.remover-item').addEventListener('click', () => {
            itemDiv.remove();
            calculateTotals();
        });

        itemDiv.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', calculateTotals);
        });

        itensContainer.appendChild(itemDiv);
    }

    /**
     * Carrega um orçamento existente no formulário.
     * @param {string} orpecasId - O ID do orçamento.
     */
    window.carregarOrpecas = function(orpecasId) {
        formTitle.textContent = 'Carregando...';
        const fetchUrl = GET_ORPECAS_URL_TEMPLATE.replace('0', orpecasId);
        
        fetch(fetchUrl)
            .then(response => response.json())
            .then(data => {
                // Preenche campos principais
                for (const key in data) {
                    const field = document.getElementById(key);
                    if (field && key !== 'itens') {
                        field.value = data[key];
                    }
                }
                
                // Limpa e preenche os itens
                itensContainer.innerHTML = '';
                if (data.itens && data.itens.length > 0) {
                    data.itens.forEach(item => createItemRow(item));
                } else {
                    addItemBtn.click(); // Adiciona um vazio se não houver
                }
                
                // Atualiza UI para modo de edição
                orpecasIdField.value = data.id;
                formTitle.textContent = `Editar Orçamento: ${data.numero}`;
                submitBtn.textContent = 'Atualizar';
                form.action = UPDATE_URL_TEMPLATE.replace('0', data.id);
                cancelBtn.style.display = 'inline-block';
                
                calculateTotals();
                form.scrollIntoView({ behavior: 'smooth' });
            })
            .catch(error => {
                console.error('Erro ao carregar orçamento:', error);
                alert('Não foi possível carregar os dados do orçamento.');
                formTitle.textContent = 'Novo Orçamento de Peças';
            });
    }

    /**
     * Realiza a busca por AJAX.
     */
    const performSearch = () => {
        const searchName = document.getElementById('search-name-input').value;
        const searchNumero = document.getElementById('search-numero-input').value;
        const resultsContainer = document.getElementById('orpecas-list-results');
        const searchUrl = `${window.location.pathname}?search_name=${encodeURIComponent(searchName)}&search_numero=${encodeURIComponent(searchNumero)}`;

        resultsContainer.innerHTML = '<div class="p-4 text-center">Buscando...</div>';

        fetch(searchUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.json())
            .then(data => {
                resultsContainer.innerHTML = data.html;
            })
            .catch(error => {
                console.error('Erro na busca AJAX:', error);
                resultsContainer.innerHTML = '<div class="p-4 text-center text-red-500">Erro ao buscar.</div>';
            });
    };
    
    const debounce = (func, delay) => {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    };
    const debouncedSearch = debounce(performSearch, 300);

    // --- EVENT LISTENERS ---
    limparBtn.addEventListener('click', resetFormToCreateMode);
    cancelBtn.addEventListener('click', () => window.location.reload());
    addItemBtn.addEventListener('click', () => createItemRow());
    descontoInput.addEventListener('input', calculateTotals);
    document.getElementById('search-name-input').addEventListener('input', debouncedSearch);
    document.getElementById('search-numero-input').addEventListener('input', debouncedSearch);
    form.addEventListener('submit', () => submitBtn.disabled = true);

    // --- INICIALIZAÇÃO ---
    addItemBtn.click(); // Adiciona a primeira linha de item
    console.log('=== ORPECAS JS INICIALIZADO ===');
}); 