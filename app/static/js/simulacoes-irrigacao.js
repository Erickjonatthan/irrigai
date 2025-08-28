// Gerenciador de Simulações de Irrigação

class SimulacoesManager {
    constructor() {
        this.simulacoes = this.carregarSimulacoes();
        this.inicializar();
    }

    inicializar() {
        this.configurarEventos();
        this.atualizarHistorico();
    }

    configurarEventos() {
        const form = document.getElementById('form-simulacao');
        if (form) {
            form.addEventListener('submit', (e) => this.executarSimulacao(e));
        }
    }

    async executarSimulacao(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const dados = {
            culturaTipo: formData.get('cultura-tipo'),
            areaCultivo: parseFloat(formData.get('area-cultivo')),
            sistemaIrrigacao: formData.get('sistema-irrigacao'),
            periodoSimulacao: parseInt(formData.get('periodo-simulacao')),
            condicaoSolo: formData.get('condicao-solo')
        };

        // Validar dados
        if (!this.validarDados(dados)) {
            return;
        }

        // Mostrar loading
        this.mostrarLoading();

        try {
            // Simular processamento (em uma aplicação real, seria uma chamada à API)
            await this.simularProcessamento();
            
            // Calcular resultados
            const resultados = this.calcularResultados(dados);
            
            // Salvar simulação
            this.salvarSimulacao(dados, resultados);
            
            // Exibir resultados
            this.exibirResultados(resultados);
            
            // Atualizar histórico
            this.atualizarHistorico();
            
            // Limpar formulário
            event.target.reset();
            
        } catch (error) {
            console.error('Erro na simulação:', error);
            this.mostrarErro('Erro ao executar simulação. Tente novamente.');
        } finally {
            this.ocultarLoading();
        }
    }

    validarDados(dados) {
        if (!dados.culturaTipo) {
            this.mostrarErro('Selecione o tipo de cultura');
            return false;
        }
        if (!dados.areaCultivo || dados.areaCultivo <= 0) {
            this.mostrarErro('Informe uma área válida');
            return false;
        }
        if (!dados.sistemaIrrigacao) {
            this.mostrarErro('Selecione o sistema de irrigação');
            return false;
        }
        if (!dados.periodoSimulacao) {
            this.mostrarErro('Selecione o período da simulação');
            return false;
        }
        if (!dados.condicaoSolo) {
            this.mostrarErro('Selecione a condição do solo');
            return false;
        }
        return true;
    }

    async simularProcessamento() {
        // Simular tempo de processamento
        return new Promise(resolve => setTimeout(resolve, 2000));
    }

    calcularResultados(dados) {
        // Coeficientes baseados no tipo de cultura
        const coeficientesCultura = {
            'milho': { kc: 1.2, eficiencia: 0.85 },
            'soja': { kc: 1.15, eficiencia: 0.80 },
            'feijao': { kc: 1.05, eficiencia: 0.75 },
            'tomate': { kc: 1.25, eficiencia: 0.90 },
            'alface': { kc: 1.0, eficiencia: 0.70 },
            'outros': { kc: 1.1, eficiencia: 0.80 }
        };

        // Coeficientes do sistema de irrigação
        const eficienciaSistema = {
            'gotejamento': 0.95,
            'aspersao': 0.80,
            'sulcos': 0.60,
            'microaspersao': 0.85
        };

        // Ajuste pela condição do solo
        const ajusteSolo = {
            'muito-seco': 1.3,
            'seco': 1.15,
            'adequado': 1.0,
            'umido': 0.85,
            'encharcado': 0.5
        };

        const cultura = coeficientesCultura[dados.culturaTipo];
        const eficiencia = eficienciaSistema[dados.sistemaIrrigacao];
        const ajuste = ajusteSolo[dados.condicaoSolo];

        // Cálculos básicos (valores simulados para demonstração)
        const evapotranspiracao = 5.5; // mm/dia (valor médio)
        const necessidadeHidrica = evapotranspiracao * cultura.kc * ajuste;
        const volumeTotal = (necessidadeHidrica * dados.areaCultivo * 10) * dados.periodoSimulacao; // litros
        const volumeEfetivo = volumeTotal / eficiencia;
        const custoEstimado = volumeEfetivo * 0.003; // R$ 0,003 por litro
        const economiaAgua = volumeTotal - volumeEfetivo;
        const frequenciaIrrigacao = this.calcularFrequencia(dados.sistemaIrrigacao, dados.condicaoSolo);

        return {
            necessidadeHidrica: necessidadeHidrica.toFixed(2),
            volumeTotal: Math.round(volumeTotal),
            volumeEfetivo: Math.round(volumeEfetivo),
            custoEstimado: custoEstimado.toFixed(2),
            economiaAgua: Math.round(Math.abs(economiaAgua)),
            frequenciaIrrigacao,
            eficienciaTotal: (eficiencia * 100).toFixed(1),
            recomendacoes: this.gerarRecomendacoes(dados, eficiencia)
        };
    }

