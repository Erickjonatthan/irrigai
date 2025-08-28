/**
 * Gerenciador de funcionalidades de irrigação para a seção de cultivo
 * Este script integra o cálculo de irrigação com a interface do usuário
 */

class IrrigacaoManager {
  constructor() {
    this.dadosFormulario = null;
    this.dadosClimaticos = null;
    this.resultadoIrrigacao = null;
    this.inicializar();
  }

  /**
   * Inicializa o gerenciador de irrigação
   */
  inicializar() {
    console.log('Executando inicialização do IrrigacaoManager...');
    
    // Verifica se o DOM está pronto, se não, aguarda
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.criarInterfaceIrrigacao());
    } else {
      // DOM já está pronto, executa imediatamente
      this.criarInterfaceIrrigacao();
    }
  }

  /**
   * Cria a interface de irrigação
   */
  criarInterfaceIrrigacao() {
    console.log('Interface de irrigação preparada - usando apenas recomendações');
    // Não cria mais o card de "Cálculo de Irrigação"
    // As recomendações serão exibidas diretamente no card de recomendações
  }

  /**
   * Cria o card para cálculo de irrigação
   */
  criarCardCalculoIrrigacao() {
    const cardDiv = document.createElement('div');
    cardDiv.id = 'calculo-irrigacao';
    cardDiv.className = 'content-card';
    cardDiv.style.marginBottom = '20px';

    cardDiv.innerHTML = `
      <div class="card-title">
        <span class="card-icon">💧</span>
        Cálculo de Irrigação
      </div>
      <div class="card-description">
        Calculando automaticamente a necessidade de irrigação para seu cultivo...
        <div class="loading-indicator" id="loading-irrigacao">
          <i class="fas fa-spinner fa-spin"></i> Processando dados...
        </div>
      </div>
      <div id="resultado-irrigacao" style="display: none; margin-top: 15px;">
        <div class="alert alert-info">
          <h5>Resultado do Cálculo:</h5>
          <div id="mensagem-irrigacao"></div>
          <div class="mt-2">
            <div><strong>Frequência de irrigação:</strong> <span id="frequencia-irrigacao"></span> dias</div>
            <div><strong>Lâmina bruta por evento:</strong> <span id="lamina-bruta"></span> mm</div>
            <div><strong>Lâmina líquida por evento:</strong> <span id="lamina-liquida"></span> mm</div>
          </div>
        </div>
      </div>
    `;

    return cardDiv;
  }

  /**
   * Mostra o indicador de carregamento das recomendações
   */
  mostrarCarregamentoRecomendacoes() {
    const recomendacoesElement = document.getElementById('lista-recomendacoes-cultivo');
    if (recomendacoesElement) {
      recomendacoesElement.innerHTML = `
        <div class="text-center py-4" id="loading-recomendacoes">
          <p class="text-muted">Carregando...</p>
        </div>
      `;
    }
  }

  /**
   * Inicia o cálculo de irrigação usando dados já armazenados
   */
  async mostrarFormularioIrrigacao() {
    console.log('Inicia o cálculo de irrigação usando dados já armazenados');
    
    // Mostrar indicador de carregamento das recomendações imediatamente
    this.mostrarCarregamentoRecomendacoes();
    
    try {
      // Carrega os dados do formulário inicial se ainda não temos
      if (!this.dadosFormulario) {
        console.log('Carregando dados do formulário inicial...');
        await this.carregarDadosFormularioInicial();
        console.log('Dados do formulário carregados:', this.dadosFormulario);
      } else {
        console.log('Dados do formulário já disponíveis:', this.dadosFormulario);
      }
      
      // Verifica se já temos os dados climáticos necessários
      if (!this.dadosClimaticos) {
        console.log('Dados climáticos não encontrados, carregando...');
        await this.carregarDadosClimaticos();
        console.log('Dados climáticos carregados com sucesso:', this.dadosClimaticos);
      } else {
        console.log('Dados climáticos já disponíveis:', this.dadosClimaticos);
      }
      
      // Calcula diretamente a irrigação
      console.log('Calculando irrigação com dados existentes...');
      this.calcularIrrigacao();
      console.log('Cálculo de irrigação concluído!');
      
    } catch (erro) {
      console.error('Erro durante o cálculo de irrigação:', erro);
      
      // Ocultar o indicador de carregamento em caso de erro
      const loadingIndicator = document.getElementById('loading-irrigacao');
      if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
      }
      
      // Exibir mensagem de erro no card
      const resultadoDiv = document.getElementById('resultado-irrigacao');
      if (resultadoDiv) {
        resultadoDiv.style.display = 'block';
        resultadoDiv.innerHTML = `
          <div style="color: #e74c3c; padding: 10px; border: 1px solid #e74c3c; border-radius: 5px; background-color: #fdf2f2;">
            <h4>❌ Erro no Cálculo</h4>
            <p>Não foi possível calcular a irrigação. Verifique se você preencheu o formulário inicial.</p>
            <p><small>Erro: ${erro.message}</small></p>
          </div>
        `;
      }
    }
  }

  /**
   * Carrega os dados do formulário inicial do servidor
   */
  async carregarDadosFormularioInicial() {
    try {
      const response = await fetch('/api/dados-formulario-inicial');
      if (!response.ok) {
        throw new Error('Falha ao carregar dados do formulário inicial');
      }
      
      const dados = await response.json();
      if (!dados.tem_dados) {
        throw new Error('Dados do formulário inicial não encontrados');
      }
      
      this.dadosFormulario = dados;
      console.log('Dados do formulário inicial carregados:', this.dadosFormulario);
    } catch (erro) {
      console.error('Erro ao carregar dados do formulário inicial:', erro);
      throw erro;
    }
  }

  /**
   * Carrega os dados climáticos do servidor
   */
  async carregarDadosClimaticos() {
    try {
      // Verifica se os dados já estão disponíveis na página
      if (window.dadosGraficos && window.dadosGraficos.balancoHidrico && window.dadosGraficos.precipitacao) {
        this.dadosClimaticos = {
          dados_grafico_balanco_hidrico: window.dadosGraficos.balancoHidrico,
          dados_grafico_precipitacao: window.dadosGraficos.precipitacao
        };
        console.log('Dados climáticos carregados da variável global dadosGraficos');
        return;
      }

      // Se não estiverem disponíveis, faz uma requisição ao servidor
      const response = await fetch('/api/dados-climaticos');
      if (!response.ok) {
        throw new Error('Falha ao carregar dados climáticos');
      }
      this.dadosClimaticos = await response.json();
      console.log('Dados climáticos carregados da API');
    } catch (erro) {
      console.error('Erro ao carregar dados climáticos:', erro);
      // Se não conseguir carregar os dados, usar dados de exemplo para teste
      this.dadosClimaticos = this.criarDadosClimaticosExemplo();
      console.log('Usando dados climáticos de exemplo devido a erro:', erro);
    }
  }



  /**
   * Calcula o manejo de irrigação usando a nova função do módulo calcular-irrigacao.js
   */
  calcularIrrigacao() {
    console.log('Iniciando método calcularIrrigacao...');
    
    try {
      // Verifica se a função está disponível
      console.log('Verificando disponibilidade da função calcularManejoDeIrrigacao...');
      if (typeof calcularManejoDeIrrigacao !== 'function') {
        console.error('Função calcularManejoDeIrrigacao não está disponível');
        throw new Error('A função de cálculo de irrigação não está disponível');
      }
      console.log('Função calcularManejoDeIrrigacao está disponível');

      // Verifica se os dados necessários estão disponíveis
      console.log('Verificando dados necessários...');
      console.log('dadosFormulario:', this.dadosFormulario);
      console.log('dadosClimaticos:', this.dadosClimaticos);
      
      if (!this.dadosFormulario || !this.dadosClimaticos) {
        throw new Error('Dados necessários não estão disponíveis');
      }

      // Converte os dados do formulário inicial para o formato esperado pela função de cálculo
      console.log('Formatando dados do formulário...');
      
      // Os dados já vêm estruturados da API, apenas precisamos garantir que estão no formato correto
      const dadosFormularioFormatados = {
        respostas: {
          etapa_1: this.dadosFormulario.respostas?.etapa_1 || { valor: '', texto: '' },
          etapa_3: this.dadosFormulario.respostas?.etapa_3 || { valor: '100_150' },
          etapa_5: this.dadosFormulario.respostas?.etapa_5 || { valor: 'arenoso' }
        },
        coordenadas: this.dadosFormulario.coordenadas || { latitude: '', longitude: '' }
      };
        
      console.log('Dados formatados para cálculo de irrigação:', dadosFormularioFormatados);
      console.log('Chamando função calcularManejoDeIrrigacao...');
      
      // Calcula a irrigação usando a nova função
      this.resultadoIrrigacao = calcularManejoDeIrrigacao(dadosFormularioFormatados, this.dadosClimaticos);
      
      console.log('Resultado do cálculo de irrigação:', this.resultadoIrrigacao);
      console.log('Chamando exibirResultadoIrrigacao...');
      
      // Exibe o resultado
      this.exibirResultadoIrrigacao();
      
      console.log('Método calcularIrrigacao concluído com sucesso!');
    } catch (erro) {
      console.error('Erro ao calcular irrigação:', erro);
      throw erro; // Re-lança o erro para ser capturado pelo método pai
    }
  }

  /**
   * Exibe o resultado do cálculo de irrigação na interface
   */
  exibirResultadoIrrigacao() {
    // Apenas adiciona o resultado às recomendações de cultivo
    // O card de "Cálculo de Irrigação" foi removido
    this.adicionarRecomendacaoIrrigacao();
  }
  
  /**
   * Cria um gráfico de pizza para visualizar a distribuição de irrigação vs precipitação
   */
  criarGraficoIrrigacaoPizza() {
    // Verificar se o Chart.js está disponível
    if (typeof Chart === 'undefined') {
      console.error('Chart.js não está disponível. O gráfico não será criado.');
      return;
    }
    
    // Obter o elemento canvas
    const canvas = document.getElementById('grafico-irrigacao-pizza');
    if (!canvas) {
      console.error('Elemento canvas para o gráfico de pizza não encontrado.');
      return;
    }
    
    // Obter dados dos parâmetros calculados
    const parametros = this.resultadoIrrigacao.parametrosCalculados;
    const porcentagemIrrigacao = parametros.porcentagemIrrigacao;
    const porcentagemPrecipitacao = parametros.porcentagemPrecipitacao;
    
    // Destruir gráfico existente se houver
    if (this.graficoIrrigacaoPizza) {
      this.graficoIrrigacaoPizza.destroy();
    }
    
    // Criar novo gráfico
    this.graficoIrrigacaoPizza = new Chart(canvas, {
      type: 'pie',
      data: {
        labels: ['Irrigação Necessária', 'Precipitação Natural'],
        datasets: [{
          data: [porcentagemIrrigacao, porcentagemPrecipitacao],
          backgroundColor: ['#36a2eb', '#4bc0c0'],
          borderColor: ['#fff', '#fff'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 10
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.raw || 0;
                return `${label}: ${value.toFixed(1)}%`;
              }
            }
          }
        }
      }
    });
  }

  /**
   * Adiciona o resultado do cálculo às recomendações de cultivo
   */
  adicionarRecomendacaoIrrigacao() {
    console.log('Adicionando recomendação de irrigação às recomendações de cultivo...');
    
    const recomendacoesElement = document.getElementById('lista-recomendacoes-cultivo');
    const recomendacoesCard = document.getElementById('recomendacoes-cultivo');
    
    console.log('Elementos encontrados:', {
      recomendacoesElement: !!recomendacoesElement,
      recomendacoesCard: !!recomendacoesCard
    });
    
    if (recomendacoesElement) {
      // Cria um elemento para a recomendação
      const recomendacaoItem = document.createElement('div');
      recomendacaoItem.className = 'recomendacao-item mt-3';
      
      // Extrair dados do resultado
      const parametros = this.resultadoIrrigacao.parametrosCalculados;
      const parametrosBase = this.resultadoIrrigacao.parametrosBase;
      const cultura = this.dadosFormulario.respostas.etapa_1.valor;
      const frequencia = parametros.frequenciaDias;
      const laminaBruta = parametros.laminaBrutaAplicarMM;
      const laminaLiquida = parametros.laminaLiquidaAplicarMM;
      const eficiencia = parametrosBase.eficienciaIrrigacao_Ei;
      const etcDiaria = parametrosBase.ETc_diaria_mm;
    
    // Criar HTML com informações mais claras
    recomendacaoItem.innerHTML = `
      <div class="card border-0 shadow-sm mb-3">
        <div class="card-body">

          <div class="row">
            <div class="col-md-6">

              
              <div class="mb-3">
                <h6 class="fw-bold text-secondary">📊 Resumo do Cálculo</h6>
                <div class="bg-light p-3 rounded">
                  <div class="row g-2">
                    <div class="col-6">
                      <small class="text-muted">Cultura:</small><br>
                      <span class="fw-bold">${cultura}</span>
                    </div>
                    <div class="col-6">
                      <small class="text-muted">ETc Diária:</small><br>
                      <span class="fw-bold">${etcDiaria.toFixed(2)} mm/dia</span>
                    </div>
                    <div class="col-6">
                      <small class="text-muted">Frequência:</small><br>
                      <span class="fw-bold text-info">${frequencia} dias</span>
                    </div>
                    <div class="col-6">
                      <small class="text-muted">Eficiência:</small><br>
                      <span class="fw-bold text-success">${(eficiencia * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="alert alert-info mb-0">
                <h6 class="alert-heading"><i class="fas fa-lightbulb me-2"></i>Recomendação</h6>
                <p class="mb-2">${this.resultadoIrrigacao.recomendacao}</p>
                <hr>
                <div class="row text-center">
                  <div class="col-4">
                    <div class="fw-bold text-primary">${laminaBruta} mm</div>
                    <small class="text-muted">Lâmina Bruta</small>
                  </div>
                  <div class="col-4">
                    <div class="fw-bold text-success">${laminaLiquida} mm</div>
                    <small class="text-muted">Lâmina Líquida</small>
                  </div>
                  <div class="col-4">
                    <div class="fw-bold text-info">${frequencia} dias</div>
                    <small class="text-muted">Intervalo</small>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="chart-container" style="position: relative; height: 200px;">
                <canvas id="grafico-irrigacao-pizza"></canvas>
              </div>
            </div>
          </div>
          <div class="small text-muted mt-3">Cálculo baseado na Circular Técnica 136 da Embrapa</div>
        </div>
      </div>
    `;

      // Limpar o indicador de carregamento
      recomendacoesElement.innerHTML = '';
      
      // Adiciona à lista de recomendações
      recomendacoesElement.appendChild(recomendacaoItem);
      console.log('Recomendação adicionada com sucesso');
    
    // Garante que o card de recomendações esteja visível
    if (recomendacoesCard) {
      recomendacoesCard.style.display = 'block';
      console.log('Card de recomendações agora está visível');
    } else {
      console.warn('Card de recomendações não encontrado, mas a recomendação foi adicionada à lista');
    }
    
      // Criar o gráfico de pizza após um pequeno delay para garantir que o canvas esteja pronto
      setTimeout(() => {
        this.criarGraficoIrrigacaoPizza();
      }, 100);
    } else {
      console.error('Elemento lista-recomendacoes-cultivo não encontrado. Criando elemento...');
      
      // Tenta encontrar o card de recomendações
      if (!recomendacoesCard) {
        console.error('Card recomendacoes-cultivo não encontrado. Criando card...');
        
        // Cria o card de recomendações se não existir
        const secaoCultivo = document.getElementById('section-cultivo');
        if (secaoCultivo) {
          const novoCard = document.createElement('div');
          novoCard.id = 'recomendacoes-cultivo';
          novoCard.className = 'content-card';
          novoCard.style.marginBottom = '20px';
          novoCard.innerHTML = `
            <div class="card-title">
              <span class="card-icon">💡</span>
              Recomendações de Irrigação
            </div>
            <div class="card-description" id="lista-recomendacoes-cultivo">
              <!-- Será preenchido dinamicamente -->
            </div>
          `;
          
          // Insere o card no início da seção de cultivo
          const primeiroElemento = secaoCultivo.querySelector('.cards-grid');
          secaoCultivo.insertBefore(novoCard, primeiroElemento);
          
          console.log('Card de recomendações criado com sucesso');
          
          // Agora tenta adicionar a recomendação novamente
          setTimeout(() => {
            this.adicionarRecomendacaoIrrigacao();
            // Criar o gráfico de pizza após adicionar a recomendação
            setTimeout(() => this.criarGraficoIrrigacaoPizza(), 100);
          }, 100);
        } else {
          console.error('Seção de cultivo não encontrada. Não foi possível criar o card de recomendações.');
        }
      }
    }
  }
}

