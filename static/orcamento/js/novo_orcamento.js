document.addEventListener('DOMContentLoaded', function() {
    let itemCounter = 0;

    // Adicionar item
    document.getElementById('adicionar-item').addEventListener('click', function() {
        addItem();
    });

    // Calcular totais quando valores mudam
    document.querySelector('input[name="valor_desconto"]').addEventListener('input', calculateTotals);

    // Submeter formulário
    document.getElementById('novoOrcamentoForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitForm();
    });

    function addItem() {
        itemCounter++;
        const container = document.getElementById('itens-container');
        
        const itemDiv = document.createElement('div');
        itemDiv.className = 'grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border border-gray-200 rounded-md';
        itemDiv.innerHTML = `
            <div>
                <label class="block text-sm font-medium text-gray-700">Produto</label>
                <input type="text" name="produto[]" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Quantidade</label>
                <input type="number" name="quantidade[]" min="1" value="1" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Valor Unitário</label>
                <input type="number" name="valor_unitario[]" step="0.01" min="0" required class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
            </div>
            <div class="flex items-end space-x-2">
                <div class="flex-1">
                    <label class="block text-sm font-medium text-gray-700">Valor Total</label>
                    <input type="number" name="valor_total[]" step="0.01" readonly class="mt-1 block w-full rounded-md border-gray-300 shadow-sm bg-gray-50">
                </div>
                <button type="button" class="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700" onclick="this.parentElement.parentElement.remove(); calculateTotals();">
                    ×
                </button>
            </div>
        `;

        container.appendChild(itemDiv);

        // Adicionar event listeners para calcular totais
        const inputs = itemDiv.querySelectorAll('input[name="quantidade[]"], input[name="valor_unitario[]"]');
        inputs.forEach(input => {
            input.addEventListener('input', calculateItemTotal);
        });
    }

    function calculateItemTotal() {
        const itemDiv = this.closest('.grid');
        const quantidade = parseFloat(itemDiv.querySelector('input[name="quantidade[]"]').value) || 0;
        const valorUnitario = parseFloat(itemDiv.querySelector('input[name="valor_unitario[]"]').value) || 0;
        const valorTotal = quantidade * valorUnitario;
        
        itemDiv.querySelector('input[name="valor_total[]"]').value = valorTotal.toFixed(2);
        calculateTotals();
    }

    function calculateTotals() {
        const valorTotalInputs = document.querySelectorAll('input[name="valor_total[]"]');
        let valorTotal = 0;

        valorTotalInputs.forEach(input => {
            valorTotal += parseFloat(input.value) || 0;
        });

        const valorDesconto = parseFloat(document.querySelector('input[name="valor_desconto"]').value) || 0;
        const valorTotalComDesconto = valorTotal - valorDesconto;

        document.querySelector('input[name="valor_total"]').value = valorTotal.toFixed(2);
        document.querySelector('input[name="valor_total_com_desconto"]').value = valorTotalComDesconto.toFixed(2);
    }

    function submitForm() {
        const form = document.getElementById('novoOrcamentoForm');
        const formData = new FormData(form);

        // Coletar dados dos itens
        const itens = [];
        const produtos = formData.getAll('produto[]');
        const quantidades = formData.getAll('quantidade[]');
        const valoresUnitarios = formData.getAll('valor_unitario[]');
        const valoresTotais = formData.getAll('valor_total[]');

        for (let i = 0; i < produtos.length; i++) {
            if (produtos[i] && quantidades[i] && valoresUnitarios[i]) {
                itens.push({
                    produto: produtos[i],
                    quantidade: parseInt(quantidades[i]),
                    valor_unitario: parseFloat(valoresUnitarios[i]),
                    valor_total: parseFloat(valoresTotais[i])
                });
            }
        }

        // Adicionar itens ao FormData
        formData.set('itens', JSON.stringify(itens));

        // Enviar requisição
        fetch('', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Orçamento criado com sucesso!');
                window.location.href = '/orcamento/';
            } else {
                alert('Erro ao criar orçamento: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao criar orçamento. Tente novamente.');
        });
    }

    // Adicionar primeiro item automaticamente
    addItem();
}); 