    calcularFrequencia(sistema, condicao) {
        const frequencias = {
            'gotejamento': { 'muito-seco': 1, 'seco': 2, 'adequado': 3, 'umido': 4, 'encharcado': 7 },
            'aspersao': { 'muito-seco': 2, 'seco': 3, 'adequado': 4, 'umido': 5, 'encharcado': 8 },
            'sulcos': { 'muito-seco': 3, 'seco': 4, 'adequado': 5, 'umido': 6, 'encharcado': 10 },
            'microaspersao': { 'muito-seco': 1, 'seco': 2, 'adequado': 3, 'umido': 4, 'encharcado': 6 }
        };
        
        return frequencias[sistema][condicao] || 3;
    }

    gerarRecomendacoes(dados, eficiencia) {
        const recomendacoes = [];
        
        if (eficiencia < 0.7) {
            recomendacoes.push('Considere melhorar o sistema de irrigação para maior eficiência');
        }
        
        if (dados.condicaoSolo === 'muito-seco') {
            recomendacoes.push('Solo muito seco detectado. Aumente a frequência de irrigação');
        }
        
        if (dados.condicaoSolo === 'encharcado') {
            recomendacoes.push('Solo encharcado. Reduza ou suspenda a irrigação temporariamente');
        }
        
        if (dados.sistemaIrrigacao === 'sulcos') {
            recomendacoes.push('Sistema de sulcos tem menor eficiência. Considere gotejamento ou aspersão');
        }
        
        recomendacoes.push('Monitore regularmente a umidade do solo');
        recomendacoes.push('Ajuste a irrigação conforme as condições climáticas');
        
        return recomendacoes;
    }