/**
 * Cria dados climáticos de exemplo para teste
 */
IrrigacaoManager.prototype.criarDadosClimaticosExemplo = function() {
  return {
    dados_grafico_balanco_hidrico: {
      dados: {
        series: [
          { nome: 'Precipitação', valores: [120, 130, 110, 90, 80, 70, 60, 50, 60, 80, 100, 110] },
          { nome: 'Evapotranspiração', valores: [80, 85, 90, 95, 100, 105, 110, 115, 110, 100, 90, 85] }
        ]
      }
    },
    dados_grafico_precipitacao: {
      dados: {
        series: [
          { nome: 'Precipitação', valores: [120, 130, 110, 90, 80, 70, 60, 50, 60, 80, 100, 110] }
        ]
      }
    }
  };
};

// Função para inicializar o gerenciador (será chamada pelo app-navegacao.js)
function inicializarIrrigacaoManager() {
  if (!window.irrigacaoManager) {
    console.log('Inicializando IrrigacaoManager...');
    try {
      window.irrigacaoManager = new IrrigacaoManager();
      console.log('IrrigacaoManager inicializado com sucesso!');
      return window.irrigacaoManager;
    } catch (error) {
      console.error('Erro ao inicializar IrrigacaoManager:', error);
      return null;
    }
  } else {
    console.log('IrrigacaoManager já está inicializado');
    return window.irrigacaoManager;
  }
}