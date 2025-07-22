document.addEventListener('DOMContentLoaded', function() {
    console.log('=== JAVASCRIPT CARREGADO ===');
    
    // Elementos do DOM
    const form = document.getElementById('estoqueForm');
    const formTitle = document.getElementById('formTitle');
    const submitBtn = document.getElementById('submitBtn');
    const estoqueIdField = document.getElementById('estoque_id');
    const cancelBtn = document.getElementById('cancelEdit');
    const limparBtn = document.getElementById('limparForm');
    const listContainer = document.getElementById('estoque-list-container');

    console.log('Elementos encontrados:', {
        form: !!form,
        formTitle: !!formTitle,
        submitBtn: !!submitBtn,
        estoqueIdField: !!estoqueIdField,
        listContainer: !!listContainer
    });

    if (!form || !listContainer) {
        console.error('Elementos essenciais não encontrados!');
        return;
    }

    const CREATE_URL = form.action;
    const UPDATE_URL_TEMPLATE = listContainer.dataset.updateUrlTemplate;
    const GET_ESTOQUE_URL_TEMPLATE = listContainer.dataset.getUrlTemplate;
    
    console.log('URLs configuradas:', {
        CREATE_URL,
        UPDATE_URL_TEMPLATE,
        GET_ESTOQUE_URL_TEMPLATE
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
            'id_registro', 'codigo', 'modelo', 'fornecedor', 
            'data_entrada', 'nome_peca', 'descricao'
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
        
        // Limpa o status display
        const statusDisplay = document.getElementById('status_display');
        if (statusDisplay) {
            statusDisplay.textContent = '';
        }
        
        // Limpa os radio buttons
        document.querySelectorAll('input[name="status"]').forEach(radio => {
            radio.checked = false;
        });
        
        // Reseta o formulário (pode ser redundante, mas é uma boa prática)
        if(form) form.reset();

        // Reseta os campos e botões específicos da interface
        if(estoqueIdField) estoqueIdField.value = '';
        if(formTitle) formTitle.textContent = 'Nova Peça';
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

    // Event listeners
    if (limparBtn) limparBtn.addEventListener('click', resetFormToCreateMode);

    // O botão "Voltar" (cancelBtn) agora simplesmente recarrega a página.
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            console.log('Botão Voltar clicado. Recarregando a página...');
            window.location.reload();
        });
    }

    /**
     * Lida com a submissão do formulário.
     */
    form.addEventListener('submit', function(e) {
        console.log('Formulário submetido - redirecionamento normal');
        
        // Remove o preventDefault para permitir o submit normal
        // e.preventDefault();
        
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

    console.log('=== JAVASCRIPT INICIALIZADO COMPLETAMENTE ===');
}); 