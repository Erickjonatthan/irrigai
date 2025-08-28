// Gerenciador do Calendário de Irrigação

class CalendarioIrrigacao {
    constructor() {
        this.dataAtual = new Date();
        this.mesAtual = this.dataAtual.getMonth();
        this.anoAtual = this.dataAtual.getFullYear();
        this.dataSelecionada = null;
        this.registrosIrrigacao = this.carregarRegistros();
        this.inicializar();
    }

    inicializar() {
        this.renderizarCalendario();
        this.configurarEventos();
    }

    configurarEventos() {
        // Event listeners serão adicionados dinamicamente
    }

    renderizarCalendario() {
        const container = document.getElementById('calendario-irrigacao');
        if (!container) return;

        const meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ];

        const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

        // Header do calendário
        const headerHTML = `
            <div class="calendario-header">
                <button class="calendario-nav" onclick="calendarioIrrigacao.mesAnterior()">
                    ← Anterior
                </button>
                <div class="calendario-mes-ano">
                    ${meses[this.mesAtual]} ${this.anoAtual}
                </div>
                <button class="calendario-nav" onclick="calendarioIrrigacao.proximoMes()">
                    Próximo →
                </button>
            </div>
        `;

        // Grid do calendário
        let gridHTML = '<div class="calendario-grid">';
        
        // Cabeçalho dos dias da semana
        diasSemana.forEach(dia => {
            gridHTML += `<div class="calendario-dia-semana">${dia}</div>`;
        });

        // Calcular primeiro dia do mês e quantos dias tem
        const primeiroDia = new Date(this.anoAtual, this.mesAtual, 1).getDay();
        const diasNoMes = new Date(this.anoAtual, this.mesAtual + 1, 0).getDate();
        const diasMesAnterior = new Date(this.anoAtual, this.mesAtual, 0).getDate();

        // Dias do mês anterior (para preencher o início)
        for (let i = primeiroDia - 1; i >= 0; i--) {
            const dia = diasMesAnterior - i;
            gridHTML += `<div class="calendario-dia outro-mes">${dia}</div>`;
        }

        // Dias do mês atual
        for (let dia = 1; dia <= diasNoMes; dia++) {
            const dataCompleta = `${this.anoAtual}-${String(this.mesAtual + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
            const hoje = new Date();
            const ehHoje = dia === hoje.getDate() && this.mesAtual === hoje.getMonth() && this.anoAtual === hoje.getFullYear();
            const temIrrigacao = this.registrosIrrigacao.hasOwnProperty(dataCompleta);
            const podeClicar = new Date(this.anoAtual, this.mesAtual, dia) <= hoje;
            
            let classes = 'calendario-dia';
            if (ehHoje) classes += ' hoje';
            if (temIrrigacao) classes += ' com-irrigacao';
            
            const onclick = podeClicar ? `onclick="calendarioIrrigacao.selecionarDia('${dataCompleta}')"` : '';
            
            gridHTML += `<div class="${classes}" ${onclick}>${dia}</div>`;
        }

        // Dias do próximo mês (para preencher o final)
        const totalCelulas = Math.ceil((primeiroDia + diasNoMes) / 7) * 7;
        const diasRestantes = totalCelulas - (primeiroDia + diasNoMes);
        for (let dia = 1; dia <= diasRestantes; dia++) {
            gridHTML += `<div class="calendario-dia outro-mes">${dia}</div>`;
        }

        gridHTML += '</div>';

        container.innerHTML = headerHTML + gridHTML;
    }

    mesAnterior() {
        if (this.mesAtual === 0) {
            this.mesAtual = 11;
            this.anoAtual--;
        } else {
            this.mesAtual--;
        }
        this.renderizarCalendario();
    }

    proximoMes() {
        if (this.mesAtual === 11) {
            this.mesAtual = 0;
            this.anoAtual++;
        } else {
            this.mesAtual++;
        }
        this.renderizarCalendario();
    }

    selecionarDia(data) {
        this.dataSelecionada = data;
        this.abrirModalRegistro(data);
    }

    abrirModalRegistro(data) {
        const registro = this.registrosIrrigacao[data] || {};
        const dataFormatada = new Date(data + 'T00:00:00').toLocaleDateString('pt-BR');
        
        const modalHTML = `
            <div class="modal-irrigacao" id="modal-irrigacao">
                <div class="modal-irrigacao-content">
                    <div class="modal-irrigacao-header">
                        <h3 class="modal-irrigacao-title">
                            📅 Irrigação - ${dataFormatada}
                        </h3>
                        <button class="modal-irrigacao-close" onclick="calendarioIrrigacao.fecharModal()">
                            ×
                        </button>
                    </div>
                    
                    <form id="form-irrigacao" onsubmit="calendarioIrrigacao.salvarRegistro(event, '${data}')">
                        <div class="form-group">
                            <label class="form-label" for="quantidade-agua">Quantidade de Água (litros)</label>
                            <input type="number" id="quantidade-agua" name="quantidade-agua" 
                                   class="form-input" min="0" step="0.1" 
                                   value="${registro.quantidadeAgua || ''}" required>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="condicao-solo">Condição do Solo</label>
                            <select id="condicao-solo" name="condicao-solo" class="form-input" required>
                                <option value="">Selecione...</option>
                                <option value="muito-seco" ${registro.condicaoSolo === 'muito-seco' ? 'selected' : ''}>Muito Seco</option>
                                <option value="seco" ${registro.condicaoSolo === 'seco' ? 'selected' : ''}>Seco</option>
                                <option value="adequado" ${registro.condicaoSolo === 'adequado' ? 'selected' : ''}>Adequado</option>
                                <option value="umido" ${registro.condicaoSolo === 'umido' ? 'selected' : ''}>Úmido</option>
                                <option value="encharcado" ${registro.condicaoSolo === 'encharcado' ? 'selected' : ''}>Encharcado</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="duracao-irrigacao">Duração da Irrigação (minutos)</label>
                            <input type="number" id="duracao-irrigacao" name="duracao-irrigacao" 
                                   class="form-input" min="1" 
                                   value="${registro.duracaoIrrigacao || ''}" required>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label" for="observacoes">Observações</label>
                            <textarea id="observacoes" name="observacoes" 
                                      class="form-input form-textarea" 
                                      placeholder="Anote observações sobre o clima, plantas, etc...">${registro.observacoes || ''}</textarea>
                        </div>
                        
                        <div class="modal-irrigacao-actions">
                            ${registro.quantidadeAgua ? 
                                '<button type="button" class="btn-modal danger" onclick="calendarioIrrigacao.excluirRegistro(\'' + data + '\')">' +
                                'Excluir Registro</button>' : ''}
                            <button type="button" class="btn-modal secondary" onclick="calendarioIrrigacao.fecharModal()">
                                Cancelar
                            </button>
                            <button type="submit" class="btn-modal primary">
                                Salvar
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        // Remover modal existente se houver
        const modalExistente = document.getElementById('modal-irrigacao');
        if (modalExistente) {
            modalExistente.remove();
        }
        
        // Adicionar modal ao body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Focar no primeiro campo
        setTimeout(() => {
            document.getElementById('quantidade-agua').focus();
        }, 100);
    }

