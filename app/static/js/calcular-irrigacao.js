// Realiza o calculo da irrigacao com base nas informacoes vinda do formulário e com os dados de ET e Precipitação. Deve retornar quanto de irrigação deve ser feita por dia. 
/**
 * Calcula a necessidade de irrigação para uma cultura com base nas respostas de um formulário e em dados climáticos históricos.
 * A metodologia segue os princípios do balanço hídrico da cultura, conforme detalhado na 'Circular Técnica 136' da Embrapa.
 *
 * @param {object} dadosFormulario - O objeto JSON contendo as respostas do formulário do agricultor.
 * @param {object} dadosClimaticos - O objeto JSON com os dados históricos anuais de clima (precipitação, ET, PET).
 * @returns {object} Um objeto contendo a necessidade total de irrigação em milímetros (mm) e uma mensagem explicativa.
 */
function calcularNecessidadeDeIrrigacao(dadosFormulario, dadosClimaticos) {

  // --- ETAPA 1: Extrair e interpretar os parâmetros do formulário ---

  const respostas = dadosFormulario.respostas;

  // Mapeamento de valores do formulário para parâmetros de cálculo.
  const cultura = respostas.etapa_1.valor; // Ex: "feijao"
  const tipoSolo = respostas.etapa_5.valor; // Ex: "arenoso"
  
  // Extrai a duração média do ciclo em dias (ex: "100_150" -> 125)
  const [cicloMin, cicloMax] = respostas.etapa_3.valor.split('_').map(Number);
  const duracaoCicloDias = (cicloMin + cicloMax) / 2;

  // --- ETAPA 2: Definir constantes agronômicas com base na 'Circular Técnica 136' ---

  // Coeficiente de Cultura (Kc) médio para a fase principal do ciclo.
  // Valores baseados na Tabela 8 da circular (Kc-mid).
  const KC_POR_CULTURA = {
    'Feijão': 1.10, // Média de 1.05-1.15
    'Milho': 1.20,
    'Soja': 1.15,
    'Algodão': 1.18, // Média de 1.15-1.20
    'Girassol': 1.08 // Média de 1.00-1.15
    // Outras culturas podem ser adicionadas aqui.
  };
  const kc = KC_POR_CULTURA[cultura] || 1.0; // Usa 1.0 como padrão se a cultura não for encontrada.

  // --- ETAPA 3: Processar os dados climáticos para obter médias diárias ---

  // Função auxiliar para calcular a média de um array de números.
  const calcularMedia = (arr) => {
    if (!arr || arr.length === 0) return 0;
    const soma = arr.reduce((acc, val) => acc + val, 0);
    return soma / arr.length;
  };

  // A Evapotranspiração de Referência (ETo) corresponde à PET (Evapotranspiração Potencial) nos dados.
  // Verificar se os dados estão disponíveis na estrutura esperada
  let mediaAnualETo = 0;
  let mediaAnualPrec = 0;
  
  if (dadosClimaticos && dadosClimaticos.dados_grafico_balanco_hidrico && 
      dadosClimaticos.dados_grafico_balanco_hidrico.dados && 
      dadosClimaticos.dados_grafico_balanco_hidrico.dados.series && 
      dadosClimaticos.dados_grafico_balanco_hidrico.dados.series.length > 1) {
    mediaAnualETo = calcularMedia(dadosClimaticos.dados_grafico_balanco_hidrico.dados.series[1].valores);
  }
  
  if (dadosClimaticos && dadosClimaticos.dados_grafico_precipitacao && 
      dadosClimaticos.dados_grafico_precipitacao.dados && 
      dadosClimaticos.dados_grafico_precipitacao.dados.series && 
      dadosClimaticos.dados_grafico_precipitacao.dados.series.length > 0) {
    mediaAnualPrec = calcularMedia(dadosClimaticos.dados_grafico_precipitacao.dados.series[0].valores);
  }

  // Converte as médias anuais para médias diárias.
  const mediaDiariaETo = mediaAnualETo / 365;
  const mediaDiariaPrec = mediaAnualPrec / 365;

  // --- ETAPA 4: Realizar o cálculo do Balanço Hídrico ---

  // a. Calcular a necessidade total de água da cultura (Evapotranspiração da Cultura - ETc) para o ciclo.
  // ETc = ETo * Kc
  const etcDiaria = mediaDiariaETo * kc;
  const etcTotalCiclo = etcDiaria * duracaoCicloDias;

  // b. Calcular a precipitação total esperada durante o ciclo.
  const precTotalCiclo = mediaDiariaPrec * duracaoCicloDias;

  // c. Calcular o déficit hídrico, que é a Necessidade de Irrigação (Lâmina Líquida).
  // Se a chuva for maior que a necessidade da planta, a irrigação necessária é zero.
  let necessidadeIrrigacaoLiquida = etcTotalCiclo - precTotalCiclo;
  if (necessidadeIrrigacaoLiquida < 0) {
    necessidadeIrrigacaoLiquida = 0;
  }

  // --- ETAPA 5: Calcular frequência e volume de irrigação ---
  
  // Definir frequência de irrigação com base no tipo de solo
  const FREQUENCIA_POR_SOLO = {
    'arenoso': 2, // A cada 2 dias para solos arenosos (drenagem rápida)
    'argiloso': 5, // A cada 5 dias para solos argilosos (retenção alta)
    'medio': 3 // A cada 3 dias para solos médios (loam)
  };
  
  const frequenciaIrrigacao = FREQUENCIA_POR_SOLO[tipoSolo] || 3; // Padrão: a cada 3 dias
  
  // Calcular número total de irrigações durante o ciclo
  const numeroIrrigacoes = Math.ceil(duracaoCicloDias / frequenciaIrrigacao);
  
  // Calcular volume de água por irrigação (em mm)
  let volumePorIrrigacao = 0;
  if (numeroIrrigacoes > 0 && necessidadeIrrigacaoLiquida > 0) {
    volumePorIrrigacao = necessidadeIrrigacaoLiquida / numeroIrrigacoes;
  }
  
  // Calcular porcentagem de irrigação necessária em relação à necessidade total de água
  const porcentagemIrrigacao = (necessidadeIrrigacaoLiquida / etcTotalCiclo) * 100;
  const porcentagemPrecipitacao = (precTotalCiclo / etcTotalCiclo) * 100;
  
  // --- ETAPA 6: Retornar o resultado final ---

  return {
    necessidadeTotalIrrigacaoMM: parseFloat(necessidadeIrrigacaoLiquida.toFixed(2)),
    diagnostico: {
      cultura: cultura,
      duracaoCicloDias: duracaoCicloDias,
      necessidadeAguaTotalMM: parseFloat(etcTotalCiclo.toFixed(2)),
      precipitacaoEsperadaMM: parseFloat(precTotalCiclo.toFixed(2)),
      kcUtilizado: kc,
      frequenciaIrrigacao: frequenciaIrrigacao,
      volumePorIrrigacao: parseFloat(volumePorIrrigacao.toFixed(2)),
      numeroIrrigacoes: numeroIrrigacoes,
      porcentagemIrrigacao: parseFloat(porcentagemIrrigacao.toFixed(2)),
      porcentagemPrecipitacao: parseFloat(porcentagemPrecipitacao.toFixed(2))
    },
    mensagem: `Para a cultura de ${respostas.etapa_1.texto}, com um ciclo de ${duracaoCicloDias} dias, a necessidade total de água (ETc) é de aproximadamente ${etcTotalCiclo.toFixed(2)} mm. Com uma precipitação esperada de ${precTotalCiclo.toFixed(2)} mm no mesmo período, a necessidade de irrigação suplementar (lâmina líquida) é de ${necessidadeIrrigacaoLiquida.toFixed(2)} mm.`
  };
}