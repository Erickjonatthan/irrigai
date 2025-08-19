// JavaScript para navegação do aplicativo - Irriga.ai

class IrrigaApp {
    constructor() {
        this.secaoAtual = 'home';
        this.dadosUsuario = null;
        this.graficoAtual = null; // Para controlar a instância do Chart.js
        this.init();
    }

    init() {
        this.criarEventListeners();
        this.carregarDadosUsuario();
        this.mostrarSecao('home');
    }

    criarEventListeners() {
        // Navegação inferior
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const secao = item.getAttribute('data-section');
                this.mostrarSecao(secao);
            });
        });

        // Botões de ação dos cards
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('card-button')) {
                this.processarAcaoCard(e.target);
            }
        });
    }

    mostrarSecao(secao) {
        // Limpar gráfico anterior se estivermos saindo da seção home
        if (this.secaoAtual === 'home' && secao !== 'home' && this.graficoAtual) {
            this.graficoAtual.destroy();
            this.graficoAtual = null;
        }

        // Esconder todas as seções
        document.querySelectorAll('.app-section').forEach(section => {
            section.classList.remove('active');
        });

        // Remover estado ativo de todos os itens de navegação
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });

        // Mostrar seção selecionada
        const secaoElement = document.getElementById(`section-${secao}`);
        const navItem = document.querySelector(`[data-section="${secao}"]`);
        
        if (secaoElement) {
            secaoElement.classList.add('active');
        }
        
        if (navItem) {
            navItem.classList.add('active');
        }

        this.secaoAtual = secao;
        
        // Carregar conteúdo específico da seção
        this.carregarConteudoSecao(secao);
    }

    carregarConteudoSecao(secao) {
        switch(secao) {
            case 'home':
                this.carregarHome();
                break;
            case 'cultivo':
                this.carregarCultivo();
                break;
            case 'noticias':
                this.carregarNoticias();
                break;
            case 'configuracoes':
                this.carregarConfiguracoes();
                break;
        }
    }

    carregarHome() {
        const welcomeElement = document.querySelector('.welcome-subtitle');
        if (welcomeElement && this.dadosUsuario) {
            const horaAtual = new Date().getHours();
            let saudacao = 'Bom dia';
            if (horaAtual >= 12 && horaAtual < 18) {
                saudacao = 'Boa tarde';
            } else if (horaAtual >= 18) {
                saudacao = 'Boa noite';
            }
            
            welcomeElement.textContent = `${saudacao}! Como está sua plantação hoje?`;
        }

        // Carregar dados específicos da análise para a home
        this.carregarDadosHome();
    }

    async carregarDadosHome() {
        try {
            // Carregar dados da análise
            const responseAnalise = await fetch('/api/dados-analise');
            if (responseAnalise.ok) {
                const dadosAnalise = await responseAnalise.json();
                this.exibirDadosHome(dadosAnalise);
            } else {
                this.exibirStatusSemDados();
            }
        } catch (error) {
            console.error('Erro ao carregar dados da home:', error);
            this.exibirStatusSemDados();
        }
    }

    exibirDadosHome(dados) {
        // Atualizar informações de localização
        const localizacaoElement = document.getElementById('dados-localizacao');
        if (localizacaoElement && dados.localizacao) {
            localizacaoElement.innerHTML = `
                <div style="text-align: left;">
                    <div style="margin-bottom: 8px;">
                        <strong>${dados.localizacao.nome_local}</strong>
                    </div>
                    <div style="font-size: 0.85rem; color: #6c757d;">
                        📍 Lat: ${dados.localizacao.latitude}°, Long: ${dados.localizacao.longitude}°
                    </div>
                    <div style="font-size: 0.85rem; color: #6c757d;">
                        📐 Área: ${dados.localizacao.area} km²
                    </div>
                    <div style="font-size: 0.85rem; color: #6c757d;">
                        📅 Período: ${dados.localizacao.periodo}
                    </div>
                </div>
            `;
        }

        // Atualizar dados climáticos
        const climaElement = document.getElementById('dados-clima');
        if (climaElement && dados.clima) {
            climaElement.innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center; font-size: 0.85rem;">
                    <div style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 6px;">
                        <div style="font-weight: 600;">Precipitação Média</div>
                        <div style="font-size: 1.1rem; margin-top: 4px;">${dados.clima.precipitacao_media} mm</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.2); padding: 8px; border-radius: 6px;">
                        <div style="font-weight: 600;">Índice de Aridez</div>
                        <div style="font-size: 1.1rem; margin-top: 4px;">${dados.clima.indice_aridez}</div>
                    </div>
                </div>
            `;
        }

        // Atualizar status da análise
        const statusElement = document.getElementById('status-analise');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="card-title">
                    <span class="card-icon">📊</span>
                    Análise Disponível
                </div>
                <div class="card-description">
                    Última análise realizada em ${dados.data_analise || 'data não disponível'}. 
                    Todos os dados estão atualizados e prontos para visualização.
                </div>
                <button class="card-button" data-action="ver-analise">
                    Ver Análise Completa
                </button>
            `;
        }

        // Exibir índices principais
        if (dados.indices && dados.indices.length > 0) {
            const indicesElement = document.getElementById('indices-principais');
            const dadosIndices = document.getElementById('dados-indices');
            
            if (indicesElement && dadosIndices) {
                let indicesHTML = '<div style="font-size: 0.85rem;">';
                dados.indices.slice(0, 3).forEach(indice => {
                    indicesHTML += `<div style="margin-bottom: 6px;">• ${indice}</div>`;
                });
                if (dados.indices.length > 3) {
                    indicesHTML += `<div style="color: #6c757d; font-style: italic;">+${dados.indices.length - 3} outros índices</div>`;
                }
                indicesHTML += '</div>';
                
                dadosIndices.innerHTML = indicesHTML;
                indicesElement.style.display = 'block';
            }
        }

        // Exibir gráfico de precipitação
        if (dados.grafico_precipitacao) {
            const titulo = dados?.localizacao?.nome_local
                ? `Precipitação Anual - ${dados.localizacao.nome_local}`
                : 'Precipitação Anual';
            this.exibirGraficoRapido({ ...dados.grafico_precipitacao, titulo });
        }

        // Exibir mapa de aridez
        if (dados.mapa_IA) {
            this.exibirMapaAridez(dados.mapa_IA);
        }

        // Salvar recomendações para a seção de cultivo
        this.dadosRecomendacoes = dados.recomendacoes;
    }

    exibirStatusSemDados() {
        // Informações de localização - loading padrão
        const localizacaoElement = document.getElementById('dados-localizacao');
        if (localizacaoElement) {
            localizacaoElement.innerHTML = `
                <div style="text-align: center; color: #6c757d;">
                    <div style="margin-bottom: 8px;">📍</div>
                    <div style="font-size: 0.9rem;">Nenhuma análise encontrada</div>
                    <div style="font-size: 0.8rem;">Realize uma nova análise para ver os dados da sua propriedade</div>
                </div>
            `;
        }

        // Dados climáticos - sem dados
        const climaElement = document.getElementById('dados-clima');
        if (climaElement) {
            climaElement.innerHTML = `
                <div style="text-align: center; color: rgba(255,255,255,0.8); padding: 15px;">
                    <div style="margin-bottom: 8px;">🌤️</div>
                    <div style="font-size: 0.9rem;">Dados climáticos indisponíveis</div>
                    <div style="font-size: 0.8rem;">Realize uma análise para acessar previsões personalizadas</div>
                </div>
            `;
        }

        // Status da análise - sem dados
        const statusElement = document.getElementById('status-analise');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="card-title">
                    <span class="card-icon">📍</span>
                    Análise Pendente
                </div>
                <div class="card-description">
                    Realize uma nova análise para obter dados atualizados sobre sua cultura e localização.
                </div>
                <button class="card-button" data-action="nova-analise">
                    Nova Análise
                </button>
            `;
        }
    }

    exibirGraficoRapido(dadosGrafico) {
        const graficoContainer = document.getElementById('grafico-rapido');
        if (!graficoContainer || !dadosGrafico) return;

        graficoContainer.style.display = 'block';

        const carregarGraficosLibs = () => new Promise((resolve) => {
            const precisaChart = (typeof Chart === 'undefined');
            const precisaManager = (typeof GraficosManager === 'undefined');

            const next = () => {
                if (!precisaManager) return resolve();
                const s2 = document.createElement('script');
                s2.src = '/static/js/graficos.js';
                s2.onload = resolve;
                document.head.appendChild(s2);
            };

            if (precisaChart) {
                const s1 = document.createElement('script');
                s1.src = 'https://cdn.jsdelivr.net/npm/chart.js';
                s1.onload = next;
                document.head.appendChild(s1);
            } else {
                next();
            }
        });

        carregarGraficosLibs().then(() => {
            // Normalizar dados para o formato do painel
            let dadosPainel = dadosGrafico;
            if (dadosGrafico.anos && dadosGrafico.valores) {
                dadosPainel = {
                    titulo: dadosGrafico.titulo || 'Precipitação Anual',
                    tipo: 'bar',
                    dados: {
                        anos: dadosGrafico.anos,
                        series: [{ nome: 'Precipitação (mm)', valores: dadosGrafico.valores, cor: '#4682B4' }]
                    },
                    eixos: { x: 'Ano', y: 'Precipitação (mm)' }
                };
            }

            // Destruir qualquer gráfico anterior no mesmo canvas via manager global
            try { if (window.graficosManager) window.graficosManager.destruirGraficos(); } catch (_) {}

            const manager = new GraficosManager();
            window.graficosManager = manager;
            manager.criarGrafico('grafico-precipitacao', dadosPainel);
        });
    }

    // Helper para destruir gráfico existente por canvasId e referência local
    destruirGraficoCanvas(canvasId) {
        try {
            if (typeof Chart !== 'undefined' && Chart.getChart) {
                const existente = Chart.getChart(canvasId) || Chart.getChart(document.getElementById(canvasId));
                if (existente) existente.destroy();
            }
        } catch (_) {}
        if (this.graficoAtual) {
            try { this.graficoAtual.destroy(); } catch (_) {}
            this.graficoAtual = null;
        }
    }

    criarGraficoRapido(dados) {
        const ctx = document.getElementById('grafico-home-precipitacao');
        if (!ctx) return;

        // Destruir gráfico anterior se existir (robusto)
        this.destruirGraficoCanvas('grafico-home-precipitacao');

        // Usar dados reais se disponíveis, senão usar dados de exemplo
        let dadosParaGrafico = dados;
        // Caso 1: forma simples {anos, valores}
        if (dadosParaGrafico && Array.isArray(dadosParaGrafico.anos) && Array.isArray(dadosParaGrafico.valores)) {
            this.criarGraficoComDados(ctx, {
                anos: dadosParaGrafico.anos,
                valores: dadosParaGrafico.valores,
                titulo: dadosParaGrafico.titulo || 'Precipitação Anual'
            });
            return;
        }
        // Caso 2: sem estrutura esperada -> buscar API
        if (!dadosParaGrafico || !dadosParaGrafico.dados || !dadosParaGrafico.dados.series) {
            // Tentar carregar dados reais da API
            this.carregarDadosGraficoReais().then(dadosReais => {
                if (dadosReais) {
                    this.criarGraficoComDados(ctx, dadosReais);
                } else {
                    this.criarGraficoComDadosExemplo(ctx);
                }
            });
            return;
        }

        // Usar dados reais estruturados
        const serie = dadosParaGrafico.dados.series[0];
        this.graficoAtual = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dadosParaGrafico.dados.anos,
                datasets: [{
                    label: serie.nome,
                    data: serie.valores,
                    backgroundColor: serie.cor || 'rgba(0, 123, 255, 0.8)',
                    borderColor: serie.cor || 'rgba(0, 123, 255, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: dadosParaGrafico.titulo || 'Precipitação Anual'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: dadosParaGrafico.eixos?.y || 'Precipitação (mm)'
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: dadosParaGrafico.eixos?.x || 'Ano'
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    async carregarDadosGraficoReais() {
        try {
            const response = await fetch('/api/dados-grafico-precipitacao');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Erro ao carregar dados do gráfico:', error);
        }
        return null;
    }

    criarGraficoComDados(ctx, dados) {
        // Destruir gráfico anterior se existir (robusto)
        this.destruirGraficoCanvas('grafico-home-precipitacao');

        this.graficoAtual = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dados.anos || dados.labels,
                datasets: [{
                    label: 'Precipitação (mm)',
                    data: dados.valores || dados.data,
                    backgroundColor: 'rgba(0, 123, 255, 0.8)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: dados.titulo || 'Precipitação Anual'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Precipitação (mm)'
                        },
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Ano'
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    criarGraficoComDadosExemplo(ctx) {
        // Destruir gráfico anterior se existir (robusto)
        this.destruirGraficoCanvas('grafico-home-precipitacao');

        const dadosExemplo = {
            anos: [2020, 2021, 2022, 2023, 2024],
            valores: [800, 650, 1200, 900, 750]
        };

        this.graficoAtual = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dadosExemplo.anos,
                datasets: [{
                    label: 'Precipitação (mm)',
                    data: dadosExemplo.valores,
                    backgroundColor: 'rgba(0, 123, 255, 0.8)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    exibirRecomendacoesRapidas(recomendacoes) {
        const container = document.getElementById('recomendacoes-rapidas');
        const lista = document.getElementById('lista-recomendacoes');
        
        if (container && lista && recomendacoes.length > 0) {
            let html = '<div style="text-align: left; font-size: 0.9rem;">';
            recomendacoes.slice(0, 3).forEach((rec, index) => {
                html += `<div style="margin-bottom: 8px; display: flex; align-items: flex-start; gap: 8px;">
                    <span style="color: #28a745; font-weight: 600; flex-shrink: 0;">${index + 1}.</span>
                    <span>${rec}</span>
                </div>`;
            });
            
            if (recomendacoes.length > 3) {
                html += `<div style="margin-top: 12px; text-align: center; color: #6c757d; font-size: 0.8rem;">
                    +${recomendacoes.length - 3} outras recomendações na análise completa
                </div>`;
            }
            
            html += '</div>';
            lista.innerHTML = html;
            container.style.display = 'block';
        }
    }

    exibirMapaAridez(caminhoMapa) {
        const container = document.getElementById('mapa-aridez');
        const iframe = document.getElementById('iframe-mapa');
        const expandBtn = document.getElementById('expandir-mapa');
        // Criar/obter elemento img para quando o recurso for uma imagem
        let img = document.getElementById('img-mapa');
        if (!img && container) {
            img = document.createElement('img');
            img.id = 'img-mapa';
            img.style.display = 'none';
            img.alt = 'Mapa de Índice de Aridez';
            const mapaContainer = container.querySelector('.mapa-container');
            if (mapaContainer) mapaContainer.appendChild(img);
        }
        
        if (container && iframe && caminhoMapa) {
            // Construir a URL correta para o mapa
            const urlMapa = `/static/${caminhoMapa}`;
            const isImage = /\.(png|jpe?g|webp|gif)$/i.test(caminhoMapa);
            
            // Exibir como imagem (melhor centralização e contain) quando for arquivo de imagem
            if (isImage && img) {
                iframe.style.display = 'none';
                img.src = urlMapa;
                img.onload = () => {
                    container.querySelector('.loading-spinner').style.display = 'none';
                    container.querySelector('.loading-text').style.display = 'none';
                    img.style.display = 'block';
                };
                img.onerror = () => {
                    container.querySelector('.loading-spinner').style.display = 'none';
                    container.querySelector('.loading-text').textContent = 'Erro ao carregar o mapa';
                };
            } else {
                // Configurar o iframe (para HTML interativo)
                iframe.src = urlMapa;
                iframe.onload = function() {
                    container.querySelector('.loading-spinner').style.display = 'none';
                    container.querySelector('.loading-text').style.display = 'none';
                    iframe.style.display = 'block';
                };
                iframe.onerror = function() {
                    container.querySelector('.loading-spinner').style.display = 'none';
                    container.querySelector('.loading-text').textContent = 'Erro ao carregar o mapa';
                };
            }
            
            // Configurar botão de expansão usando modal Bootstrap existente
            if (expandBtn) {
                expandBtn.onclick = () => this.abrirMapaModal(urlMapa, isImage);
            }
            
            container.style.display = 'block';
        }
    }

    abrirMapaModal(urlMapa, isImage = false) {
        // Usar modal Bootstrap existente no template (#mapaModal)
        const modalEl = document.getElementById('mapaModal');
        const iframeModal = document.getElementById('iframe-mapa-modal');
        // Garantir elemento de imagem no modal
        let imgModal = document.getElementById('img-mapa-modal');
        if (!imgModal && modalEl) {
            imgModal = document.createElement('img');
            imgModal.id = 'img-mapa-modal';
            imgModal.style.display = 'none';
            imgModal.style.width = '100%';
            imgModal.style.height = '100%';
            imgModal.style.objectFit = 'contain';
            const body = modalEl.querySelector('.modal-body > div');
            if (body) body.appendChild(imgModal);
        }
        if (!modalEl || !iframeModal) return;

        // Alternar entre imagem e iframe
        if (isImage && imgModal) {
            iframeModal.style.display = 'none';
            imgModal.style.display = 'block';
            imgModal.src = urlMapa;
        } else {
            if (imgModal) {
                imgModal.style.display = 'none';
                imgModal.src = '';
            }
            iframeModal.style.display = 'block';
            iframeModal.src = urlMapa;
        }
        try {
            const modal = new bootstrap.Modal(modalEl);
            // Limpar src ao fechar para forçar reflow em reaberturas e liberar memória
            modalEl.addEventListener('hidden.bs.modal', () => {
                iframeModal.src = '';
                if (imgModal) imgModal.src = '';
            }, { once: true });
            modal.show();
        } catch (e) {
            // Fallback caso Bootstrap não esteja disponível
            window.open(urlMapa, '_blank');
        }
    }

    fecharMapaModal() {
        const modalEl = document.getElementById('mapaModal');
        if (!modalEl) return;
        try {
            const instance = bootstrap.Modal.getInstance(modalEl);
            if (instance) instance.hide();
        } catch (_) {}
    }

    exibirRecomendacoesCultivo(recomendacoes) {
        const container = document.getElementById('recomendacoes-cultivo');
        const lista = document.getElementById('lista-recomendacoes-cultivo');
        
        if (container && lista && recomendacoes.length > 0) {
            let html = '<div style="text-align: left; font-size: 0.9rem;">';
            recomendacoes.forEach((rec, index) => {
                html += `<div style="margin-bottom: 12px; display: flex; align-items: flex-start; gap: 10px;">
                    <div class="recomendacao-numero">${index + 1}</div>
                    <div class="recomendacao-texto">${rec}</div>
                </div>`;
            });
            html += '</div>';
            
            lista.innerHTML = html;
            container.style.display = 'block';
        }
    }

    carregarCultivo() {
        // Carregar dados específicos do cultivo
        console.log('Carregando dados do cultivo...');
        
        // Verificar se há dados de análise disponíveis
        this.verificarDadosAnalise();

        // Exibir recomendações na seção cultivo
        if (this.dadosRecomendacoes && this.dadosRecomendacoes.length > 0) {
            this.exibirRecomendacoesCultivo(this.dadosRecomendacoes);
        }
    }

    carregarNoticias() {
        // Carregar notícias relacionadas à agricultura
        console.log('Carregando notícias...');
        
        // Aqui você pode fazer uma chamada para API de notícias
        this.carregarNoticiasExternas();
    }

    carregarConfiguracoes() {
        // Carregar configurações do usuário
        console.log('Carregando configurações...');
    }

    async carregarDadosUsuario() {
        try {
            // Aqui você faria uma chamada para o backend para pegar dados do usuário
            // Por enquanto, vamos simular
            this.dadosUsuario = {
                nome: 'Usuário',
                ultimaAnalise: null,
                configFormulario: null
            };
        } catch (error) {
            console.error('Erro ao carregar dados do usuário:', error);
        }
    }

    async verificarDadosAnalise() {
        try {
            const response = await fetch('/verificar-dados-analise');
            const dados = await response.json();
            
            if (dados.temDados) {
                this.atualizarStatusAnalise(true);
            } else {
                this.atualizarStatusAnalise(false);
            }
        } catch (error) {
            console.error('Erro ao verificar dados de análise:', error);
            this.atualizarStatusAnalise(false);
        }
    }

    atualizarStatusAnalise(temDados) {
        const statusElement = document.getElementById('status-analise');
        if (statusElement) {
            if (temDados) {
                statusElement.innerHTML = `
                    <div class="card-title">
                        <span class="card-icon">📊</span>
                        Análise Disponível
                    </div>
                    <div class="card-description">
                        Seus dados de análise estão prontos para visualização.
                    </div>
                    <button class="card-button" data-action="ver-analise">
                        Ver Análise
                    </button>
                `;
            } else {
                statusElement.innerHTML = `
                    <div class="card-title">
                        <span class="card-icon">📍</span>
                        Análise Pendente
                    </div>
                    <div class="card-description">
                        Realize uma nova análise para obter dados atualizados sobre sua cultura.
                    </div>
                    <button class="card-button" data-action="nova-analise">
                        Nova Análise
                    </button>
                `;
            }
        }
    }

    async carregarNoticiasExternas() {
        const noticiasContainer = document.getElementById('noticias-container');
        if (!noticiasContainer) return;

        // Mostrar loading
        noticiasContainer.innerHTML = `
            <div class="loading-state">
                <div class="loading-spinner"></div>
                <div class="loading-text">Carregando notícias...</div>
            </div>
        `;

        try {
            // Simular carregamento de notícias
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            const noticias = [
                {
                    titulo: "Técnicas de Irrigação Sustentável",
                    descricao: "Novas metodologias para economizar água na agricultura.",
                    fonte: "Portal Agricultura",
                    tempo: "2 horas atrás"
                },
                {
                    titulo: "Previsão Climática para Agosto",
                    descricao: "Análise das condições meteorológicas para o mês.",
                    fonte: "Clima Rural",
                    tempo: "5 horas atrás"
                },
                {
                    titulo: "Inovações em Monitoramento de Solo",
                    descricao: "Sensores inteligentes revolucionam a agricultura.",
                    fonte: "Tech Agro",
                    tempo: "1 dia atrás"
                }
            ];

            let noticiasHTML = '';
            noticias.forEach(noticia => {
                noticiasHTML += `
                    <div class="content-card slide-up">
                        <div class="card-title">
                            <span class="card-icon">📰</span>
                            ${noticia.titulo}
                        </div>
                        <div class="card-description">
                            ${noticia.descricao}
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                            <small class="text-muted">${noticia.fonte}</small>
                            <small class="text-muted">${noticia.tempo}</small>
                        </div>
                    </div>
                `;
            });

            noticiasContainer.innerHTML = noticiasHTML;
        } catch (error) {
            console.error('Erro ao carregar notícias:', error);
            noticiasContainer.innerHTML = `
                <div class="content-card">
                    <div class="card-title">
                        <span class="card-icon">⚠️</span>
                        Erro ao Carregar
                    </div>
                    <div class="card-description">
                        Não foi possível carregar as notícias no momento.
                    </div>
                    <button class="card-button secondary" onclick="window.irrigaApp.carregarNoticias()">
                        Tentar Novamente
                    </button>
                </div>
            `;
        }
    }

    processarAcaoCard(botao) {
        const acao = botao.getAttribute('data-action');
        
        switch(acao) {
            case 'ver-analise':
                window.location.href = '/painel';
                break;
            case 'nova-analise':
                window.location.href = '/form';
                break;
            case 'ver-previsao':
                this.mostrarPrevisaoDetalhada();
                break;
            case 'configurar-perfil':
                this.mostrarConfiguracoesPerfil();
                break;
            case 'sobre-app':
                this.mostrarSobreApp();
                break;
            default:
                console.log('Ação não implementada:', acao);
        }
    }

    mostrarPrevisaoDetalhada() {
        // Implementar modal ou nova tela com previsão detalhada
        console.log('Mostrar previsão detalhada');
    }

    mostrarConfiguracoesPerfil() {
        // Implementar configurações de perfil
        console.log('Mostrar configurações de perfil');
    }

    mostrarSobreApp() {
        // Implementar informações sobre o app
        alert('Irriga.ai v1.0\n\nAplicativo desenvolvido para auxiliar agricultores na tomada de decisões sobre irrigação e monitoramento climático.');
    }

    // Método para atualizar dados em tempo real
    async atualizarDados() {
        if (this.secaoAtual === 'home' || this.secaoAtual === 'cultivo') {
            await this.verificarDadosAnalise();
        }
    }
}

// Inicializar aplicativo quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    window.irrigaApp = new IrrigaApp();
    
    // Atualizar dados a cada 5 minutos
    setInterval(() => {
        window.irrigaApp.atualizarDados();
    }, 300000);
});