    salvarRegistro(event, data) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const registro = {
            quantidadeAgua: parseFloat(formData.get('quantidade-agua')),
            condicaoSolo: formData.get('condicao-solo'),
            duracaoIrrigacao: parseInt(formData.get('duracao-irrigacao')),
            observacoes: formData.get('observacoes'),
            dataRegistro: new Date().toISOString()
        };
        
        this.registrosIrrigacao[data] = registro;
        this.salvarRegistros();
        this.fecharModal();
        this.renderizarCalendario();
        
        // Mostrar mensagem de sucesso
        this.mostrarMensagem('Registro de irrigação salvo com sucesso!', 'success');
    }

    excluirRegistro(data) {
        if (confirm('Tem certeza que deseja excluir este registro de irrigação?')) {
            delete this.registrosIrrigacao[data];
            this.salvarRegistros();
            this.fecharModal();
            this.renderizarCalendario();
            this.mostrarMensagem('Registro excluído com sucesso!', 'success');
        }
    }

    fecharModal() {
        const modal = document.getElementById('modal-irrigacao');
        if (modal) {
            modal.remove();
        }
    }

    carregarRegistros() {
        const registros = localStorage.getItem('registros_irrigacao');
        return registros ? JSON.parse(registros) : {};
    }

    salvarRegistros() {
        localStorage.setItem('registros_irrigacao', JSON.stringify(this.registrosIrrigacao));
    }

    mostrarMensagem(texto, tipo = 'info') {
        // Criar elemento de mensagem
        const mensagem = document.createElement('div');
        mensagem.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${tipo === 'success' ? '#28a745' : '#007bff'};
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            z-index: 2000;
            font-size: 0.9rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideInRight 0.3s ease-out;
        `;
        mensagem.textContent = texto;
        
        // Adicionar animação CSS
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(mensagem);
        
        // Remover após 3 segundos
        setTimeout(() => {
            mensagem.remove();
            style.remove();
        }, 3000);
    }

    // Método para obter estatísticas dos registros
    obterEstatisticas() {
        const registros = Object.values(this.registrosIrrigacao);
        if (registros.length === 0) return null;
        
        const totalAgua = registros.reduce((sum, reg) => sum + reg.quantidadeAgua, 0);
        const mediaDiaria = totalAgua / registros.length;
        const totalDuracao = registros.reduce((sum, reg) => sum + reg.duracaoIrrigacao, 0);
        
        return {
            totalRegistros: registros.length,
            totalAgua: totalAgua.toFixed(1),
            mediaDiaria: mediaDiaria.toFixed(1),
            totalDuracao: totalDuracao
        };
    }
}

// Inicializar calendário quando a página carregar
let calendarioIrrigacao;
document.addEventListener('DOMContentLoaded', () => {
    // Aguardar um pouco para garantir que o DOM esteja completamente carregado
    setTimeout(() => {
        if (document.getElementById('calendario-irrigacao')) {
            calendarioIrrigacao = new CalendarioIrrigacao();
        }
    }, 500);
});