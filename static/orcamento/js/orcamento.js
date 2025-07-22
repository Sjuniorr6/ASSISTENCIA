console.log('JavaScript do orçamento carregado!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== JAVASCRIPT INICIALIZADO ===');
    
    // Elementos do DOM
    const form = document.getElementById('orcamentoForm');
    const formTitle = document.getElementById('formTitle');
    const submitBtn = document.getElementById('submitBtn');
    const orcamentoIdField = document.getElementById('orcamento_id');
    const cancelBtn = document.getElementById('cancelEdit');
    const limparBtn = document.getElementById('limparForm');
    const addItemBtn = document.getElementById('adicionar-item');
    const itensContainer = document.getElementById('itens-container');
    const descontoInput = document.getElementById('valor_desconto');

    console.log('Elementos encontrados:', {
        form: !!form,
        formTitle: !!formTitle,
        submitBtn: !!submitBtn,
        orcamentoIdField: !!orcamentoIdField,
        addItemBtn: !!addItemBtn,
        itensContainer: !!itensContainer
    });

    if (!form || !itensContainer) {
        console.error('Elementos essenciais não encontrados!');
        return;
    }

    // Função para obter o token CSRF
    function getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    /**
     * Reseta o formulário para o estado de criação.
     */
    function resetFormToCreateMode() {
        console.log('Resetando formulário para modo criação');
        form.reset();
        orcamentoIdField.value = '';
        formTitle.textContent = 'Novo Orçamento';
        submitBtn.textContent = 'Salvar';
        submitBtn.className = 'btn-primary';
        cancelBtn.style.display = 'none';
        
        // Limpa os itens
        itensContainer.innerHTML = '';
        
        // Adiciona um item vazio
        if (addItemBtn) addItemBtn.click();
    }

    /**
     * Cria uma linha de item do orçamento.
     */
    function createItemRow() {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'grid grid-cols-1 md:grid-cols-5 gap-4 mb-4 items-end';
        itemDiv.innerHTML = `
            <div class="md:col-span-2">
                <input type="text" name="produto[]" class="w-full px-3 py-2 border border-gray-300 rounded-md" placeholder="Produto" required>
            </div>
            <div>
                <input type="number" name="quantidade[]" value="1" class="item-qtd w-full px-3 py-2 border border-gray-300 rounded-md" placeholder="Qtd" required>
            </div>
            <div>
                <input type="number" step="0.01" name="valor_unitario[]" class="item-valor w-full px-3 py-2 border border-gray-300 rounded-md" placeholder="Vlr Unit." required>
            </div>
            <div class="flex items-end">
                <button type="button" class="remover-item px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700">X</button>
            </div>
        `;

        itemDiv.querySelector('.remover-item').addEventListener('click', () => {
            itemDiv.remove();
            calculateTotals();
        });

        itemDiv.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', () => calculateTotals());
        });

        return itemDiv;
    }

    /**
     * Calcula os totais do orçamento.
     */
    function calculateTotals() {
        let total = 0;
        const itemRows = document.querySelectorAll('#itens-container .grid');
        itemRows.forEach(row => {
            const qtd = parseFloat(row.querySelector('.item-qtd').value) || 0;
            const valor = parseFloat(row.querySelector('.item-valor').value) || 0;
            total += qtd * valor;
        });
        
        const totalInput = document.getElementById('valor_total');
        const descontoInput = document.getElementById('valor_desconto');
        const totalComDescontoInput = document.getElementById('valor_total_com_desconto');
        
        totalInput.value = total.toFixed(2);
        const desconto = parseFloat(descontoInput.value) || 0;
        totalComDescontoInput.value = (total - desconto).toFixed(2);
    }

    // Event listeners
    if (limparBtn) limparBtn.addEventListener('click', resetFormToCreateMode);
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            console.log('Botão Voltar clicado. Recarregando a página...');
            window.location.reload();
        });
    }
    
    if (addItemBtn) {
        addItemBtn.addEventListener('click', () => {
            itensContainer.appendChild(createItemRow());
            calculateTotals();
        });
    }
    
    if (descontoInput) {
        descontoInput.addEventListener('input', () => calculateTotals());
    }

    /**
     * Lida com a submissão do formulário.
     */
    form.addEventListener('submit', function(e) {
        console.log('Formulário submetido - redirecionamento normal');
        
        // Adiciona CSRF token se necessário
        const csrfToken = getCSRFToken();
        if (csrfToken && !form.querySelector('[name=csrfmiddlewaretoken]')) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken;
            form.appendChild(csrfInput);
        }
        
        // O formulário será submetido normalmente e a página será redirecionada
        // A view do Django irá processar e redirecionar de volta para a mesma página
    });

    // Adiciona um item inicial
    if (addItemBtn) addItemBtn.click();
    
    console.log('=== JAVASCRIPT INICIALIZADO COMPLETAMENTE ===');
}); 