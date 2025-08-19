// JavaScript para o formulário inicial - Irriga.ai

class FormularioInicial {
    constructor() {
        this.etapaAtual = 1;
        this.totalEtapas = 9; // Total de etapas do formulário
        this.respostas = {};
        this.init();
    }

    init() {
        this.criarEventListeners();
        this.atualizarInterface();
    }

    criarEventListeners() {
        // Botões de navegação
        document.getElementById('btn-voltar').addEventListener('click', () => this.voltarEtapa());
        document.getElementById('btn-continuar').addEventListener('click', () => this.proximaEtapa());
        document.getElementById('btn-finalizar').addEventListener('click', () => this.finalizarFormulario());

        // Listener para mudanças nas alternativas
        document.addEventListener('change', (e) => {
            if (e.target.type === 'radio') {
                this.salvarResposta(e.target);
                this.verificarEtapaCompleta();
            }
        });

        // Listener para campos de texto das opções "Outra"
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('campo-outro')) {
                this.salvarRespostaTexto(e.target);
                this.verificarEtapaCompleta(); // Verificar novamente quando o texto mudar
            }
        });
    }

    salvarResposta(input) {
        const etapa = input.getAttribute('data-etapa');
        const valor = input.value;
        
        this.respostas[`etapa_${etapa}`] = {
            valor: valor,
            texto: input.getAttribute('data-texto') || '',
            timestamp: new Date().toISOString()
        };

        // Primeiro, ocultar todos os campos de texto da etapa atual
        const etapaAtiva = document.querySelector('.etapa.ativa');
        const todosCamposTexto = etapaAtiva.querySelectorAll('.campo-texto');
        todosCamposTexto.forEach(campo => {
            campo.style.display = 'none';
            const inputTexto = campo.querySelector('input');
            if (inputTexto) inputTexto.value = '';
        });

        // Verificar se precisa mostrar campo de texto para a opção selecionada
        const precisaCampoTexto = (
            valor.includes('outra') || 
            valor.includes('outro') || 
            valor === 'mes' || 
            valor === 'estacao' || 
            valor === 'dias' ||
            valor === 'analise' ||
            valor === 'descricao' ||
            valor === 'exata'
        );

        if (precisaCampoTexto) {
            this.mostrarCampoTexto(input);
        }

        console.log('Resposta salva:', this.respostas[`etapa_${etapa}`]);
    }

    salvarRespostaTexto(input) {
        const etapa = input.getAttribute('data-etapa');
        if (this.respostas[`etapa_${etapa}`]) {
            this.respostas[`etapa_${etapa}`].texto_adicional = input.value;
        }
    }

    mostrarCampoTexto(input) {
        const container = input.closest('.alternativa');
        let campoTexto = container.querySelector('.campo-texto');
        
        if (!campoTexto) {
            campoTexto = document.createElement('div');
            campoTexto.className = 'campo-texto';
            
            // Definir placeholder baseado no tipo de pergunta
            let placeholder = 'Por favor, especifique:';
            const valor = input.value;
            
            if (valor === 'mes') {
                placeholder = 'Ex: Março, Abril, etc.';
            } else if (valor === 'estacao') {
                placeholder = 'Ex: Primavera, Verão, etc.';
            } else if (valor === 'dias') {
                placeholder = 'Ex: 30 dias, 2 semanas, etc.';
            } else if (valor === 'analise') {
                placeholder = 'Ex: CC: 25%, PMP: 12%, Densidade: 1.3 g/cm³';
            } else if (valor === 'descricao') {
                placeholder = 'Ex: pouca, média ou muita';
            } else if (valor === 'exata') {
                placeholder = 'Ex: 85%';
            }
            
            campoTexto.innerHTML = `
                <input type="text" 
                       placeholder="${placeholder}" 
                       class="campo-outro"
                       data-etapa="${input.getAttribute('data-etapa')}"
                       required>
            `;
            container.appendChild(campoTexto);
        }
        
        campoTexto.style.display = 'block';
        setTimeout(() => {
            const inputTexto = campoTexto.querySelector('input');
            if (inputTexto) {
                inputTexto.focus();
            }
        }, 100);
    }

    ocultarCampoTexto(input) {
        const container = input.closest('.alternativa');
        const campoTexto = container.querySelector('.campo-texto');
        
        if (campoTexto) {
            campoTexto.style.display = 'none';
            campoTexto.querySelector('input').value = '';
        }
    }

    verificarEtapaCompleta() {
        const etapaAtiva = document.querySelector('.etapa.ativa');
        const inputsSelecionados = etapaAtiva.querySelectorAll('input[type="radio"]:checked');
        const btnContinuar = document.getElementById('btn-continuar');
        const btnFinalizar = document.getElementById('btn-finalizar');
        
        let completa = inputsSelecionados.length > 0;
        
        // Verificar se há campos de texto que precisam ser preenchidos
        inputsSelecionados.forEach(input => {
            const valor = input.value;
            const precisaCampoTexto = (
                valor.includes('outra') || 
                valor.includes('outro') || 
                valor === 'mes' || 
                valor === 'estacao' || 
                valor === 'dias' ||
                valor === 'analise' ||
                valor === 'descricao' ||
                valor === 'exata'
            );

            if (precisaCampoTexto && completa) {
                const campoTexto = input.closest('.alternativa').querySelector('.campo-outro');
                if (!campoTexto || !campoTexto.value.trim()) {
                    completa = false;
                }
            }
        });

        // Habilitar/desabilitar botões
        if (btnContinuar) btnContinuar.disabled = !completa;
        if (btnFinalizar) btnFinalizar.disabled = !completa;
        
        console.log('Etapa completa:', completa);
    }

    proximaEtapa() {
        if (this.etapaAtual < this.totalEtapas) {
            this.etapaAtual++;
            this.atualizarInterface();
        }
    }

    voltarEtapa() {
        if (this.etapaAtual > 1) {
            this.etapaAtual--;
            this.atualizarInterface();
        }
    }

    atualizarInterface() {
        // Esconder todas as etapas
        document.querySelectorAll('.etapa').forEach(etapa => {
            etapa.classList.remove('ativa');
        });

        // Mostrar etapa atual
        const etapaAtiva = document.getElementById(`etapa-${this.etapaAtual}`);
        if (etapaAtiva) {
            etapaAtiva.classList.add('ativa');
        }

        // Atualizar indicador de progresso
        this.atualizarProgresso();

        // Atualizar botões
        this.atualizarBotoes();

        // Verificar se etapa já está completa
        setTimeout(() => this.verificarEtapaCompleta(), 100);
    }

    atualizarProgresso() {
        const dots = document.querySelectorAll('.progress-dot');
        const etapaInfo = document.querySelector('.etapa-info');
        
        dots.forEach((dot, index) => {
            dot.classList.remove('active', 'completed');
            if (index + 1 < this.etapaAtual) {
                dot.classList.add('completed');
            } else if (index + 1 === this.etapaAtual) {
                dot.classList.add('active');
            }
        });

        if (etapaInfo) {
            etapaInfo.textContent = `${this.etapaAtual}/${this.totalEtapas}`;
        }
    }

    atualizarBotoes() {
        const btnVoltar = document.getElementById('btn-voltar');
        const btnContinuar = document.getElementById('btn-continuar');
        const btnFinalizar = document.getElementById('btn-finalizar');

        // Botão voltar
        if (btnVoltar) {
            btnVoltar.style.display = this.etapaAtual === 1 ? 'none' : 'block';
        }

        // Botões continuar/finalizar
        if (this.etapaAtual === this.totalEtapas) {
            if (btnContinuar) btnContinuar.style.display = 'none';
            if (btnFinalizar) btnFinalizar.style.display = 'block';
        } else {
            if (btnContinuar) btnContinuar.style.display = 'block';
            if (btnFinalizar) btnFinalizar.style.display = 'none';
        }
    }

    async finalizarFormulario() {
        const btnFinalizar = document.getElementById('btn-finalizar');
        
        // Mostrar loading
        btnFinalizar.classList.add('loading');
        btnFinalizar.disabled = true;

        try {
            // Preparar dados para envio
            const dadosFormulario = {
                respostas: this.respostas,
                timestamp_conclusao: new Date().toISOString(),
                user_agent: navigator.userAgent
            };

            console.log('Dados do formulário:', dadosFormulario);

            // Enviar para o servidor
            const response = await fetch('/salvar-formulario-inicial', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dadosFormulario)
            });

            if (response.ok) {
                const resultado = await response.json();
                console.log('Formulário salvo com sucesso:', resultado);
                
                // Redirecionar para o formulário principal ou painel
                window.location.href = '/form';
            } else {
                throw new Error('Erro ao salvar formulário');
            }

        } catch (error) {
            console.error('Erro ao finalizar formulário:', error);
            alert('Erro ao salvar o formulário. Tente novamente.');
        } finally {
            // Remover loading
            btnFinalizar.classList.remove('loading');
            btnFinalizar.disabled = false;
        }
    }

    // Método para carregar estado salvo (se houver)
    carregarEstadoSalvo() {
        const estadoSalvo = localStorage.getItem('formulario_inicial_estado');
        if (estadoSalvo) {
            try {
                const estado = JSON.parse(estadoSalvo);
                this.etapaAtual = estado.etapaAtual || 1;
                this.respostas = estado.respostas || {};
                
                // Restaurar seleções na interface
                Object.keys(this.respostas).forEach(chave => {
                    const resposta = this.respostas[chave];
                    const input = document.querySelector(`input[value="${resposta.valor}"]`);
                    if (input) {
                        input.checked = true;
                        if (resposta.texto_adicional) {
                            this.mostrarCampoTexto(input);
                            const campoTexto = input.closest('.alternativa').querySelector('.campo-outro');
                            if (campoTexto) {
                                campoTexto.value = resposta.texto_adicional;
                            }
                        }
                    }
                });

                this.atualizarInterface();
            } catch (error) {
                console.error('Erro ao carregar estado salvo:', error);
            }
        }
    }

    // Salvar estado no localStorage
    salvarEstado() {
        const estado = {
            etapaAtual: this.etapaAtual,
            respostas: this.respostas
        };
        localStorage.setItem('formulario_inicial_estado', JSON.stringify(estado));
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    window.formularioInicial = new FormularioInicial();
    
    // Salvar estado periodicamente
    setInterval(() => {
        if (window.formularioInicial) {
            window.formularioInicial.salvarEstado();
        }
    }, 10000); // Salvar a cada 10 segundos
});
