// Font Loader - Garante que as páginas só carreguem após as fontes estarem prontas
(function() {
    'use strict';

    // CSS para ocultar o conteúdo inicialmente
    const hideContentCSS = `
        .font-loading {
            visibility: hidden !important;
        }
        .font-loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #f8f6ef 0%, #f0ede3 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }
        .font-loading-spinner {
            text-align: center;
            color: #666;
            animation: font-loading-fade-in 0.3s ease-in-out;
        }
        .font-loading-spinner::before {
            content: '';
            display: block;
            width: 40px;
            height: 40px;
            margin: 0 auto 16px;
            border: 3px solid #e0e0e0;
            border-top: 3px solid #4fc3f7;
            border-radius: 50%;
            animation: font-loading-spin 1s linear infinite;
        }
        @keyframes font-loading-spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes font-loading-fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes font-loading-fade-out {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        .font-loading-overlay.fade-out {
            animation: font-loading-fade-out 0.3s ease-in-out forwards;
        }
    `;    // Adiciona o CSS ao head
    const style = document.createElement('style');
    style.textContent = hideContentCSS;
    document.head.appendChild(style);

    // Adiciona classe de loading ao html
    document.documentElement.classList.add('font-loading');

    let overlay;

    function createOverlay() {
        // Cria overlay de loading apenas quando o body existir
        if (document.body) {
            overlay = document.createElement('div');
            overlay.className = 'font-loading-overlay';
            overlay.innerHTML = '<div class="font-loading-spinner">Carregando fontes...</div>';
            document.body.appendChild(overlay);
        }
    }    function showContent() {
        // Adiciona animação de fade out apenas se o overlay existir
        if (overlay) {
            overlay.classList.add('fade-out');
        }
        
        setTimeout(() => {
            document.documentElement.classList.remove('font-loading');
            document.documentElement.classList.add('fonts-loaded');
            
            if (overlay && overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
            
            // Remove a classe fonts-loaded após a transição
            setTimeout(() => {
                document.documentElement.classList.remove('fonts-loaded');
            }, 300);
            
            // Dispara evento customizado para outros scripts
            const event = new CustomEvent('fontsLoaded');
            document.dispatchEvent(event);
            
        }, overlay ? 300 : 0);
    }    function loadFonts() {
        // Cria o overlay primeiro
        createOverlay();
        
        // Se Font Loading API estiver disponível
        if ('fonts' in document) {
            // Lista das fontes Raleway que precisamos
            const fontPromises = [
                document.fonts.load('400 16px Raleway'),
                document.fonts.load('500 16px Raleway'),
                document.fonts.load('600 16px Raleway'),
                document.fonts.load('700 16px Raleway')
            ];

            Promise.all(fontPromises)
                .then(() => {
                    showContent();
                })
                .catch((error) => {
                    console.warn('⚠ Erro ao carregar fontes, mostrando conteúdo...', error);
                    showContent();
                });

            // Fallback: se demorar mais que 3 segundos, mostra o conteúdo
            setTimeout(() => {
                if (document.documentElement.classList.contains('font-loading')) {
                    console.warn('⚠ Timeout no carregamento de fontes (3s)');
                    showContent();
                }
            }, 3000);
        } else {
            setTimeout(() => {
                showContent();
            }, 1500);
        }
    }    // Inicia o carregamento das fontes quando o DOM estiver pronto
    function initializeFontLoader() {
        // Garante que o documento e body estejam disponíveis
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                // Aguarda um frame para garantir que o body esteja presente
                requestAnimationFrame(loadFonts);
            });
        } else {
            // Se o DOM já está carregado, executa no próximo frame
            requestAnimationFrame(loadFonts);
        }
    }

    // Inicia o processo
    initializeFontLoader();
})();
