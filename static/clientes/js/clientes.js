document.addEventListener('DOMContentLoaded', function() {
    console.log('=== JAVASCRIPT CARREGADO ===');
    
    // Elementos do DOM
    const form = document.getElementById('clienteForm');
    const formTitle = document.getElementById('formTitle');
    const submitBtn = document.getElementById('submitBtn');
    const clienteIdField = document.getElementById('cliente_id');
    const cancelBtn = document.getElementById('cancelEdit');
    const limparBtn = document.getElementById('limparForm');
    const listContainer = document.getElementById('client-list-container');
    const resultsContainer = document.getElementById('client-list-results');
    const searchNameInput = document.getElementById('search-name-input');
    const searchOsInput = document.getElementById('search-os-input');

    console.log('Elementos encontrados:', {
        form: !!form,
        formTitle: !!formTitle,
        submitBtn: !!submitBtn,
        clienteIdField: !!clienteIdField,
        listContainer: !!listContainer
    });

    if (!form || !listContainer || !resultsContainer) {
        console.error('Elementos essenciais não encontrados!');
        return;
    }

    const CREATE_URL = form.action;
    const UPDATE_URL_TEMPLATE = listContainer.dataset.updateUrlTemplate;
    const GET_CLIENT_URL_TEMPLATE = listContainer.dataset.getUrlTemplate;
    
    console.log('URLs configuradas:', {
        CREATE_URL,
        UPDATE_URL_TEMPLATE,
        GET_CLIENT_URL_TEMPLATE
    });

    // Função para obter o token CSRF
    function getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    /**
     * Reseta o formulário para o estado de criação de forma explícita.
     */
    function resetFormToCreateMode() {
        console.log('Botão Voltar/Limpar clicado. Resetando formulário...');

        // Lista de todos os campos do formulário que são preenchidos dinamicamente
        const camposParaLimpar = [
            'numero_os', 'data_chamado', 'status_servico', 'nome',
            'cpf_cnpj', 'telefone', 'celular', 'email', 'apto_bloco',
            'endereco', 'bairro', 'cidade', 'cep', 'revendedor',
            'tecnicos', 'periodo', 'data_instalacao', 'valor_total',
            'forma_pagamento', 'servicos', 'relatorios_servicos_prestados'
        ];
        
        // Limpa cada campo individualmente para garantir
        camposParaLimpar.forEach(campoId => {
            const elemento = document.getElementById(campoId);
            if (elemento) {
                if (elemento.tagName.toLowerCase() === 'select') {
                    elemento.selectedIndex = 0; // Para selects, volta para a primeira opção
                } else {
                    elemento.value = ''; // Para inputs e textareas
                }
            }
        });
        
        // Reseta o formulário (pode ser redundante, mas é uma boa prática)
        if(form) form.reset();

        // Reseta os campos e botões específicos da interface
        if(clienteIdField) clienteIdField.value = '';
        if(formTitle) formTitle.textContent = 'Novo Cliente';
        if(submitBtn) {
            submitBtn.textContent = 'Salvar';
            submitBtn.className = 'btn-primary';
        }
        if(cancelBtn) cancelBtn.style.display = 'none';

        // Reseta a URL de action do formulário para a URL de criação
        if (form && CREATE_URL) {
            form.action = CREATE_URL;
        }

        console.log('Formulário resetado para o modo de criação.');
        
        // Rola a página para o topo do formulário para melhor UX
        if (form) form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // --- BUSCA AJAX COM DEBOUNCE ---
    function performSearch() {
        const searchName = searchNameInput ? searchNameInput.value : '';
        const searchOs = searchOsInput ? searchOsInput.value : '';
        const url = `${CREATE_URL}?search_name=${encodeURIComponent(searchName)}&search_os=${encodeURIComponent(searchOs)}`;
        resultsContainer.innerHTML = '<div class="p-4 text-center">Buscando...</div>';
        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.text())
            .then(html => {
                resultsContainer.innerHTML = html;
            })
            .catch(error => {
                console.error('Erro na busca AJAX:', error);
                resultsContainer.innerHTML = '<div class="p-4 text-center text-red-500">Erro ao buscar.</div>';
            });
    }
    const debounce = (func, delay) => {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    };
    const debouncedSearch = debounce(performSearch, 300);
    if (searchNameInput) searchNameInput.addEventListener('input', debouncedSearch);
    if (searchOsInput) searchOsInput.addEventListener('input', debouncedSearch);
                    
    // --- CLIQUE NA LISTA CARREGA CLIENTE ---
    resultsContainer.addEventListener('click', function(event) {
        const item = event.target.closest('.client-list-item');
        if (item && item.dataset.id) {
            carregarCliente(item.dataset.id);
            }
    });

    // --- FUNÇÃO GLOBAL PARA CARREGAR CLIENTE ---
    window.carregarCliente = function(clienteId) {
        if (!GET_CLIENT_URL_TEMPLATE) return;
        const fetchUrl = GET_CLIENT_URL_TEMPLATE.replace('0', clienteId);
        formTitle.textContent = 'Carregando...';
        fetch(fetchUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.cliente) {
                    const cliente = data.cliente;
                    [
                        'numero_os', 'data_chamado', 'status_servico', 'nome',
                        'cpf_cnpj', 'telefone', 'celular', 'email', 'apto_bloco',
                        'endereco', 'bairro', 'cidade', 'cep', 'revendedor',
                        'tecnicos', 'periodo', 'data_instalacao', 'valor_total',
                        'forma_pagamento', 'servicos', 'relatorios_servicos_prestados'
                    ].forEach(campo => {
                        const el = document.getElementById(campo);
                        if (el && cliente[campo] !== undefined && cliente[campo] !== null) {
                            el.value = cliente[campo];
                        }
                    });
                    clienteIdField.value = cliente.id;
                    formTitle.textContent = `Editar Cliente: ${cliente.nome || ''}`;
                    submitBtn.textContent = 'Atualizar';
                    submitBtn.className = 'btn-primary';
                    cancelBtn.style.display = 'inline-block';
                    form.action = UPDATE_URL_TEMPLATE.replace('0', cliente.id);
                    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    alert('Erro ao carregar cliente.');
                    formTitle.textContent = 'Novo Cliente';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar cliente:', error);
                alert('Não foi possível carregar os dados do cliente.');
                formTitle.textContent = 'Novo Cliente';
            });
    };

    // --- RESET FORM ---
    if (limparBtn) limparBtn.addEventListener('click', function() {
        form.reset();
        clienteIdField.value = '';
        formTitle.textContent = 'Novo Cliente';
        submitBtn.textContent = 'Salvar';
        submitBtn.className = 'btn-primary';
        cancelBtn.style.display = 'none';
        form.action = CREATE_URL;
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    if (cancelBtn) cancelBtn.addEventListener('click', function() {
        window.location.reload();
    });
    form.addEventListener('submit', function() {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Salvando...';
    });

    console.log('=== JAVASCRIPT INICIALIZADO COMPLETAMENTE ===');
}); 