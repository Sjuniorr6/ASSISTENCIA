document.addEventListener('DOMContentLoaded', function() {
    const numeroRatField = document.getElementById('id_numero_rat');
    const ratModal = document.getElementById('ratModal');
    const closeRatModalBtn = document.getElementById('closeRatModal');
    const modalRatForm = document.getElementById('modalRatForm');
    const downloadPdfBtn = document.getElementById('downloadPdf');
    const statusSelect = document.getElementById('modal_status');

    const successModal = document.getElementById('successModal');
    const closeSuccessModalBtn = document.getElementById('closeSuccessModal');
    const successMessage = document.getElementById('successMessage');

    // Função para atualizar a cor do status
    function updateStatusColor() {
        const statusColors = {
            'aberto': 'text-yellow-600',
            'finalizado': 'text-green-600'
        };
        
        if (statusSelect) {
            // Remove todas as classes de cor
            statusSelect.classList.remove('text-yellow-600', 'text-green-600');
            
            // Adiciona a classe de cor correspondente ao status selecionado
            const selectedStatus = statusSelect.value;
            statusSelect.classList.add(statusColors[selectedStatus]);
        }
    }

    // Atualiza a cor quando o status muda
    if (statusSelect) {
        statusSelect.addEventListener('change', updateStatusColor);
        // Atualiza a cor inicial
        updateStatusColor();
    }

    // Função para buscar o próximo número de RAT
    function getNextRatNumber() {
        fetch('/relatoriomanutencao/get-next-rat-number/')
            .then(response => response.json())
            .then(data => {
                if (numeroRatField) {
                    numeroRatField.value = data.numero_rat;
                }
            })
            .catch(error => console.error('Erro ao buscar próximo número de RAT:', error));
    }

    // Preencher o campo RAT ao carregar a página, se ele estiver vazio
    if (numeroRatField && !numeroRatField.value) {
        getNextRatNumber();
    }

    // Função para abrir o modal e carregar dados do RAT
    window.openRatModal = function(ratPk) {
        fetch(`/relatoriomanutencao/api/rat/${ratPk}/`)
            .then(response => response.json())
            .then(data => {
                // Popular os campos do formulário no modal
                const fields = [
                    'numero_rat', 'status', 'data_instalacao', 'data_visita', 'periodo',
                    'horario', 'cliente', 'cpf_cnpj', 'telefone1', 'telefone2', 'email',
                    'rg_inscricao', 'endereco', 'bairro', 'cidade', 'uf', 'cep',
                    'loja_revendedora', 'data_compra', 'equipamento', 'numero_serie',
                    'codigo_produto', 'fabricante', 'modelo', 'diametro_tubulacao',
                    'voltagem', 'numero_nota_fiscal', 'tipo_gas', 'equipe_tecnica',
                    'relatorio_interno', 'servico_executar', 'tipo_servico'
                ];

                fields.forEach(field => {
                    const element = document.getElementById(`modal_${field}`);
                    if (element) {
                        element.value = data[field] || '';
                    }
                });

                // Adicionar o PK do RAT ao formulário para futuras atualizações
                modalRatForm.setAttribute('data-rat-pk', ratPk);

                ratModal.classList.remove('hidden');
            })
            .catch(error => console.error('Erro ao carregar detalhes do RAT:', error));
    };

    // Fechar o modal
    closeRatModalBtn.addEventListener('click', function() {
        ratModal.classList.add('hidden');
    });

    // Fechar o modal ao clicar fora dele
    ratModal.addEventListener('click', function(e) {
        if (e.target === ratModal) {
            ratModal.classList.add('hidden');
        }
    });

    // Função para exibir erro
    function showError(fieldId, message) {
        const field = document.getElementById(fieldId);
        const errorSpan = document.getElementById(fieldId + '_error');
        if (field) {
            field.classList.add('border-red-500', 'focus:ring-red-500');
            field.classList.remove('border-gray-300', 'focus:ring-indigo-500');
        }
        if (errorSpan) {
            errorSpan.textContent = message;
            errorSpan.classList.remove('hidden');
        }
    }

    // Função para ocultar erro
    function hideError(fieldId) {
        const field = document.getElementById(fieldId);
        const errorSpan = document.getElementById(fieldId + '_error');
        if (field) {
            field.classList.remove('border-red-500', 'focus:ring-red-500');
            field.classList.add('border-gray-300', 'focus:ring-indigo-500');
        }
        if (errorSpan) {
            errorSpan.classList.add('hidden');
            errorSpan.textContent = '';
        }
    }

    // Função de validação para um campo específico
    function validateField(fieldId, errorMessage, validationFn = (value) => value.trim() !== '') {
        const field = document.getElementById(fieldId);
        if (!field) return true;

        const value = field.value;
        if (!validationFn(value)) {
            showError(fieldId, errorMessage);
            return false;
        } else {
            hideError(fieldId);
            return true;
        }
    }

    // Função de validação de e-mail
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Campos obrigatórios para validação
    const requiredFields = [
        { id: 'modal_cliente', message: 'Cliente é obrigatório.' },
        { id: 'modal_telefone1', message: 'Telefone 1 é obrigatório.' },
        { id: 'modal_endereco', message: 'Endereço é obrigatório.' },
        { id: 'modal_email', message: 'Email inválido.', validationFn: isValidEmail },
        { id: 'modal_equipamento', message: 'Equipamento é obrigatório.' },
    ];

    // Adicionar validação em tempo real
    requiredFields.forEach(fieldInfo => {
        const fieldElement = document.getElementById(fieldInfo.id);
        if (fieldElement) {
            fieldElement.addEventListener('blur', () => {
                validateField(fieldInfo.id, fieldInfo.message, fieldInfo.validationFn);
            });
            fieldElement.addEventListener('input', () => {
                hideError(fieldInfo.id);
            });
        }
    });

    // Lidar com o envio do formulário do modal
    modalRatForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Validação completa antes do envio
        let formIsValid = true;
        requiredFields.forEach(fieldInfo => {
            if (!validateField(fieldInfo.id, fieldInfo.message, fieldInfo.validationFn)) {
                formIsValid = false;
            }
        });

        if (!formIsValid) {
            alert('Por favor, preencha todos os campos obrigatórios corretamente.');
            return;
        }

        const ratPk = this.getAttribute('data-rat-pk');
        const formData = new FormData(this);
        
        // Converter FormData para JSON
        const jsonData = {};
        for (const [key, value] of formData.entries()) {
            if (key === 'status' && !value) {
                jsonData[key] = 'aberto';
            } else if (value === '') {
                jsonData[key] = null;
            } else {
                jsonData[key] = value;
            }
        }

        fetch(`/relatoriomanutencao/api/rat/${ratPk}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.json().then(err => Promise.reject(err));
            }
        })
        .then(data => {
            if (data.status === 'success') {
                ratModal.classList.add('hidden');
                successMessage.textContent = 'RAT atualizado com sucesso!';
                successModal.classList.remove('hidden');
            } else {
                throw new Error(data.message || 'Erro ao atualizar RAT');
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar RAT:', error);
            alert('Erro ao atualizar RAT: ' + error.message);
        });
    });

    // Lidar com o fechamento do modal de sucesso
    if (closeSuccessModalBtn) {
        closeSuccessModalBtn.addEventListener('click', function() {
            successModal.classList.add('hidden');
            location.reload();
        });
    }

    // Lidar com o download do PDF
    downloadPdfBtn.addEventListener('click', function() {
        const ratPk = modalRatForm.getAttribute('data-rat-pk');
        if (ratPk) {
            window.open(`/relatoriomanutencao/pdf/${ratPk}/`, '_blank');
        } else {
            alert('Selecione um RAT para gerar o PDF.');
        }
    });
}); 