    exibirResultados(resultados) {
        const container = document.getElementById('resultados-simulacao');
        const conteudo = document.getElementById('conteudo-resultados');
        
        if (!container || !conteudo) return;

        conteudo.innerHTML = `
            <div class="resultado-item">
                <div class="resultado-titulo">Necessidade Hídrica Diária</div>
                <div class="resultado-valor">${resultados.necessidadeHidrica} mm/dia</div>
                <div class="resultado-descricao">Quantidade de água necessária por dia</div>
            </div>
            
            <div class="resultado-item">
                <div class="resultado-titulo">Volume Total Necessário</div>
                <div class="resultado-valor">${resultados.volumeTotal.toLocaleString()} L</div>
                <div class="resultado-descricao">Volume total para o período simulado</div>
            </div>
            
            <div class="resultado-item">
                <div class="resultado-titulo">Volume Efetivo (com perdas)</div>
                <div class="resultado-valor">${resultados.volumeEfetivo.toLocaleString()} L</div>
                <div class="resultado-descricao">Volume considerando a eficiência do sistema</div>
            </div>
            
            <div class="resultado-item">
                <div class="resultado-titulo">Custo Estimado</div>
                <div class="resultado-valor">R$ ${resultados.custoEstimado}</div>
                <div class="resultado-descricao">Custo estimado com água para o período</div>
            </div>
            
            <div class="resultado-item">
                <div class="resultado-titulo">Frequência Recomendada</div>
                <div class="resultado-valor">A cada ${resultados.frequenciaIrrigacao} dias</div>
                <div class="resultado-descricao">Intervalo recomendado entre irrigações</div>
            </div>
            
            <div class="resultado-item">
                <div class="resultado-titulo">Eficiência do Sistema</div>
                <div class="resultado-valor">${resultados.eficienciaTotal}%</div>
                <div class="resultado-descricao">Eficiência do sistema de irrigação escolhido</div>
            </div>
            
            <div class="resultado-item">
                <div class="resultado-titulo">Recomendações</div>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    ${resultados.recomendacoes.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;
        
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });
    }

    salvarSimulacao(dados, resultados) {
        const simulacao = {
            id: Date.now(),
            data: new Date().toISOString(),
            dados,
            resultados
        };
        
        this.simulacoes.push(simulacao);
        localStorage.setItem('simulacoes_irrigacao', JSON.stringify(this.simulacoes));
    }

    carregarSimulacoes() {
        const simulacoes = localStorage.getItem('simulacoes_irrigacao');
        return simulacoes ? JSON.parse(simulacoes) : [];
    }

    atualizarHistorico() {
        const container = document.getElementById('historico-simulacoes');
        if (!container) return;

        if (this.simulacoes.length === 0) {
            container.innerHTML = `
                <div class="historico-vazio">
                    <span class="icon-vazio">📝</span>
                    <p>Nenhuma simulação realizada ainda</p>
                    <small>Execute sua primeira simulação para ver o histórico aqui</small>
                </div>
            `;
            return;
        }

        const historicoHtml = this.simulacoes
            .sort((a, b) => new Date(b.data) - new Date(a.data))
            .map(simulacao => {
                const data = new Date(simulacao.data).toLocaleString('pt-BR');
                const cultura = simulacao.dados.culturaTipo.charAt(0).toUpperCase() + simulacao.dados.culturaTipo.slice(1);
                
                return `
                    <div class="historico-item">
                        <div class="historico-info">
                            <div class="historico-titulo">${cultura} - ${simulacao.dados.areaCultivo}ha</div>
                            <div class="historico-data">${data}</div>
                        </div>
                        <div class="historico-acoes">
                            <button class="btn-historico" onclick="simulacoesManager.visualizarSimulacao(${simulacao.id})">
                                Ver Detalhes
                            </button>
                            <button class="btn-historico delete" onclick="simulacoesManager.excluirSimulacao(${simulacao.id})">
                                Excluir
                            </button>
                        </div>
                    </div>
                `;
            })
            .join('');

        container.innerHTML = historicoHtml;
    }

    visualizarSimulacao(id) {
        const simulacao = this.simulacoes.find(s => s.id === id);
        if (!simulacao) return;

        this.exibirResultados(simulacao.resultados);
    }

    excluirSimulacao(id) {
        if (confirm('Tem certeza que deseja excluir esta simulação?')) {
            this.simulacoes = this.simulacoes.filter(s => s.id !== id);
            localStorage.setItem('simulacoes_irrigacao', JSON.stringify(this.simulacoes));
            this.atualizarHistorico();
        }
    }

    mostrarLoading() {
        const btnSimular = document.querySelector('.btn-simular');
        if (btnSimular) {
            btnSimular.innerHTML = `
                <div class="loading-spinner"></div>
                Processando...
            `;
            btnSimular.disabled = true;
        }
    }

    ocultarLoading() {
        const btnSimular = document.querySelector('.btn-simular');
        if (btnSimular) {
            btnSimular.innerHTML = `
                <span class="btn-icon">🔄</span>
                Executar Simulação
            `;
            btnSimular.disabled = false;
        }
    }

    mostrarErro(mensagem) {
        alert(mensagem); // Em uma aplicação real, usaria um toast ou modal mais elegante
    }
}

// Função para voltar à tela principal
function voltarParaHome() {
    window.history.back();
}

// Inicializar quando a página carregar
let simulacoesManager;
document.addEventListener('DOMContentLoaded', () => {
    simulacoesManager = new SimulacoesManager();
});