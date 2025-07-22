document.addEventListener('DOMContentLoaded', function() {
    console.log('=== RAT JS CARREGADO ===');

    // Elementos do DOM
    const form = document.getElementById('ratForm');
    const formTitle = document.getElementById('formTitle');
    const submitBtn = document.getElementById('submitBtn');
    const ratIdField = document.getElementById('rat_id');
    const cancelBtn = document.getElementById('cancelEdit');
    const limparBtn = document.getElementById('limparForm');
    const listContainer = document.getElementById('rat-list-container');
    const clienteSelect = document.getElementById('cliente');

    if (!form || !listContainer || !clienteSelect) {
        console.error('Elementos essenciais do formulário RAT não encontrados!');
        return;
    }

    const CREATE_URL = form.action;
    const UPDATE_URL_TEMPLATE = listContainer.dataset.updateUrlTemplate;
    const GET_CLIENT_URL_TEMPLATE = clienteSelect.dataset.getClienteUrlTemplate;

    // --- FUNÇÕES ---

    /**
     * Reseta o formulário para o modo de criação.
     */
    function resetFormToCreateMode() {
        console.log('Resetando formulário RAT...');
        form.reset();
        ratIdField.value = '';
        formTitle.textContent = 'Novo RAT';
        submitBtn.textContent = 'Salvar';
        submitBtn.className = 'btn-primary';
        cancelBtn.style.display = 'none';
        form.action = CREATE_URL;
        
        // Limpa campos de cliente que são readonly
        const clientFields = ['cliente_nome', 'cliente_cpf_cnpj', 'cliente_telefone', 'cliente_celular', 'cliente_email', 'cliente_endereco', 'cliente_bairro', 'cliente_cidade', 'cliente_cep'];
        clientFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) field.value = '';
        });
        
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function setClienteFieldsReadonly(readonly) {
        const clientFields = ['cliente_nome', 'cliente_cpf_cnpj', 'cliente_telefone', 'cliente_celular', 'cliente_email', 'cliente_endereco', 'cliente_bairro', 'cliente_cidade', 'cliente_cep'];
        clientFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) field.readOnly = readonly;
        });
    }

    /**
     * Busca e preenche os dados do cliente selecionado.
     * @param {string} clienteId - O ID do cliente.
     */
    function fetchAndFillClienteData(clienteId) {
        if (!clienteId) return;
        const fetchUrl = GET_CLIENT_URL_TEMPLATE.replace('0', clienteId);
        fetch(fetchUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.cliente) {
                    document.getElementById('cliente_nome').value = data.cliente.nome || '';
                    document.getElementById('cliente_cpf_cnpj').value = data.cliente.cpf_cnpj || '';
                    document.getElementById('cliente_telefone').value = data.cliente.telefone || '';
                    document.getElementById('cliente_celular').value = data.cliente.celular || '';
                    document.getElementById('cliente_email').value = data.cliente.email || '';
                    document.getElementById('cliente_endereco').value = data.cliente.endereco || '';
                    document.getElementById('cliente_bairro').value = data.cliente.bairro || '';
                    document.getElementById('cliente_cidade').value = data.cliente.cidade || '';
                    document.getElementById('cliente_cep').value = data.cliente.cep || '';
                }
            });
    }

    /**
     * Função global para carregar os dados de um RAT no formulário.
     * @param {string} ratId - O ID do RAT.
     */
    window.carregarRat = function(ratId) {
        console.log(`Carregando RAT ID: ${ratId}`);
        const GET_RAT_URL_TEMPLATE = listContainer.dataset.getUrlTemplate;
        const fetchUrl = GET_RAT_URL_TEMPLATE.replace('0', ratId);

        formTitle.textContent = 'Carregando...';
        
        fetch(fetchUrl)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const rat = data.rat;
                    // Preenche todos os campos do formulário
                    for (const key in rat) {
                        const field = document.getElementById(key);
                        if (field) {
                            field.value = rat[key];
                        }
                    }
                    // O campo 'cliente' é um select, então tratamos separadamente
                    document.getElementById('cliente').value = rat.cliente_id;

                    // --- CARREGA EQUIPAMENTOS ---
                    if (Array.isArray(data.equipamentos)) {
                        equipamentosContainer.innerHTML = '';
                        data.equipamentos.forEach(eq => {
                            window.addEquipamentoBlock(eq);
                        });
                    }

                    // Atualiza a UI para o modo de edição
                    ratIdField.value = rat.id;
                    formTitle.textContent = `Editar RAT: ${rat.numero_rat}`;
                    submitBtn.textContent = 'Atualizar';
                    form.action = UPDATE_URL_TEMPLATE.replace('0', rat.id);
                    cancelBtn.style.display = 'inline-block';
                    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
                } else {
                    // alert(`Erro ao carregar RAT: ${data.error}`);
                    console.error(`Erro ao carregar RAT: ${data.error}`);
                    formTitle.textContent = 'Novo RAT';
                }
            })
            .catch(error => {
                console.error('Erro na requisição:', error);
                // alert(`Erro ao carregar RAT: ${error.message}`);
                formTitle.textContent = 'Novo RAT';
            });
    }

    // --- BUSCA AJAX COM DEBOUNCE ---
    function performSearch() {
        const searchNameInput = document.getElementById('search-name-input');
        const searchRatInput = document.getElementById('search-rat-input');
        const resultsContainer = document.getElementById('rat-list-results');
        const searchName = searchNameInput ? searchNameInput.value : '';
        const searchRat = searchRatInput ? searchRatInput.value : '';
        const url = `${window.location.pathname}?search_name=${encodeURIComponent(searchName)}&search_rat=${encodeURIComponent(searchRat)}`;
        resultsContainer.innerHTML = '<div class="p-6 text-center text-gray-500">Buscando...</div>';
        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.text())
            .then(html => {
                resultsContainer.innerHTML = html;
            })
            .catch(error => {
                console.error('Erro na busca AJAX:', error);
                resultsContainer.innerHTML = '<div class="p-6 text-center text-red-500">Erro ao buscar resultados.</div>';
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
    const searchNameInput = document.getElementById('search-name-input');
    const searchRatInput = document.getElementById('search-rat-input');
    if (searchNameInput) searchNameInput.addEventListener('input', debouncedSearch);
    if (searchRatInput) searchRatInput.addEventListener('input', debouncedSearch);

    // --- CLIQUE NA LISTA CARREGA RAT ---
    const resultsContainer = document.getElementById('rat-list-results');
    resultsContainer.addEventListener('click', function(event) {
        const item = event.target.closest('.rat-item');
        if (item && item.dataset.id) {
            window.carregarRat(item.dataset.id);
        }
    });

    // --- EQUIPAMENTOS DINÂMICOS ---
    const equipamentosContainer = document.getElementById('equipamentos-container');
    const equipamentoTemplate = document.getElementById('equipamento-template');
    const addEquipamentoBtn = document.getElementById('adicionar-equipamento');

    function addEquipamentoBlock(data) {
        const clone = equipamentoTemplate.cloneNode(true);
        clone.classList.remove('hidden');
        clone.removeAttribute('id');
        // Preenche os campos se data for fornecida
        if (data) {
            const fields = ['equipamento', 'fabricante', 'modelo', 'numero_serie', 'data_instalacao', 'data_compra'];
            fields.forEach((field, idx) => {
                const input = clone.querySelector(`[name='${field}[]']`);
                if (input && data[field] !== undefined && data[field] !== null) {
                    input.value = data[field];
                }
            });
        }
        // Botão remover
        clone.querySelector('.remover-equipamento').addEventListener('click', function() {
            clone.remove();
        });
        equipamentosContainer.appendChild(clone);
    }
    window.addEquipamentoBlock = addEquipamentoBlock;

    addEquipamentoBtn.addEventListener('click', function() {
        addEquipamentoBlock();
    });

    // Adiciona pelo menos um bloco ao abrir o form
    if (equipamentosContainer.childElementCount === 0) {
        addEquipamentoBlock();
    }

    // --- GARANTE QUE O CONTAINER DE EQUIPAMENTOS ESTÁ DENTRO DO FORM ---
    if (equipamentosContainer && form && equipamentosContainer.parentElement !== form) {
        form.insertBefore(equipamentosContainer, form.querySelector('.border-t.pt-6.mb-6 + .border-t.pt-6.mb-6, .flex.justify-end.mt-6'));
    }

    // --- EVENT LISTENERS ---

    limparBtn.addEventListener('click', resetFormToCreateMode);
    cancelBtn.addEventListener('click', () => window.location.reload());

    // Função para listener simples: preenche só nome e cpf/cnpj
    function bindClienteSelectListenerSimples() {
        const clienteSelect = document.getElementById('cliente');
        if (!clienteSelect) {
            console.error('Campo #cliente não encontrado!');
            return;
        }
        const GET_CLIENT_URL_TEMPLATE = clienteSelect.dataset.getClienteUrlTemplate;
        if (!GET_CLIENT_URL_TEMPLATE) {
            console.error('Atributo data-get-cliente-url-template não encontrado no select!');
            return;
        }
        clienteSelect.addEventListener('change', function(e) {
            const clienteId = e.target.value;
            if (clienteId) {
                const url = GET_CLIENT_URL_TEMPLATE.replace('0', clienteId);
                fetch(url)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.cliente) {
                            document.getElementById('cliente_nome').value = data.cliente.nome || '';
                            document.getElementById('cliente_cpf_cnpj').value = data.cliente.cpf_cnpj || '';
                            console.log('Preencheu nome/cpf_cnpj:', data.cliente.nome, data.cliente.cpf_cnpj);
                        } else {
                            document.getElementById('cliente_nome').value = '';
                            document.getElementById('cliente_cpf_cnpj').value = '';
                            console.warn('Cliente não encontrado ou erro no JSON:', data);
                        }
                    })
                    .catch(error => {
                        document.getElementById('cliente_nome').value = '';
                        document.getElementById('cliente_cpf_cnpj').value = '';
                        console.error('Erro ao buscar dados do cliente:', error);
                    });
            } else {
                document.getElementById('cliente_nome').value = '';
                document.getElementById('cliente_cpf_cnpj').value = '';
            }
        });
    }
    // Chama ao carregar
    bindClienteSelectListenerSimples();

    // --- CLIQUE NA LISTA CARREGA RAT ---
    // document.getElementById('rat-list-results').addEventListener('click', function(event) {
    //     const item = event.target.closest('.rat-item');
    //     if (item && item.dataset.id) {
    //         window.carregarRat(item.dataset.id);
    //     }
    // });

    form.addEventListener('submit', function() {
        console.log('Formulário RAT submetido.');
        // Permite o envio padrão do formulário
    });

    console.log('=== RAT JS INICIALIZADO ===');
}); 