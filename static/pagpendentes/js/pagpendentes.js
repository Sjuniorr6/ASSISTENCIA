document.addEventListener('DOMContentLoaded', function() {
    console.log('=== PAGPENDENTES JS CARREGADO ===');

    const detailsSection = document.getElementById('details-section');
    const detailsForm = document.getElementById('payment-details-form');
    const marcarPagoBtn = document.getElementById('marcarPagoBtn');
    const listResultsContainer = document.getElementById('payment-list-results');
    const closeDetailsBtn = document.getElementById('closeDetailsBtn');
    const notificationContainer = document.getElementById('notification-container');
    const confirmModal = document.getElementById('confirm-modal');
    
    let selectedItem = null;

    // Sistema de Notificações Customizado
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        const id = 'notification-' + Date.now();
        notification.id = id;
        
        const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
        const iconColor = type === 'success' ? 'text-green-500' : type === 'error' ? 'text-red-500' : 'text-blue-500';
        const icon = type === 'success' ? 
            '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>' :
            type === 'error' ?
            '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>' :
            '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>';

        notification.className = `${bgColor} text-white px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 ease-in-out translate-x-full`;
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    ${icon}
                </div>
                <div class="ml-3">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <button onclick="document.getElementById('${id}').remove()" class="text-white hover:text-gray-200">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        notificationContainer.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);

        // Auto-remover após 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('translate-x-full');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    // Sistema de Confirmação Customizado
    function showConfirm(message, title = 'Confirmar Ação') {
        return new Promise((resolve) => {
            const confirmTitle = document.getElementById('confirm-title');
            const confirmMessage = document.getElementById('confirm-message');
            const confirmOk = document.getElementById('confirm-ok');
            const confirmCancel = document.getElementById('confirm-cancel');

            confirmTitle.textContent = title;
            confirmMessage.textContent = message;
            
            confirmModal.classList.remove('hidden');

            const handleConfirm = () => {
                confirmModal.classList.add('hidden');
                cleanup();
                resolve(true);
            };

            const handleCancel = () => {
                confirmModal.classList.add('hidden');
                cleanup();
                resolve(false);
            };

            const cleanup = () => {
                confirmOk.removeEventListener('click', handleConfirm);
                confirmCancel.removeEventListener('click', handleCancel);
            };

            confirmOk.addEventListener('click', handleConfirm);
            confirmCancel.addEventListener('click', handleCancel);
        });
    }

    // Função para preencher detalhes
    function fillDetails(item) {
        const data = item.dataset;
        
        // Campos principais
        document.getElementById('details_id').value = data.id;
        document.getElementById('details_content_type').value = data.type;
        document.getElementById('details_tipo_documento').value = data.tipoDocumento || 'N/A';
        document.getElementById('details_data_servico').value = data.dataServico || 'N/A';
        document.getElementById('details_nome').value = data.nome || 'N/A';
        document.getElementById('details_valor_total').value = data.valorTotal || 'N/A';
        document.getElementById('details_status').value = data.status || 'N/A';
        
        // Definir o valor do dropdown baseado no status atual
        const statusSelect = document.getElementById('details_status_select');
        if (data.status && data.status.toLowerCase().includes('pendente')) {
            statusSelect.value = 'pendente_pagamento';
        } else if (data.status && data.status.toLowerCase().includes('pago')) {
            statusSelect.value = 'pago';
        } else {
            statusSelect.value = 'pendente_pagamento';
        }
        
        // Mostrar seção com animação
        detailsSection.style.visibility = 'visible';
        setTimeout(() => {
            detailsSection.classList.add('visible');
        }, 10);
    }

    // Função para fechar detalhes
    function closeDetails() {
        detailsSection.classList.remove('visible');
        setTimeout(() => {
            detailsSection.style.visibility = 'hidden';
        }, 300);
        
        if (selectedItem) {
            selectedItem.classList.remove('selected');
            selectedItem = null;
        }
    }

    // Botão de fechar
    if (closeDetailsBtn) {
        closeDetailsBtn.addEventListener('click', closeDetails);
    }

    // Usar delegação de eventos para itens da lista de pagamento
    if (listResultsContainer) {
        listResultsContainer.addEventListener('click', function(event) {
            const item = event.target.closest('.payment-item');
            if (!item) return;

            if (selectedItem) {
                selectedItem.classList.remove('selected');
            }
            item.classList.add('selected');
            selectedItem = item;

            fillDetails(item);
        });
    }

    // Lógica para 'Atualizar Status'
    if (marcarPagoBtn) {
        marcarPagoBtn.addEventListener('click', async function() {
            if (!selectedItem) {
                showNotification('Por favor, selecione um item da lista primeiro.', 'error');
                return;
            }

            const statusSelect = document.getElementById('details_status_select');
            const newStatus = statusSelect.value;
            
            if (newStatus === 'pago') {
                const confirmed = await showConfirm(
                    'Tem certeza que deseja marcar este pagamento como PAGO? Esta ação não pode ser desfeita.',
                    'Confirmar Pagamento'
                );
                
                if (!confirmed) {
                    return;
                }
            }

            const url = detailsForm.dataset.marcarPagoUrl;
            const formData = new FormData(detailsForm);
            formData.append('new_status', newStatus);
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-CSRFToken': formData.get('csrfmiddlewaretoken') }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const statusText = newStatus === 'pago' ? 'PAGO' : 'Pendente de Pagamento';
                    showNotification(`Status atualizado para ${statusText} com sucesso!`, 'success');
                    
                    if (newStatus === 'pago') {
                        selectedItem.remove();
                        closeDetails();
                    } else {
                        // Atualizar o status na interface
                        selectedItem.dataset.status = statusText;
                        document.getElementById('details_status').value = statusText;
                    }
                } else {
                    showNotification('Erro ao atualizar status: ' + data.error, 'error');
                }
            } catch (error) {
                console.error('Erro na requisição:', error);
                showNotification('Ocorreu um erro de comunicação com o servidor.', 'error');
            }
        });
    }

    // --- Lógica da Busca ---
    const searchNameInput = document.getElementById('search-name-input');
    const searchNumeroInput = document.getElementById('search-numero-input');
    const searchForm = document.getElementById('search-form');

    console.log('Elementos de busca encontrados:', {
        searchNameInput: !!searchNameInput,
        searchNumeroInput: !!searchNumeroInput,
        searchForm: !!searchForm
    });

    function performSearch() {
        console.log('=== PERFORMING SEARCH ===');
        if (!searchForm || !listResultsContainer) {
            console.error('Elementos não encontrados:', { searchForm: !!searchForm, listResultsContainer: !!listResultsContainer });
            return;
        }

        const nameQuery = searchNameInput.value;
        const numeroQuery = searchNumeroInput.value;
        const baseUrl = searchForm.action;

        console.log('Valores de busca:', { nameQuery, numeroQuery, baseUrl });

        const url = new URL(baseUrl);
        url.searchParams.set('search_name', nameQuery);
        url.searchParams.set('search_numero', numeroQuery);
        url.searchParams.set('source', 'js');

        console.log('URL da requisição:', url.toString());

        fetch(url)
            .then(response => {
                console.log('Response status:', response.status);
                return response.text();
            })
            .then(html => {
                console.log('HTML recebido:', html.substring(0, 200) + '...');
                listResultsContainer.innerHTML = html;
                // Com a delegação de eventos, não é necessário reanexar os listeners.
                // Resetar seleção para evitar confusão.
                closeDetails();
            })
            .catch(error => {
                console.error('Erro ao buscar resultados:', error);
                showNotification('Erro ao realizar busca. Tente novamente.', 'error');
            });
    }

    // Função Debounce para evitar requisições excessivas
    function debounce(func, delay) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    const debouncedSearch = debounce(performSearch, 300);

    if (searchNameInput && searchNumeroInput) {
        console.log('Anexando event listeners aos campos de busca');
        searchNameInput.addEventListener('input', debouncedSearch);
        searchNumeroInput.addEventListener('input', debouncedSearch);
    } else {
        console.error('Campos de busca não encontrados para anexar listeners');
    }
    
    console.log('=== PAGPENDENTES JS INICIALIZADO ===');
}); 