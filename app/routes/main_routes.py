import json
import os
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from flask import send_from_directory

from app.dto.dtos import ResultadosDTO
from app.process.utils import verificar_token_valido
from app.globals import api_url
main_bp = Blueprint("main", __name__)  # O nome do Blueprint deve ser "main"

@main_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Evitar 404 do favicon em navegadores
@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join('app', 'static', 'img', 'favicon_io'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Rota para a página de acesso
@main_bp.route("/acesso", methods=["GET"])
def acesso():
    # Verifica se o usuário já está autenticado
    if "head" in session:
        # Verifica se já preencheu o formulário inicial
        user_id = session.get("user_id")
        formulario_inicial_path = os.path.join("app/static/data", user_id, "formulario_inicial.json")
        
        if os.path.exists(formulario_inicial_path):
            # Redireciona para o formulário principal se já preencheu o inicial
            return redirect(url_for("main.form"))
        else:
            # Redireciona para o formulário inicial se ainda não preencheu
            return redirect(url_for("main.formulario_inicial"))
    return render_template("acesso.html")

@main_bp.route("/formulario-inicial", methods=["GET"])
def formulario_inicial():
    if "head" not in session:
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso se não estiver autenticado

    head = session["head"]
    user_id = session.get("user_id")

    # Verifica se o token ainda é válido
    if not verificar_token_valido(api_url, head):
        session.pop("head", None)  # Remove o token inválido da sessão
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso

    # Verifica se já preencheu o formulário inicial
    user_folder = os.path.join("app/static/data", user_id)
    formulario_inicial_path = os.path.join(user_folder, "formulario_inicial.json")
    
    if os.path.exists(formulario_inicial_path):
        # Se já preencheu, redireciona para o formulário principal
        return redirect(url_for("main.form"))

    return render_template("formulario-inicial.html")

@main_bp.route("/salvar-formulario-inicial", methods=["POST"])
def salvar_formulario_inicial():
    if "head" not in session:
        return jsonify({"erro": "Usuário não autenticado"}), 401

    try:
        dados = request.get_json()
        user_id = session.get("user_id")
        
        if not user_id:
            return jsonify({"erro": "ID de usuário não encontrado"}), 400

        # Criar pasta do usuário se não existir
        user_folder = os.path.join("app/static/data", user_id)
        os.makedirs(user_folder, exist_ok=True)

        # Salvar o formulário inicial
        formulario_inicial_path = os.path.join(user_folder, "formulario_inicial.json")
        
        dados_completos = {
            **dados,
            "user_id": user_id,
            "timestamp_salvamento": "timestamp_atual"
        }

        with open(formulario_inicial_path, "w", encoding="utf-8") as f:
            json.dump(dados_completos, f, ensure_ascii=False, indent=2)

        return jsonify({
            "sucesso": True,
            "mensagem": "Formulário inicial salvo com sucesso",
            "proximo_passo": "/form"
        })

    except Exception as e:
        print(f"Erro ao salvar formulário inicial: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

@main_bp.route("/form", methods=["GET"])
def form():
    if "head" not in session:
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso se não estiver autenticado

    head = session["head"]
    usuario = session["usuario"]
    user_id = session.get("user_id")

    # Verifica se o token ainda é válido
    if not verificar_token_valido(api_url, head):
        session.pop("head", None)  # Remove o token inválido da sessão
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso

    # Verifica se preencheu o formulário inicial
    user_folder = os.path.join("app/static/data", user_id)
    formulario_inicial_path = os.path.join(user_folder, "formulario_inicial.json")
    
    if not os.path.exists(formulario_inicial_path):
        # Se não preencheu o formulário inicial, redireciona
        return redirect(url_for("main.formulario_inicial"))

    # Caminho correto para o arquivo de resultados
    resultados_path = os.path.join(user_folder, f"{user_id}_resultados.json")

    # Verifica se o arquivo de resultados existe
    if os.path.exists(resultados_path):
        return redirect(url_for("main.app_principal"))  # Redireciona para o app principal

    # Passa o nome do usuário para o template
    return render_template("form.html", usuario=usuario)

@main_bp.route("/app", methods=["GET"])
def app_principal():
    if "head" not in session:
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso se não estiver autenticado

    head = session["head"]
    usuario = session["usuario"]
    user_id = session.get("user_id")

    # Verifica se o token ainda é válido
    if not verificar_token_valido(api_url, head):
        session.pop("head", None)  # Remove o token inválido da sessão
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso

    # Verifica se preencheu o formulário inicial
    user_folder = os.path.join("app/static/data", user_id)
    formulario_inicial_path = os.path.join(user_folder, "formulario_inicial.json")
    
    if not os.path.exists(formulario_inicial_path):
        # Se não preencheu o formulário inicial, redireciona
        return redirect(url_for("main.formulario_inicial"))

    return render_template("app-principal.html", usuario=usuario)

@main_bp.route("/verificar-dados-analise", methods=["GET"])
def verificar_dados_analise():
    if "head" not in session:
        return jsonify({"erro": "Usuário não autenticado"}), 401

    try:
        user_id = session.get("user_id")
        user_folder = os.path.join("app/static/data", user_id)
        resultados_path = os.path.join(user_folder, f"{user_id}_resultados.json")

        tem_dados = os.path.exists(resultados_path)
        
        return jsonify({
            "temDados": tem_dados,
            "ultimaAnalise": "2024-01-01" if tem_dados else None  # Você pode pegar a data real do arquivo
        })

    except Exception as e:
        print(f"Erro ao verificar dados de análise: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

@main_bp.route("/api/dados-analise", methods=["GET"])
def api_dados_analise():
    if "head" not in session:
        return jsonify({"erro": "Usuário não autenticado"}), 401

    try:
        user_id = session.get("user_id")
        user_folder = os.path.join("app/static/data", user_id)
        resultados_path = os.path.join(user_folder, f"{user_id}_resultados.json")

        if not os.path.exists(resultados_path):
            return jsonify({"tem_dados": False}), 404

        with open(resultados_path, "r") as f:
            resultados_data = json.load(f)
            
        # Processar dados para a API
        # Preparar dados do gráfico de precipitação consistentes com o painel
        grafico_precipitacao = resultados_data.get("dados_grafico_precipitacao")
        if not grafico_precipitacao or isinstance(grafico_precipitacao, str):
            # Fallback: construir gráfico simples com anos/valores
            anos_ini = resultados_data.get('ano_inicial', 2020)
            anos_fim = resultados_data.get('ano_final', 2024)
            anos_lista = list(range(anos_ini, anos_fim + 1))
            valores_placeholder = [800, 650, 1200, 900, 450, 1100, 750, 850, 950, 700]
            grafico_precipitacao = {
                "anos": anos_lista,
                "valores": valores_placeholder[:len(anos_lista)],
                "titulo": f"Precipitação Anual - {resultados_data.get('nome_local', 'Local')}"
            }

        dados_resumo = {
            "tem_dados": True,
            "localizacao": {
                "nome_local": resultados_data.get("nome_local", "Local não identificado"),
                "latitude": resultados_data.get("latitude", "N/A"),
                "longitude": resultados_data.get("longitude", "N/A"),
                "area": resultados_data.get("area", "N/A"),
                "periodo": f"{resultados_data.get('ano_inicial', 'N/A')} - {resultados_data.get('ano_final', 'N/A')}"
            },
            "clima": {
                "precipitacao_media": "750 mm",  # Calcular com base nos dados reais
                "indice_aridez": "0.65"  # Extrair dos dados reais
            },
            "data_analise": "Hoje",  # Você pode pegar a data real do arquivo
            "indices": resultados_data.get("indices_e_classificacoes", []),
            "recomendacoes": resultados_data.get("recomendacoes", []),
            "mapa_IA": resultados_data.get("mapa_IA", None),  # Caminho do mapa
            "grafico_precipitacao": grafico_precipitacao
        }
        
        return jsonify(dados_resumo)

    except Exception as e:
        print(f"Erro ao carregar dados da análise: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

@main_bp.route("/api/dados-grafico-precipitacao", methods=["GET"])
def api_dados_grafico_precipitacao():
    if "head" not in session:
        return jsonify({"erro": "Usuário não autenticado"}), 401

    try:
        user_id = session.get("user_id")
        user_folder = os.path.join("app/static/data", user_id)
        resultados_path = os.path.join(user_folder, f"{user_id}_resultados.json")

        if not os.path.exists(resultados_path):
            return jsonify({"erro": "Dados de análise não encontrados"}), 404

        with open(resultados_path, "r") as f:
            resultados_data = json.load(f)
        
        # Extrair dados do gráfico de precipitação
        dados_grafico = resultados_data.get("dados_grafico_precipitacao", {})
        
        if dados_grafico:
            return jsonify({
                "titulo": dados_grafico.get("titulo", "Precipitação Anual"),
                "anos": dados_grafico.get("anos", []),
                "valores": dados_grafico.get("valores", []),
                "unidade": dados_grafico.get("unidade", "mm")
            })
        else:
            return jsonify({"erro": "Dados de gráfico não disponíveis"}), 404

    except Exception as e:
        print(f"Erro ao carregar dados do gráfico: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

@main_bp.route("/painel", methods=["GET"])
def painel():
    if "head" not in session:
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso se não estiver autenticado

    head = session["head"]
    user_id = session.get("user_id")

    # Verifica se o token ainda é válido
    if not verificar_token_valido(api_url, head):
        session.pop("head", None)  # Remove o token inválido da sessão
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso

    # Caminho para os resultados salvos
    user_folder = os.path.join("app/static/data", user_id)
    resultados_path = os.path.join(user_folder, f"{user_id}_resultados.json")    
    
    # Tenta carregar os resultados do disco
    if os.path.exists(resultados_path):
        try:
            with open(resultados_path, "r") as f:
                resultados_data = json.load(f)
                  # Mapear campos antigos para os novos se necessário (compatibilidade retroativa)
                campos_mapeamento = {
                    'grafico_precipitacao': 'dados_grafico_precipitacao',
                    'grafico_precipitacao_vs_evaporacao': 'dados_grafico_precipitacao_vs_evaporacao',
                    'grafico_balanco_hidrico': 'dados_grafico_balanco_hidrico',
                    'grafico_rai': 'dados_grafico_rai',
                    'grafico_aridez': 'dados_grafico_aridez'
                }
                
                # Atualizar os nomes dos campos se necessário
                for campo_antigo, campo_novo in campos_mapeamento.items():
                    if campo_antigo in resultados_data and campo_novo not in resultados_data:
                        valor = resultados_data.pop(campo_antigo)
                        # Se o valor é uma string (caminho de arquivo), substitui por None para indicar dados indisponíveis
                        if isinstance(valor, str):
                            print(f"Convertendo campo {campo_antigo} de caminho de arquivo para dados estruturados (será substituído por dados de exemplo)")
                            resultados_data[campo_novo] = None  # Será tratado no frontend
                        else:
                            resultados_data[campo_novo] = valor
                
                resultados = ResultadosDTO(**resultados_data)  # Reconstrói o DTO a partir do JSON
        except Exception as e:
            print(f"Erro ao carregar resultados do disco: {e}")
            return render_template("error.html", mensagem="Erro ao carregar os resultados.")
    else:
        # Se não há resultados, redireciona para o app principal
        return redirect(url_for("main.app_principal"))

    # Passa os resultados para o template
    return render_template("painel.html", resultados=resultados)

@main_bp.route("/api/dados-formulario-inicial", methods=["GET"])
def api_dados_formulario_inicial():
    if "head" not in session:
        return jsonify({"erro": "Usuário não autenticado"}), 401

    try:
        user_id = session.get("user_id")
        user_folder = os.path.join("app/static/data", user_id)
        formulario_inicial_path = os.path.join(user_folder, "formulario_inicial.json")

        if not os.path.exists(formulario_inicial_path):
            return jsonify({"tem_dados": False}), 404

        with open(formulario_inicial_path, "r", encoding="utf-8") as f:
            dados_formulario = json.load(f)
            
        # Extrair dados das respostas do formulário inicial
        respostas = dados_formulario.get("respostas", {})
        
        # Retornar os dados no formato esperado pelo IrrigacaoManager
        dados_formatados = {
            "tem_dados": True,
            "respostas": {
                "etapa_1": {
                    "valor": respostas.get("etapa_1", {}).get("valor", ""),
                    "texto": respostas.get("etapa_1", {}).get("texto", "")
                },
                "etapa_3": {
                    "valor": respostas.get("etapa_3", {}).get("valor", "")
                },
                "etapa_5": {
                    "valor": respostas.get("etapa_5", {}).get("valor", "")
                }
            },
            "coordenadas": {
                "latitude": respostas.get("etapa_6", {}).get("texto_adicional", ""),
                "longitude": respostas.get("etapa_7", {}).get("texto_adicional", "")
            }
        }
        
        return jsonify(dados_formatados)

    except Exception as e:
        print(f"Erro ao carregar dados do formulário inicial: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

@main_bp.route("/api/dados-climaticos", methods=["GET"])
def api_dados_climaticos():
    """Retorna os dados climáticos para cálculo de irrigação"""
    if "head" not in session:
        return jsonify({"erro": "Usuário não autenticado"}), 401

    try:
        user_id = session.get("user_id")
        user_folder = os.path.join("app/static/data", user_id)
        resultados_path = os.path.join(user_folder, f"{user_id}_resultados.json")
        
        if not os.path.exists(resultados_path):
            return jsonify({"erro": "Dados climáticos não encontrados"}), 404
        
        # Carrega os dados de resultados
        with open(resultados_path, "r", encoding="utf-8") as f:
            dados_resultados = json.load(f)
        
        # Extrai os dados climáticos necessários
        dados_climaticos = {
            "dados_grafico_balanco_hidrico": dados_resultados.get("dados_grafico_balanco_hidrico", {}),
            "dados_grafico_precipitacao": dados_resultados.get("dados_grafico_precipitacao", {})
        }
        
        return jsonify(dados_climaticos)
        
    except Exception as e:
        print(f"Erro ao obter dados climáticos: {e}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

@main_bp.route("/logout", methods=["GET"])
def logout():
    # Limpar a sessão
    session.clear()
    return redirect(url_for("main.index"))
