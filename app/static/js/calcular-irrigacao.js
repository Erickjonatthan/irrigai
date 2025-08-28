// Realiza o cálculo da irrigação com base nas informações vindas do formulário e com os dados de ET e Precipitação.
// Calcula a Lâmina Bruta (LB) e a Frequência de Irrigação (F) com base em parâmetros detalhados do solo e da cultura.
/**
 * Calcula a Lâmina Bruta (LB) e a Frequência de Irrigação (F) com base em parâmetros detalhados do solo e da cultura.
 * Esta versão aprimorada utiliza as equações e tabelas (CAD, f, Z, Ei) da 'Circular Técnica 136' da Embrapa
 * para fornecer uma recomendação operacional de manejo.
 *
 * @param {object} dadosFormulario - O objeto JSON contendo as respostas do formulário do agricultor.
 * @param {object} dadosClimaticos - O objeto JSON com os dados históricos anuais de clima.
 * @returns {object} Um objeto com a recomendação de manejo e todos os parâmetros calculados.
 */
function calcularManejoDeIrrigacao(dadosFormulario, dadosClimaticos) {

  // --- ETAPA 1: Extrair parâmetros do formulário ---
  const cultura = dadosFormulario.respostas.etapa_1.valor; // Ex: "feijao"
  const tipoSolo = dadosFormulario.respostas.etapa_5.valor; // Ex: "arenoso"
  
  // NOTA: O formulário indica "Não utilizo irrigação". Para fins de cálculo,
  // assumiremos um sistema de "Aspersão Convencional Fixo". Em uma aplicação real,
  // esta informação deveria vir do formulário.
  const sistemaIrrigacao = 'aspersao_convencional_fixo';

  // --- ETAPA 2: Definir Tabelas de Referência (Baseado na Circular Técnica 136) ---

  // Tabela 1: Capacidade de Água Disponível (CAD) em mm/m.
  const TABELA_CAD_POR_SOLO = {
    'arenoso': 85,
    'franco-arenoso': 120,
    'franco': 170,
    'franco-argiloso': 190,
    'silto-argiloso': 210,
    'argiloso': 230
  };

  // Tabela 3: Profundidade efetiva do sistema radicular (Z) em cm.
  const TABELA_Z_POR_CULTURA = {
    'feijao': 25, // Média de 20-30 cm
    'milho': 45, // Média de 40-50 cm
    'soja': 45, // Média de 40-50 cm
    'algodao': 30,
    'tomate': 35 // Média de 20-50 cm
  };

  // Tabela 4: Eficiência de Irrigação (Ei) em decimal.
  const TABELA_EI_POR_SISTEMA = {
    'aspersao_convencional_fixo': 0.75, // Média de 70-80%
    'pivo_central': 0.825, // Média de 75-90%
    'gotejamento': 0.825 // Média de 75-90%
  };

  // Tabela 2: Fator de disponibilidade (f). Mapeia cultura para seu grupo e ETc para o valor de f.
  const GRUPO_CULTURA = { 'feijao': 3, 'milho': 4, 'soja': 4, 'tomate': 2, 'batata': 1 };
  const TABELA_F = {
    // ETm (mm/dia) ->   2      3      4      5      6      7      8      9      10
    1: [0.50, 0.425, 0.35, 0.30, 0.25, 0.225, 0.20, 0.20, 0.175],
    2: [0.675, 0.575, 0.475, 0.40, 0.35, 0.325, 0.275, 0.25, 0.225],
    3: [0.80, 0.70, 0.60, 0.50, 0.45, 0.425, 0.375, 0.35, 0.30],
    4: [0.875, 0.80, 0.70, 0.60, 0.55, 0.50, 0.45, 0.425, 0.40]
  };
  
  // Coeficiente de Cultura (Kc) médio para a fase principal do ciclo.
  const KC_POR_CULTURA = { 'feijao': 1.10, 'milho': 1.20, 'soja': 1.15, 'algodao': 1.18, 'tomate': 1.15 };

  // --- ETAPA 3: Processar dados climáticos e buscar parâmetros ---

  const calcularMedia = (arr) => {
    if (!arr || arr.length === 0) return 0;
    return arr.reduce((acc, val) => acc + val, 0) / arr.length;
  };
  
  let mediaAnualETo = 0;
  if (dadosClimaticos && dadosClimaticos.dados_grafico_balanco_hidrico && 
      dadosClimaticos.dados_grafico_balanco_hidrico.dados && 
      dadosClimaticos.dados_grafico_balanco_hidrico.dados.series && 
      dadosClimaticos.dados_grafico_balanco_hidrico.dados.series.length > 1) {
    mediaAnualETo = calcularMedia(dadosClimaticos.dados_grafico_balanco_hidrico.dados.series[1].valores);
  }
  
  const mediaDiariaETo = mediaAnualETo / 365;

  const kc = KC_POR_CULTURA[cultura] || 1.0;
  const etcDiaria = mediaDiariaETo * kc; // Esta é a nossa ETm para a Tabela 2

  // Busca dos parâmetros nas tabelas
  const cad_mm_por_m = TABELA_CAD_POR_SOLO[tipoSolo] || 170; // Padrão: Franco
  const Z_cm = TABELA_Z_POR_CULTURA[cultura] || 40; // Padrão: 40 cm
  const Ei = TABELA_EI_POR_SISTEMA[sistemaIrrigacao] || 0.75; // Padrão: 75%

  // Lógica para buscar 'f' na Tabela 2
  const grupo = GRUPO_CULTURA[cultura] || 3;
  const etIndex = Math.max(0, Math.min(Math.round(etcDiaria) - 2, 8)); // Ajusta ETc para o índice do array (2 a 10)
  const f = TABELA_F[grupo][etIndex];

  // --- ETAPA 4: Aplicar as Equações de Manejo ---

  // Converte CAD de mm/m para mm/cm para usar na fórmula
  const cad_mm_por_cm = cad_mm_por_m / 100;

  // Equação 1: Lâmina Líquida (LL)
  // LL = CAD (mm/cm) * f * Z (cm)
  const LL = cad_mm_por_cm * f * Z_cm;

  // Equação 4: Frequência de Irrigação (F)
  // F = LL (mm) / ETc (mm/dia)
  let F_dias = LL / etcDiaria;
  // Arredonda para baixo para o dia inteiro mais próximo, como recomendado no artigo.
  F_dias = Math.floor(F_dias);

  // Ajusta a lâmina líquida para a frequência arredondada (prática recomendada no exemplo 9.1)
  const LL_ajustada = F_dias * etcDiaria;

  // Equação 3: Lâmina Bruta (LB)
  // LB = LL (mm) / Ei (decimal)
  const LB = LL_ajustada / Ei;

  // --- ETAPA 5: Calcular porcentagens de irrigação vs precipitação ---
  
  // Extrair dados de precipitação da estrutura de dados climáticos
  let precipitacaoAnual = 0;
  
  if (dadosClimaticos.dados_grafico_precipitacao && 
      dadosClimaticos.dados_grafico_precipitacao.dados && 
      dadosClimaticos.dados_grafico_precipitacao.dados.series) {
    // Busca a série de precipitação
    const seriePrecipitacao = dadosClimaticos.dados_grafico_precipitacao.dados.series
      .find(serie => serie.nome === 'Precipitação');
    
    if (seriePrecipitacao && seriePrecipitacao.valores) {
      precipitacaoAnual = seriePrecipitacao.valores.reduce((acc, val) => acc + val, 0);
    }
  }
  
  // Se não encontrou dados de precipitação, usa um valor padrão baseado na região
  if (precipitacaoAnual === 0) {
    precipitacaoAnual = 1200; // Valor médio para o Brasil (mm/ano)
  }
  
  // Estimar necessidade anual de irrigação (baseado na frequência e lâmina bruta)
  const irrigacoesAnuais = Math.floor(365 / F_dias);
  const irrigacaoAnual = irrigacoesAnuais * LB;
  
  // Calcular porcentagens
  const totalAgua = precipitacaoAnual + irrigacaoAnual;
  const porcentagemPrecipitacao = totalAgua > 0 ? (precipitacaoAnual / totalAgua) * 100 : 0;
  const porcentagemIrrigacao = totalAgua > 0 ? (irrigacaoAnual / totalAgua) * 100 : 100;

  // --- ETAPA 6: Retornar o resultado ---
  return {
    recomendacao: `Para a cultura de ${cultura} em solo ${tipoSolo}, recomenda-se irrigar a cada ${F_dias} dias, aplicando uma lâmina bruta de ${LB.toFixed(1)} mm por evento.`,
    parametrosCalculados: {
      frequenciaDias: F_dias,
      laminaLiquidaAplicarMM: parseFloat(LL_ajustada.toFixed(2)),
      laminaBrutaAplicarMM: parseFloat(LB.toFixed(1)),
      porcentagemIrrigacao: parseFloat(porcentagemIrrigacao.toFixed(1)),
      porcentagemPrecipitacao: parseFloat(porcentagemPrecipitacao.toFixed(1))
    },
    parametrosBase: {
      CAD_mm_por_m: cad_mm_por_m,
      fatorDisponibilidade_f: f,
      profundidadeRaiz_Z_cm: Z_cm,
      eficienciaIrrigacao_Ei: Ei,
      ETc_diaria_mm: parseFloat(etcDiaria.toFixed(2))
    }
  };
}

// Função de compatibilidade para manter a interface anterior
function calcularNecessidadeDeIrrigacao(dadosFormulario, dadosClimaticos) {
  const manejo = calcularManejoDeIrrigacao(dadosFormulario, dadosClimaticos);
  
  return {
    necessidadeTotalIrrigacaoMM: manejo.parametrosCalculados.laminaBrutaAplicarMM,
    diagnostico: {
      cultura: dadosFormulario.respostas.etapa_1.valor,
      frequenciaIrrigacao: manejo.parametrosCalculados.frequenciaDias,
      volumePorIrrigacao: manejo.parametrosCalculados.laminaBrutaAplicarMM,
      ETc_diaria_mm: manejo.parametrosBase.ETc_diaria_mm
    },
    mensagem: manejo.recomendacao
  };
}