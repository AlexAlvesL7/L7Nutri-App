/**
 * 🛡️ API HANDLER ROBUSTO - L7NUTRI
 * Previne e detecta erros de API com tratamento completo
 * Data: 22/07/2025
 */

class ApiHandler {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    /**
     * 🎯 Método principal para requisições API com tratamento robusto
     */
    async request(endpoint, options = {}) {
        const url = this.baseUrl + endpoint;
        
        // Configurações padrão
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        console.log(`🚀 API Request: ${config.method} ${url}`);
        
        try {
            const response = await fetch(url, config);
            
            // 🔍 VERIFICAÇÃO 1: Status HTTP
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`❌ HTTP Error ${response.status}:`, errorText);
                
                // Detecta se retornou HTML em vez de JSON
                if (errorText.includes('<!DOCTYPE') || errorText.includes('<html')) {
                    console.error('🚨 ERRO CRÍTICO: Servidor retornou HTML em vez de JSON!');
                    console.error('💡 Possíveis causas: Erro 500, 502, ou problema de inicialização');
                    throw new Error(`Erro do servidor (${response.status}): Sistema pode estar com problemas de banco de dados ou modelos`);
                }
                
                throw new Error(`Erro HTTP ${response.status}: ${errorText}`);
            }

            // 🔍 VERIFICAÇÃO 2: Content-Type
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const responseText = await response.text();
                console.error('🚨 ERRO: Esperado JSON mas recebeu:', contentType);
                console.error('📄 Conteúdo recebido:', responseText.substring(0, 200) + '...');
                
                // Se recebeu HTML, é erro crítico
                if (responseText.includes('<!DOCTYPE') || responseText.includes('<html')) {
                    console.error('💥 ERRO CRÍTICO: Página HTML retornada em resposta JSON!');
                    throw new Error('Erro crítico do servidor: Sistema retornou página de erro em vez de dados JSON');
                }
                
                throw new Error(`Resposta inválida: esperado JSON, recebido ${contentType}`);
            }

            // ✅ SUCESSO: Parse JSON
            const data = await response.json();
            console.log(`✅ API Success: ${config.method} ${url}`, data);
            return data;

        } catch (error) {
            console.error(`💥 API Error: ${config.method} ${url}`, error);
            
            // 🔍 DIAGNÓSTICO AVANÇADO
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                console.error('🌐 ERRO DE REDE: Servidor pode estar offline ou com problemas de conectividade');
                throw new Error('Erro de conectividade: Verifique sua internet ou se o servidor está online');
            }
            
            if (error.message.includes('SyntaxError') && error.message.includes('JSON')) {
                console.error('📝 ERRO DE PARSING JSON: Resposta do servidor não é JSON válido');
                throw new Error('Erro de dados: Servidor retornou dados corrompidos');
            }
            
            throw error;
        }
    }

    /**
     * 🎯 Métodos específicos para operações comuns
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// 🎯 INSTÂNCIA GLOBAL
const api = new ApiHandler();

/**
 * 🛡️ FUNÇÃO ESPECÍFICA PARA CADASTRO COM DIAGNÓSTICO AVANÇADO
 */
async function cadastrarUsuarioSeguro(dadosUsuario) {
    try {
        console.log('📝 Iniciando cadastro seguro...', dadosUsuario);
        
        // Validação prévia dos dados
        if (!dadosUsuario.nome || !dadosUsuario.email || !dadosUsuario.username || !dadosUsuario.password) {
            throw new Error('Dados obrigatórios não fornecidos: nome, email, username, password');
        }
        
        const resultado = await api.post('/api/cadastro', dadosUsuario);
        
        console.log('✅ Cadastro realizado com sucesso!', resultado);
        return resultado;
        
    } catch (error) {
        console.error('💥 Erro no cadastro:', error);
        
        // 🎯 DIAGNÓSTICO ESPECÍFICO PARA PROBLEMAS COMUNS
        if (error.message.includes('500')) {
            console.error('🔍 DIAGNÓSTICO: Erro 500 pode indicar:');
            console.error('   1. Problema de banco de dados (coluna inexistente)');
            console.error('   2. Erro nos modelos SQLAlchemy');
            console.error('   3. Problema de relacionamentos (Foreign Key)');
            console.error('💡 Sugestão: Verificar logs do servidor para detalhes específicos');
        }
        
        if (error.message.includes('400')) {
            console.error('🔍 DIAGNÓSTICO: Erro 400 pode indicar:');
            console.error('   1. Dados obrigatórios faltando');
            console.error('   2. Formato de dados incorreto');
            console.error('   3. Validação falhou no backend');
        }
        
        throw error;
    }
}

/**
 * 🧪 FUNÇÃO DE TESTE DE CONECTIVIDADE
 */
async function testarConectividadeAPI() {
    try {
        console.log('🧪 Testando conectividade da API...');
        
        // Teste básico
        const resultado = await api.get('/api/teste');
        console.log('✅ API básica funcionando:', resultado);
        
        // Teste de diagnóstico (se disponível)
        try {
            const diagnostico = await api.get('/api/teste-tabelas');
            console.log('✅ Diagnóstico de tabelas:', diagnostico);
        } catch (diagError) {
            console.warn('⚠️ Endpoint de diagnóstico indisponível:', diagError.message);
        }
        
        return true;
        
    } catch (error) {
        console.error('❌ Falha na conectividade:', error);
        return false;
    }
}

// 🎯 EXPORTAR PARA USO GLOBAL
window.ApiHandler = ApiHandler;
window.api = api;
window.cadastrarUsuarioSeguro = cadastrarUsuarioSeguro;
window.testarConectividadeAPI = testarConectividadeAPI;
