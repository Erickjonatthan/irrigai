class GraficosManager {
    constructor() {
        this.charts = {};
        this.cores = {
            primaria: '#2E8B57',
            secundaria: '#4682B4', 
            terciaria: '#DC143C',
            quaternaria: '#FF8C00',
            quinquenaria: '#9370DB'
        };
    }

    /**
     * Inicializa todos os gráficos na página
     */
    async inicializarGraficos(dadosResultados) {
        if (!dadosResultados) {
            console.error('Dados dos resultados não fornecidos');
            return;
        }

        try {
            // Carrega a biblioteca Chart.js se não estiver disponível
            await this.carregarChartJS();

            // Cria cada tipo de gráfico
            if (dadosResultados.grafico_precipitacao) {
                this.criarGraficoPrecipitacao(dadosResultados.grafico_precipitacao);
            }

            if (dadosResultados.grafico_balanco_hidrico) {
                this.criarGraficoBalancoHidrico(dadosResultados.grafico_balanco_hidrico);
            }

            if (dadosResultados.grafico_aridez) {
                this.criarGraficoAridez(dadosResultados.grafico_aridez);
            }

            if (dadosResultados.grafico_rai) {
                this.criarGraficoRAI(dadosResultados.grafico_rai);
            }

            if (dadosResultados.grafico_precipitacao_vs_evaporacao) {
                this.criarGraficoPrecipitacaoVsEvaporacao(dadosResultados.grafico_precipitacao_vs_evaporacao);
            }

        } catch (error) {
            console.error('Erro ao inicializar gráficos:', error);
        }
    }

    /**
     * Carrega a biblioteca Chart.js dinamicamente
     */
    async carregarChartJS() {
        if (typeof Chart !== 'undefined') {
            return; // Já está carregado
        }

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }    /**
     * Método genérico para criar gráficos baseado no ID
     */
    criarGrafico(elementId, dados) {
        // Se os dados são uma string (caminho de imagem) ou nulos, gerar dados de exemplo
        if (typeof dados === 'string' || !dados) {
            dados = this.gerarDadosExemplo(elementId);
        }

        // Criar gráfico interativo
        switch (elementId) {
            case 'grafico-precipitacao':
                return this.criarGraficoPrecipitacao(dados);
            case 'grafico-balanco-hidrico':
                return this.criarGraficoBalancoHidrico(dados);
            case 'grafico-aridez':
                return this.criarGraficoAridez(dados);
            case 'grafico-rai':
                return this.criarGraficoRAI(dados);
            case 'grafico-precipitacao-evaporacao':
                return this.criarGraficoPrecipitacaoVsEvaporacao(dados);
            default:
                console.error(`Tipo de gráfico não reconhecido: ${elementId}`);
                return null;
        }
    }

    /**
     * Gera dados de exemplo para gráficos quando dados reais não estão disponíveis
     */
    gerarDadosExemplo(elementId) {
        const anos = Array.from({length: 19}, (_, i) => 2004 + i);
        
        switch (elementId) {
            case 'grafico-precipitacao':
                return {
                    titulo: "Precipitação Anual (Dados de Exemplo)",
                    tipo: "bar",
                    dados: {
                        anos: anos,
                        series: [{
                            nome: "Precipitação (mm)",
                            valores: [800, 650, 1200, 900, 450, 1100, 750, 850, 950, 700, 800, 650, 1000, 550, 900, 750, 1200, 850, 600],
                            cor: "#4682B4"
                        }]
                    },
                    eixos: { x: "Ano", y: "Precipitação (mm)" }
                };
            
            case 'grafico-aridez':
                return {
                    titulo: "Índice de Aridez (Dados de Exemplo)",
                    tipo: "line",
                    dados: {
                        anos: anos,
                        series: [{
                            nome: "Índice de Aridez",
                            valores: [0.4, 0.35, 0.6, 0.45, 0.25, 0.55, 0.38, 0.42, 0.48, 0.35, 0.4, 0.33, 0.5, 0.28, 0.45, 0.38, 0.6, 0.43, 0.3],
                            cor: "#2E8B57"
                        }]
                    },
                    eixos: { x: "Ano", y: "Índice de Aridez" }
                };
                
            case 'grafico-rai':
                return {
                    titulo: "Rain Anomaly Index (RAI) - Dados de Exemplo",
                    tipo: "bar",
                    dados: {
                        anos: anos,
                        series: [{
                            nome: "RAI",
                            valores: [15, -10, 25, 5, -20, 18, -5, 12, 8, -15, 10, -8, 20, -25, 6, -3, 22, 3, -12],
                            cor: "#4169E1"
                        }]
                    },
                    eixos: { x: "Ano", y: "RAI" }
                };
                
            case 'grafico-balanco-hidrico':
                return {
                    titulo: "Balanço Hídrico Anual (Dados de Exemplo)",
                    tipo: "bar",
                    dados: {
                        anos: anos,
                        series: [
                            {
                                nome: "ET (Evapotranspiração)",
                                valores: [450, 380, 520, 420, 350, 480, 400, 440, 460, 380, 450, 370, 500, 340, 420, 400, 520, 450, 360],
                                cor: "#2E86AB"
                            },
                            {
                                nome: "PET (Evapotranspiração Potencial)",
                                valores: [650, 580, 720, 620, 550, 680, 600, 640, 660, 580, 650, 570, 700, 540, 620, 600, 720, 650, 560],
                                cor: "#A23B72"
                            },
                            {
                                nome: "Déficit Hídrico",
                                valores: [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200],
                                cor: "#F18F01"
                            }
                        ]
                    },
                    eixos: { x: "Ano", y: "Milímetros (mm)" }
                };
                
            case 'grafico-precipitacao-evaporacao':
                return {
                    titulo: "Precipitação e Evaporação Anuais (Dados de Exemplo)",
                    tipo: "line",
                    dados: {
                        anos: anos,
                        series: [
                            {
                                nome: "Precipitação",
                                valores: [800, 650, 1200, 900, 450, 1100, 750, 850, 950, 700, 800, 650, 1000, 550, 900, 750, 1200, 850, 600],
                                cor: "#1f77b4"
                            },
                            {
                                nome: "Evaporação",
                                valores: [450, 380, 520, 420, 350, 480, 400, 440, 460, 380, 450, 370, 500, 340, 420, 400, 520, 450, 360],
                                cor: "#ff7f0e"
                            }
                        ]
                    },
                    eixos: { x: "Ano", y: "Total Anual (mm)" }
                };
                
            default:
                return null;
        }
    }    /**
     * Cria gráfico de precipitação
     */
    criarGraficoPrecipitacao(dados) {
        const ctx = document.getElementById('grafico-precipitacao');
        if (!ctx) {
            console.error('Canvas grafico-precipitacao não encontrado');
            return;
        }

        console.log('Dados recebidos para precipitação:', dados);

        // Verificar se os dados têm a estrutura esperada
        if (!dados || !dados.dados) {
            console.error('Estrutura de dados inválida para gráfico de precipitação');
            return;
        }

        this.charts.precipitacao = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dados.dados.anos || dados.anos || [],
                datasets: [{
                    label: dados.dados.series?.[0]?.nome || dados.series?.[0]?.nome || 'Precipitação',
                    data: dados.dados.series?.[0]?.valores || dados.series?.[0]?.valores || [],
                    backgroundColor: dados.dados.series?.[0]?.cor || dados.series?.[0]?.cor || this.cores.secundaria,
                    borderColor: this.darkenColor(dados.dados.series?.[0]?.cor || dados.series?.[0]?.cor || this.cores.secundaria),
                    borderWidth: 2,
                    hoverBackgroundColor: this.lightenColor(dados.dados.series?.[0]?.cor || dados.series?.[0]?.cor || this.cores.secundaria),
                    hoverBorderWidth: 3
                }]
            },
            options: this.getDefaultOptions(dados.eixos?.x || 'Anos', dados.eixos?.y || 'Precipitação (mm)')
        });
    }    /**
     * Cria gráfico de balanço hídrico
     */
    criarGraficoBalancoHidrico(dados) {
        const ctx = document.getElementById('grafico-balanco-hidrico');
        if (!ctx) {
            console.error('Canvas grafico-balanco-hidrico não encontrado');
            return;
        }

        console.log('Dados recebidos para balanço hídrico:', dados);

        // Verificar se os dados têm a estrutura esperada
        if (!dados || (!dados.dados && !dados.anos)) {
            console.error('Estrutura de dados inválida para gráfico de balanço hídrico');
            return;
        }
        
        const series = dados.dados?.series || dados.series || [];
        const datasets = series.map((serie, index) => ({
            label: serie.nome || `Série ${index + 1}`,
            data: serie.valores || [],
            backgroundColor: serie.cor || Object.values(this.cores)[index],
            borderColor: this.darkenColor(serie.cor || Object.values(this.cores)[index]),
            borderWidth: 2,
            hoverBackgroundColor: this.lightenColor(serie.cor || Object.values(this.cores)[index]),
            hoverBorderWidth: 3
        }));

        this.charts.balancoHidrico = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dados.dados?.anos || dados.anos || [],
                datasets: datasets
            },
            options: {
                ...this.getDefaultOptions(dados.eixos?.x || 'Anos', dados.eixos?.y || 'mm'),
                scales: {
                    x: {
                        beginAtZero: true
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    /**
     * Cria gráfico de índice de aridez
     */    criarGraficoAridez(dados) {
        const ctx = document.getElementById('grafico-aridez');
        if (!ctx) {
            console.error('Canvas grafico-aridez não encontrado');
            return;
        }

        console.log('Dados recebidos para aridez:', dados);

        // Verificar se os dados têm a estrutura esperada
        if (!dados || (!dados.dados && !dados.anos)) {
            console.error('Estrutura de dados inválida para gráfico de aridez');
            return;
        }
        
        const series = dados.dados?.series || dados.series || [];
        const datasets = series.map((serie, index) => ({
            label: serie.nome || `Série ${index + 1}`,
            data: serie.valores || [],
            borderColor: serie.cor || Object.values(this.cores)[index],
            backgroundColor: serie.tipo === 'linha' ? 'transparent' : 
                           this.hexToRgba(serie.cor || Object.values(this.cores)[index], 0.1),
            fill: serie.tipo !== 'linha',
            tension: 0.4,
            pointBackgroundColor: serie.cor || Object.values(this.cores)[index],
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: serie.cor || Object.values(this.cores)[index],
            borderWidth: serie.tipo === 'linha' ? 3 : 2
        }));

        this.charts.aridez = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dados.dados?.anos || dados.anos || [],
                datasets: datasets
            },
            options: this.getDefaultOptions(dados.eixos?.x || 'Anos', dados.eixos?.y || 'Índice de Aridez')
        });
    }

    /**
     * Cria gráfico RAI
     */    criarGraficoRAI(dados) {
        const ctx = document.getElementById('grafico-rai');
        if (!ctx) {
            console.error('Canvas grafico-rai não encontrado');
            return;
        }

        console.log('Dados recebidos para RAI:', dados);

        // Verificar se os dados têm a estrutura esperada
        if (!dados || (!dados.dados && !dados.anos)) {
            console.error('Estrutura de dados inválida para gráfico RAI');
            return;
        }
        
        const series = dados.dados?.series || dados.series || [];
        const firstSeries = series[0] || {};
        
        // Cores diferentes para valores positivos e negativos
        const valores = firstSeries.valores || [];
        const backgroundColors = valores.map(valor => 
            valor >= 0 ? this.cores.primaria : this.cores.terciaria
        );

        this.charts.rai = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dados.dados?.anos || dados.anos || [],
                datasets: [{
                    label: firstSeries.nome || 'RAI',
                    data: valores,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(cor => this.darkenColor(cor)),
                    borderWidth: 2,
                    hoverBackgroundColor: backgroundColors.map(cor => this.lightenColor(cor)),
                    hoverBorderWidth: 3
                }]
            },
            options: {
                ...this.getDefaultOptions(dados.eixos?.x || 'Anos', dados.eixos?.y || 'RAI'),
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: function(context) {
                                if (context.tick.value === 0) {
                                    return '#000';
                                }
                                return '#e0e0e0';
                            },
                            lineWidth: function(context) {
                                if (context.tick.value === 0) {
                                    return 2;
                                }
                                return 1;
                            }
                        }
                    }
                }
            }
        });
    }    /**
     * Cria gráfico de precipitação vs evaporação
     */
    criarGraficoPrecipitacaoVsEvaporacao(dados) {
        const ctx = document.getElementById('grafico-precipitacao-evaporacao');
        if (!ctx) {
            console.error('Canvas grafico-precipitacao-evaporacao não encontrado');
            return;
        }

        console.log('Dados recebidos para precipitação vs evaporação:', dados);

        // Verificar se os dados têm a estrutura esperada
        if (!dados || (!dados.dados && !dados.anos)) {
            console.error('Estrutura de dados inválida para gráfico de precipitação vs evaporação');
            return;
        }
        
        const series = dados.dados?.series || dados.series || [];
        const datasets = series.map((serie, index) => ({
            label: serie.nome || `Série ${index + 1}`,
            data: serie.valores || [],
            borderColor: serie.cor || Object.values(this.cores)[index],
            backgroundColor: this.hexToRgba(serie.cor || Object.values(this.cores)[index], 0.1),
            fill: false,
            tension: 0.4,
            pointBackgroundColor: serie.cor || Object.values(this.cores)[index],
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: serie.cor || Object.values(this.cores)[index],
            borderWidth: 3
        }));

        this.charts.precipitacaoVsEvaporacao = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dados.dados?.anos || dados.anos || [],
                datasets: datasets
            },
            options: this.getDefaultOptions(dados.eixos?.x || 'Anos', dados.eixos?.y || 'mm')
        });
    }

    /**
     * Opções padrão para todos os gráficos
     */
    getDefaultOptions(xLabel, yLabel) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12,
                            family: 'Arial, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#fff',
                    borderWidth: 1,
                    cornerRadius: 6,
                    displayColors: true,
                    intersect: false,
                    mode: 'index'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: xLabel,
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: yLabel,
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        lineWidth: 1
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        };
    }

    /**
     * Utilitários para manipulação de cores
     */
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    darkenColor(hex, amount = 20) {
        const num = parseInt(hex.slice(1), 16);
        const amt = Math.round(2.55 * amount);
        const R = (num >> 16) - amt;
        const G = (num >> 8 & 0x00FF) - amt;
        const B = (num & 0x0000FF) - amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    lightenColor(hex, amount = 20) {
        const num = parseInt(hex.slice(1), 16);
        const amt = Math.round(2.55 * amount);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    /**
     * Destrói todos os gráficos criados
     */
    destruirGraficos() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

const graficosManager = new GraficosManager();
