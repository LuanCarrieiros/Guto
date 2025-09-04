/**
 * GUTO - Sistema de Navegação Inteligente
 * Gerencia os botões "Voltar" para seguir o fluxo real do usuário
 * 
 * @author Equipe GUTO
 * @version 1.0
 * @since 2025-01-03
 */

class GutoNavigation {
    constructor() {
        this.historyStack = [];
        this.maxHistorySize = 10;
        this.init();
    }

    init() {
        // Carrega histórico do sessionStorage
        this.loadHistory();
        
        // Adiciona página atual ao histórico
        this.addToHistory(window.location.href, document.title);
        
        // Configura todos os botões voltar
        this.setupBackButtons();
        
        // Monitora mudanças de página
        this.monitorPageChanges();
    }

    loadHistory() {
        try {
            const savedHistory = sessionStorage.getItem('guto_navigation_history');
            if (savedHistory) {
                this.historyStack = JSON.parse(savedHistory);
            }
        } catch (e) {
            console.warn('Erro ao carregar histórico de navegação:', e);
            this.historyStack = [];
        }
    }

    saveHistory() {
        try {
            sessionStorage.setItem('guto_navigation_history', JSON.stringify(this.historyStack));
        } catch (e) {
            console.warn('Erro ao salvar histórico de navegação:', e);
        }
    }

    addToHistory(url, title) {
        // Remove a página atual se ela já existir no histórico
        this.historyStack = this.historyStack.filter(item => item.url !== url);
        
        // Adiciona no topo
        this.historyStack.unshift({
            url: url,
            title: title || document.title,
            timestamp: Date.now()
        });
        
        // Mantém apenas o tamanho máximo
        if (this.historyStack.length > this.maxHistorySize) {
            this.historyStack = this.historyStack.slice(0, this.maxHistorySize);
        }
        
        this.saveHistory();
    }

    getPreviousPage() {
        // Retorna a página anterior (índice 1, já que 0 é a atual)
        if (this.historyStack.length > 1) {
            return this.historyStack[1];
        }
        
        // Se não tem histórico, tenta usar o referer
        if (document.referrer && document.referrer !== window.location.href) {
            return {
                url: document.referrer,
                title: 'Página Anterior',
                timestamp: Date.now()
            };
        }
        
        // Fallback para o dashboard
        return {
            url: '/',
            title: 'Dashboard',
            timestamp: Date.now()
        };
    }

    goBack() {
        const previousPage = this.getPreviousPage();
        
        if (previousPage) {
            // Remove a página atual antes de navegar
            this.historyStack.shift();
            this.saveHistory();
            
            // Navega para a página anterior
            window.location.href = previousPage.url;
        } else {
            // Se não tem para onde voltar, vai para o dashboard
            window.location.href = '/';
        }
    }

    setupBackButtons() {
        // Configura todos os botões de voltar existentes
        const backButtons = document.querySelectorAll('.btn-voltar, [data-action="voltar"], .back-button');
        
        backButtons.forEach(button => {
            // Remove listeners antigos
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            // Adiciona novo listener
            newButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.goBack();
            });
            
            // Atualiza o texto/título se necessário
            const previousPage = this.getPreviousPage();
            if (previousPage && newButton.hasAttribute('data-show-title')) {
                newButton.textContent = `← Voltar para ${previousPage.title}`;
            }
        });
    }

    monitorPageChanges() {
        // Monitora cliques em links para atualizar o histórico
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (link && link.href && !link.href.startsWith('javascript:')) {
                // Adiciona a página atual ao histórico antes de navegar
                setTimeout(() => {
                    this.addToHistory(window.location.href, document.title);
                }, 100);
            }
        });

        // Monitora mudanças no histórico do browser
        window.addEventListener('popstate', () => {
            this.addToHistory(window.location.href, document.title);
            this.setupBackButtons();
        });
    }

    // Método para limpar histórico (útil para logout)
    clearHistory() {
        this.historyStack = [];
        sessionStorage.removeItem('guto_navigation_history');
    }

    // Método para debug
    getHistory() {
        return this.historyStack;
    }
}

// Inicializa quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gutoNav === 'undefined') {
        window.gutoNav = new GutoNavigation();
    }
});

// Também inicializa se a página já carregou
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof window.gutoNav === 'undefined') {
            window.gutoNav = new GutoNavigation();
        }
    });
} else {
    if (typeof window.gutoNav === 'undefined') {
        window.gutoNav = new GutoNavigation();
    }
}