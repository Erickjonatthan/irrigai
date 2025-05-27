/**
 * Script para funcionalidades da página de acesso
 */

class AcessoManager {
  constructor() {
    this.initializeElements();
    this.bindEvents();
  }

  initializeElements() {
    this.togglePasswordBtn = document.getElementById("togglePassword");
    this.passwordField = document.getElementById("senha");
    this.form = document.querySelector("form");
    this.loadingOverlay = document.getElementById("loadingOverlay");
    this.loadingContainer = document.getElementById("loadingContainer");
    this.loadingText = document.getElementById("loadingText");
    this.loadingSubtext = document.getElementById("loadingSubtext");
    this.submitButton = document.querySelector("button[type='submit']");
  }
  bindEvents() {
    // Event listener para toggle de senha
    if (this.togglePasswordBtn) {
      this.togglePasswordBtn.addEventListener("click", () => {
        this.togglePasswordVisibility();
      });
      
      // Adiciona suporte para navegação por teclado
      this.togglePasswordBtn.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          this.togglePasswordVisibility();
        }
      });
    }

    // Event listener para submissão do formulário
    if (this.form) {
      this.form.addEventListener("submit", (event) => {
        this.handleFormSubmit(event);
      });
    }
  }

  /**
   * Alterna a visibilidade da senha
   */
  togglePasswordVisibility() {
    const isPassword = this.passwordField.type === "password";
    
    this.passwordField.type = isPassword ? "text" : "password";
    
    if (isPassword) {
      this.togglePasswordBtn.classList.remove("eye-open");
      this.togglePasswordBtn.classList.add("eye-closed");
      this.togglePasswordBtn.title = "Ocultar senha";
    } else {
      this.togglePasswordBtn.classList.remove("eye-closed");
      this.togglePasswordBtn.classList.add("eye-open");
      this.togglePasswordBtn.title = "Mostrar senha";
    }
  }

  /**
   * Lida com a submissão do formulário
   * @param {Event} event - Evento de submissão
   */
  async handleFormSubmit(event) {
    event.preventDefault();

    const usuario = document.getElementById("usuario").value;
    const senha = document.getElementById("senha").value;

    // Validações básicas
    if (!usuario.trim() || !senha.trim()) {
      alert("Por favor, preencha todos os campos.");
      return;
    }

    // Mostrar loading
    this.showLoading();

    try {
      const response = await this.submitAuthentication(usuario, senha);
      const data = await response.json();

      if (response.ok) {
        this.showSuccess(data);
      } else {
        this.hideLoading();
        alert(data.error || "Erro ao autenticar");
      }
    } catch (error) {
      this.hideLoading();
      console.error("Erro:", error);
      alert("Erro ao conectar ao servidor");
    }
  }

  /**
   * Envia requisição de autenticação
   * @param {string} usuario - Nome de usuário
   * @param {string} senha - Senha
   * @returns {Promise<Response>} - Promise da resposta
   */
  async submitAuthentication(usuario, senha) {
    return fetch("/autenticar", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ usuario, senha }),
    });
  }

  /**
   * Mostra o overlay de loading
   */
  showLoading() {
    this.loadingOverlay.style.display = "flex";
    this.submitButton.classList.add("loading");
    this.loadingText.textContent = "Autenticando...";
    this.loadingSubtext.textContent = "Recuperando informações da conta.";
  }

  /**
   * Mostra o estado de sucesso e redireciona
   * @param {Object} data - Dados da resposta de sucesso
   */
  showSuccess(data) {
    this.loadingContainer.classList.add("success");
    this.loadingText.textContent = "Login realizado com sucesso!";
    this.loadingSubtext.textContent = "Redirecionando para o painel...";

    // Aguardar 1.5 segundos antes de redirecionar
    setTimeout(() => {
      window.location.href = data.redirect;
    }, 1500);
  }

  /**
   * Esconde o overlay de loading
   */
  hideLoading() {
    this.loadingOverlay.style.display = "none";
    this.submitButton.classList.remove("loading");
    this.loadingContainer.classList.remove("success");
  }
}

// Inicializar quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", () => {
  new AcessoManager();
});
