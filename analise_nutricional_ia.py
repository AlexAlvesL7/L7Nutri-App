"""
Sistema de Análise Nutricional Inteligente L7Nutri
Classe modular com prompts específicos para cada etapa
"""

import json
from datetime import datetime
import google.generativeai as genai
import os

class AnaliseNutricionalIA:
    
    def __init__(self, dados_usuario, modelo_ia=None):
        """
        Inicializa o sistema de análise nutricional
        
        Args:
            dados_usuario (dict): Dados completos do usuário
            modelo_ia: Instância do modelo Google Gemini
        """
        self.dados = dados_usuario
        self.modelo_ia = modelo_ia
        
        # Preparar dados básicos
        self.nome = dados_usuario.get('nome', 'Usuário')
        self.idade = dados_usuario.get('idade', 25)
        self.peso = dados_usuario.get('peso', 70)
        self.altura = dados_usuario.get('altura', 170)
        self.sexo = dados_usuario.get('sexo', 'masculino')
        self.objetivo = dados_usuario.get('objetivo', 'manter peso')
        self.fator_atividade = dados_usuario.get('fator_atividade', 1.4)
        
        # Dados do questionário
        self.estilo_alimentar = dados_usuario.get('estilo_alimentar', 'tradicional')
        self.experiencia_suplementos = dados_usuario.get('experiencia_suplementos', 'iniciante')
        self.tempo_treino_meses = dados_usuario.get('tempo_treino_meses', 0)
        self.ja_usou_termogenico = dados_usuario.get('ja_usou_termogenico', False)
        self.restricoes = dados_usuario.get('restricoes_alimentares', [])
        self.preferencias = dados_usuario.get('preferencias_alimentares', [])
        self.horario_treino = dados_usuario.get('horario_treino', 'manha')
        self.disponibilidade_cozinhar = dados_usuario.get('disponibilidade_cozinhar', 'media')
        
        # Calcular métricas
        self.imc = self._calcular_imc()
        self.tmb = self._calcular_tmb()
        self.calorias_objetivo = self._calcular_calorias_objetivo()

    def gerar_plano(self):
        """
        Gera plano nutricional personalizado com IA
        """
        prompt = f"""
        PROMPT: PLANO NUTRICIONAL PERSONALIZADO L7NUTRI

        Com base nos dados: {self.sexo}, {self.idade} anos, {self.peso}kg, {self.altura}cm, 
        objetivo "{self.objetivo}", rotina de atividade física (fator {self.fator_atividade}), 
        preferências "{self.estilo_alimentar}" e restrições {self.restricoes}, 
        gere um plano nutricional personalizado detalhado.

        DADOS CALCULADOS:
        - IMC: {self.imc:.1f}
        - TMB: {self.tmb:.0f} kcal
        - Meta calórica: {self.calorias_objetivo:.0f} kcal

        FORNEÇA:
        1. Calorias diárias: [valor específico] kcal
        2. Proteínas: [valor específico] g (1.6-2.2g/kg peso)
        3. Carboidratos: [valor específico] g (45-65% calorias)
        4. Gorduras: [valor específico] g (20-35% calorias)
        5. Fibras: [valor específico] g (25-35g/dia)
        6. Água: [valor específico] L (35ml/kg peso)

        DIVISÃO DAS REFEIÇÕES com horários:
        - Café da manhã (07:00): [3 alimentos específicos]
        - Lanche manhã (10:00): [2 alimentos específicos]
        - Almoço (12:30): [3 alimentos específicos]
        - Lanche tarde (15:30): [2 alimentos específicos]
        - Jantar (19:00): [3 alimentos específicos]
        - Ceia (21:30): [1 alimento específico]

        SEJA ESPECÍFICO E PRÁTICO. Use alimentos comuns do Brasil.
        """
        
        try:
            if self.modelo_ia:
                resposta = self.modelo_ia.generate_content(prompt)
                return self._processar_plano_nutricional(resposta.text)
            else:
                return self._gerar_plano_fallback()
        except Exception as e:
            print(f"Erro ao gerar plano: {str(e)}")
            return self._gerar_plano_fallback()

    def recomendar_treino(self):
        """
        Sugere treino personalizado com IA
        """
        prompt = f"""
        PROMPT: TREINO PERSONALIZADO L7PERSONAL

        Sugira um treino simples e eficaz, compatível com o perfil:
        - Usuário: {self.nome}, {self.idade} anos, {self.sexo}
        - Objetivo: {self.objetivo}
        - Experiência: {self.tempo_treino_meses} meses de treino
        - Horário preferido: {self.horario_treino}
        - Atividade atual: nível {self.fator_atividade}

        CRITÉRIOS:
        - Treino para casa, máximo 30-45 minutos
        - Equipamentos básicos ou peso corporal
        - 3-5 exercícios principais
        - Frequência semanal adequada

        FORNEÇA:
        1. Tipo de treino: [nome específico]
        2. Duração: [tempo em minutos]
        3. Frequência: [vezes por semana]
        4. Exercícios principais: [lista de 3-5 exercícios]
        5. Observações importantes

        SEJA MOTIVADOR E REALISTA para o nível do usuário.
        """
        
        try:
            if self.modelo_ia:
                resposta = self.modelo_ia.generate_content(prompt)
                treino_texto = resposta.text
            else:
                treino_texto = self._gerar_treino_fallback()
            
            return {
                'tipo': self._extrair_valor(treino_texto, 'Tipo de treino:', 'Treino Funcional'),
                'duracao': self._extrair_valor(treino_texto, 'Duração:', '30-45 minutos'),
                'frequencia': self._extrair_valor(treino_texto, 'Frequência:', '3x por semana'),
                'exercicios': self._extrair_exercicios(treino_texto),
                'observacoes': self._extrair_valor(treino_texto, 'Observações:', 'Mantenha regularidade'),
                'link': f'https://l7personal.com/treinos/{self.objetivo.lower().replace(" ", "-")}',
                'texto_completo': treino_texto
            }
            
        except Exception as e:
            print(f"Erro ao gerar treino: {str(e)}")
            return self._gerar_treino_fallback_dict()

    def recomendar_receita(self):
        """
        Sugere receita personalizada com IA
        """
        restricoes_texto = ', '.join(self.restricoes) if self.restricoes else 'nenhuma'
        
        prompt = f"""
        PROMPT: RECEITA PERSONALIZADA L7CHEF

        Sugira uma receita saudável, prática e saborosa:
        - Objetivo: {self.objetivo}
        - Estilo alimentar: {self.estilo_alimentar}
        - Restrições: {restricoes_texto}
        - Disponibilidade para cozinhar: {self.disponibilidade_cozinhar}
        - Calorias meta: {self.calorias_objetivo:.0f} kcal/dia

        CRITÉRIOS:
        - Receita para 1 pessoa
        - Tempo de preparo: máximo 30 minutos
        - Ingredientes acessíveis no Brasil
        - Rica em nutrientes para o objetivo
        - Saborosa e prática

        FORNEÇA:
        1. Nome da receita: [nome específico e atrativo]
        2. Tempo de preparo: [minutos]
        3. Ingredientes: [lista completa]
        4. Modo de preparo: [passo a passo]
        5. Informações nutricionais: [calorias, proteínas, carboidratos]
        6. Dica extra: [sugestão de acompanhamento ou variação]

        SEJA CRIATIVO e adequado ao objetivo nutricional.
        """
        
        try:
            if self.modelo_ia:
                resposta = self.modelo_ia.generate_content(prompt)
                receita_texto = resposta.text
            else:
                receita_texto = self._gerar_receita_fallback()
            
            nome_receita = self._extrair_valor(receita_texto, 'Nome da receita:', 'Receita Saudável Personalizada')
            slug_receita = nome_receita.lower().replace(' ', '-').replace(',', '').replace(':', '')
            
            return {
                'nome': nome_receita,
                'tempo_preparo': self._extrair_valor(receita_texto, 'Tempo de preparo:', '20-30 minutos'),
                'ingredientes': self._extrair_lista(receita_texto, 'Ingredientes:'),
                'modo_preparo': self._extrair_lista(receita_texto, 'Modo de preparo:'),
                'calorias_porcao': self._extrair_numero(receita_texto, 'calorias', 350),
                'dica_extra': self._extrair_valor(receita_texto, 'Dica extra:', 'Varie os temperos!'),
                'link': f'https://l7chef.com/receitas/{slug_receita}',
                'categoria': self._classificar_receita_categoria(),
                'texto_completo': receita_texto
            }
            
        except Exception as e:
            print(f"Erro ao gerar receita: {str(e)}")
            return self._gerar_receita_fallback_dict()

    def recomendar_suplemento(self):
        """
        Recomenda suplemento L7 com explicação detalhada
        """
        prompt = f"""
        PROMPT: SUPLEMENTO L7 PERSONALIZADO

        Analise o estágio do usuário e recomende um suplemento L7:
        - Nome: {self.nome}
        - Experiência com suplementos: {self.experiencia_suplementos}
        - Já usou termogênico: {self.ja_usou_termogenico}
        - Tempo de treino: {self.tempo_treino_meses} meses
        - Objetivo: {self.objetivo}
        - Horário de treino: {self.horario_treino}

        PRODUTOS L7 DISPONÍVEIS:
        1. L7ULTRA - Para INICIANTES
           - Primeiro suplemento termogênico
           - Foco em energia e disposição
           - Fórmula suave e eficaz
           
        2. L7TURBO - Para INTERMEDIÁRIOS  
           - Já têm experiência com suplementos
           - Foco em performance e queima
           - Fórmula potencializada
           
        3. L7NITRO - Para AVANÇADOS
           - Experientes em termogênicos
           - Foco em resultados máximos
           - Fórmula de alta potência

        ESCOLHA O PRODUTO IDEAL e forneça:
        1. Produto recomendado: [L7Ultra, L7Turbo ou L7Nitro]
        2. Justificativa: [Por que é ideal para este perfil - 2-3 frases]
        3. Como usar: [Dosagem específica e horários]
        4. Benefícios esperados: [3 benefícios principais]
        5. Orientações importantes: [cuidados e dicas]

        SEJA EDUCATIVO e não pressione venda. Explique o VALOR do produto.
        """
        
        try:
            if self.modelo_ia:
                resposta = self.modelo_ia.generate_content(prompt)
                suplemento_texto = resposta.text
            else:
                suplemento_texto = self._gerar_suplemento_fallback()
            
            produto = self._extrair_produto_l7(suplemento_texto)
            
            return {
                'produto': produto,
                'justificativa': self._extrair_valor(suplemento_texto, 'Justificativa:', f'{produto} é ideal para seu perfil'),
                'como_usar': self._extrair_valor(suplemento_texto, 'Como usar:', '1 dose 30 minutos antes do treino'),
                'beneficios': self._extrair_lista(suplemento_texto, 'Benefícios esperados:'),
                'orientacoes': self._extrair_valor(suplemento_texto, 'Orientações importantes:', 'Respeite a dosagem recomendada'),
                'link': f'https://l7shop.com/{produto.lower()}',
                'preco_promocional': self._gerar_promocao(),
                'cta_consultivo': 'Para potencializar seus resultados, veja como nosso suplemento pode ajudar. Clique e saiba mais!',
                'texto_completo': suplemento_texto
            }
            
        except Exception as e:
            print(f"Erro ao gerar suplemento: {str(e)}")
            return self._gerar_suplemento_fallback_dict()

    def mensagem_motivacional(self):
        """
        Gera mensagem motivacional personalizada
        """
        prompt = f"""
        PROMPT: MENSAGEM MOTIVACIONAL L7NUTRI

        Escreva uma mensagem curta e motivacional para:
        - Nome: {self.nome}
        - Objetivo: {self.objetivo}
        - Idade: {self.idade} anos
        - IMC: {self.imc:.1f}

        CRITÉRIOS:
        - Máximo 3 frases
        - Tom amigável e encorajador
        - Use o nome da pessoa
        - Específico para o objetivo
        - Transmita confiança no sucesso
        - Mencione que o L7Nutri acompanha a jornada

        EXEMPLOS DO TOM:
        "Olá [Nome]! Seu plano foi criado 100% para você..."
        "[Nome], você está no caminho certo para..."
        "Estamos aqui para te apoiar, [Nome]..."

        SEJA HUMANO E MOTIVADOR.
        """
        
        try:
            if self.modelo_ia:
                resposta = self.modelo_ia.generate_content(prompt)
                return resposta.text.strip()
            else:
                return self._gerar_mensagem_fallback()
                
        except Exception as e:
            print(f"Erro ao gerar mensagem: {str(e)}")
            return self._gerar_mensagem_fallback()

    def gerar_resultado_completo(self):
        """
        Junta tudo em um único objeto/dict pronto para exibir
        """
        print(f"Gerando análise completa para {self.nome}...")
        
        # Gerar cada componente
        plano = self.gerar_plano()
        treino = self.recomendar_treino()
        receita = self.recomendar_receita()
        suplemento = self.recomendar_suplemento()
        mensagem = self.mensagem_motivacional()
        
        # Montar resultado completo
        resultado = {
            'usuario': {
                'nome': self.nome,
                'idade': self.idade,
                'peso': self.peso,
                'altura': self.altura,
                'objetivo': self.objetivo,
                'imc': self.imc,
                'tmb': self.tmb
            },
            'resumo_objetivo': f"Olá {self.nome}! Seu plano foi criado especificamente para {self.objetivo}, considerando seu perfil completo.",
            'metas_nutricionais': plano.get('metas', self._gerar_metas_padrao()),
            'divisao_refeicoes': plano.get('refeicoes', self._gerar_refeicoes_padrao()),
            'recomendacao_treino': treino,
            'recomendacao_receita': receita,
            'suplemento_recomendado': suplemento,
            'mensagem_motivacional': mensagem,
            'plano_completo': plano,
            'data_criacao': datetime.now().isoformat(),
            'versao': '2.0',
            'metadados': {
                'modelo_ia_usado': self.modelo_ia is not None,
                'estilo_alimentar': self.estilo_alimentar,
                'experiencia_suplementos': self.experiencia_suplementos,
                'tempo_treino_meses': self.tempo_treino_meses
            }
        }
        
        print(f"Análise completa gerada para {self.nome}!")
        return resultado

    # === MÉTODOS AUXILIARES ===

    def _calcular_imc(self):
        """Calcula IMC"""
        try:
            altura_m = self.altura / 100
            return self.peso / (altura_m ** 2)
        except:
            return 22.0

    def _calcular_tmb(self):
        """Calcula Taxa Metabólica Basal (Mifflin-St Jeor)"""
        try:
            if self.sexo.lower() in ['masculino', 'homem', 'male']:
                tmb = (10 * self.peso) + (6.25 * self.altura) - (5 * self.idade) + 5
            else:
                tmb = (10 * self.peso) + (6.25 * self.altura) - (5 * self.idade) - 161
            return tmb
        except:
            return 1800.0

    def _calcular_calorias_objetivo(self):
        """Calcula calorias baseadas no objetivo"""
        try:
            tmb = self.tmb
            gasto_total = tmb * self.fator_atividade
            
            if 'emagrecer' in self.objetivo.lower() or 'perder' in self.objetivo.lower():
                return gasto_total - 500  # Déficit
            elif 'ganhar' in self.objetivo.lower() or 'massa' in self.objetivo.lower():
                return gasto_total + 500  # Superávit
            else:
                return gasto_total  # Manutenção
        except:
            return 2000.0

    def _processar_plano_nutricional(self, texto):
        """Processa resposta do plano nutricional"""
        try:
            import re
            
            # Extrair metas usando regex
            calorias = re.search(r'Calorias.*?(\d+)', texto)
            proteinas = re.search(r'Proteínas.*?(\d+)', texto)
            carboidratos = re.search(r'Carboidratos.*?(\d+)', texto)
            gorduras = re.search(r'Gorduras.*?(\d+)', texto)
            fibras = re.search(r'Fibras.*?(\d+)', texto)
            agua = re.search(r'Água.*?(\d+(?:\.\d+)?)', texto)
            
            metas = {
                'calorias': int(calorias.group(1)) if calorias else int(self.calorias_objetivo),
                'proteina': int(proteinas.group(1)) if proteinas else int(self.peso * 1.8),
                'carboidratos': int(carboidratos.group(1)) if carboidratos else int(self.calorias_objetivo * 0.45 / 4),
                'gorduras': int(gorduras.group(1)) if gorduras else int(self.calorias_objetivo * 0.25 / 9),
                'fibras': int(fibras.group(1)) if fibras else 25,
                'agua': float(agua.group(1)) if agua else 2.5
            }
            
            # Extrair refeições
            refeicoes = self._extrair_refeicoes_do_texto(texto)
            
            return {
                'metas': metas,
                'refeicoes': refeicoes,
                'texto_completo': texto
            }
            
        except Exception as e:
            print(f"Erro ao processar plano: {str(e)}")
            return self._gerar_plano_fallback()

    def _extrair_refeicoes_do_texto(self, texto):
        """Extrai refeições do texto da IA"""
        try:
            import re
            
            refeicoes = {}
            
            padroes = {
                'cafe_manha': r'Café da manhã.*?:(.*?)(?=\n|Lanche|$)',
                'lanche_manha': r'Lanche manhã.*?:(.*?)(?=\n|Almoço|$)', 
                'almoco': r'Almoço.*?:(.*?)(?=\n|Lanche|$)',
                'lanche_tarde': r'Lanche tarde.*?:(.*?)(?=\n|Jantar|$)',
                'jantar': r'Jantar.*?:(.*?)(?=\n|Ceia|$)',
                'ceia': r'Ceia.*?:(.*?)(?=\n|$)'
            }
            
            for refeicao, padrao in padroes.items():
                match = re.search(padrao, texto, re.IGNORECASE | re.DOTALL)
                if match:
                    refeicoes[refeicao] = match.group(1).strip()
                else:
                    refeicoes[refeicao] = self._gerar_refeicao_padrao(refeicao)
            
            return refeicoes
            
        except:
            return self._gerar_refeicoes_padrao()

    def _extrair_valor(self, texto, chave, padrao):
        """Extrai valor específico do texto"""
        try:
            import re
            match = re.search(f'{chave}\\s*([^\\n]+)', texto, re.IGNORECASE)
            return match.group(1).strip() if match else padrao
        except:
            return padrao

    def _extrair_lista(self, texto, chave):
        """Extrai lista de itens do texto"""
        try:
            import re
            # Buscar seção da chave até próxima seção
            secao = re.search(f'{chave}(.*?)(?=\\n[A-Z]|$)', texto, re.IGNORECASE | re.DOTALL)
            if secao:
                # Dividir por quebras de linha e limpar
                items = [item.strip('- ').strip() for item in secao.group(1).split('\n') if item.strip()]
                return [item for item in items if len(item) > 3]  # Filtrar itens válidos
            return []
        except:
            return []

    def _extrair_numero(self, texto, termo, padrao):
        """Extrai número relacionado a um termo"""
        try:
            import re
            match = re.search(f'{termo}.*?(\\d+)', texto, re.IGNORECASE)
            return int(match.group(1)) if match else padrao
        except:
            return padrao

    def _extrair_exercicios(self, texto):
        """Extrai lista de exercícios do treino"""
        exercicios = self._extrair_lista(texto, 'Exercícios principais:')
        if not exercicios:
            exercicios = self._extrair_lista(texto, 'Exercícios:')
        if not exercicios:
            # Fallback para exercícios básicos
            exercicios = ['Flexões', 'Agachamentos', 'Prancha', 'Burpees']
        return exercicios

    def _extrair_produto_l7(self, texto):
        """Identifica qual produto L7 foi recomendado"""
        texto = texto.upper()
        if 'L7NITRO' in texto or 'NITRO' in texto:
            return 'L7Nitro'
        elif 'L7TURBO' in texto or 'TURBO' in texto:
            return 'L7Turbo'
        else:
            return 'L7Ultra'  # Padrão para iniciantes

    def _classificar_receita_categoria(self):
        """Classifica categoria da receita baseado no objetivo"""
        if 'emagrecer' in self.objetivo.lower():
            return 'light'
        elif 'massa' in self.objetivo.lower():
            return 'hipercalorica'
        else:
            return 'equilibrada'

    def _gerar_promocao(self):
        """Gera promoção baseada no perfil"""
        if self.experiencia_suplementos == 'iniciante':
            return '25% OFF para primeiro suplemento'
        else:
            return '20% OFF + Frete Grátis'

    # === MÉTODOS FALLBACK ===

    def _gerar_plano_fallback(self):
        """Plano padrão quando IA não disponível"""
        return {
            'metas': self._gerar_metas_padrao(),
            'refeicoes': self._gerar_refeicoes_padrao(),
            'texto_completo': f'Plano personalizado para {self.nome} com {self.calorias_objetivo:.0f} kcal/dia'
        }

    def _gerar_metas_padrao(self):
        """Metas nutricionais padrão"""
        calorias = int(self.calorias_objetivo)
        return {
            'calorias': calorias,
            'proteina': int(self.peso * 1.8),
            'carboidratos': int(calorias * 0.45 / 4),
            'gorduras': int(calorias * 0.25 / 9),
            'fibras': 25,
            'agua': round(self.peso * 0.035, 1)
        }

    def _gerar_refeicoes_padrao(self):
        """Refeições padrão"""
        return {
            'cafe_manha': '07:00 - Aveia com frutas, ovos mexidos, café',
            'lanche_manha': '10:00 - Iogurte natural, castanhas',
            'almoco': '12:30 - Frango grelhado, arroz integral, salada verde',
            'lanche_tarde': '15:30 - Fruta, whey protein',
            'jantar': '19:00 - Peixe assado, batata doce, legumes refogados',
            'ceia': '21:30 - Caseína ou iogurte natural'
        }

    def _gerar_refeicao_padrao(self, refeicao):
        """Refeição específica padrão"""
        refeicoes = self._gerar_refeicoes_padrao()
        return refeicoes.get(refeicao, 'Refeição balanceada')

    def _gerar_treino_fallback(self):
        """Treino padrão quando IA não disponível"""
        return f"Treino funcional de 30 minutos, 3x por semana, adequado para {self.objetivo}. Exercícios: flexões, agachamentos, prancha."

    def _gerar_treino_fallback_dict(self):
        """Treino padrão em formato dict"""
        return {
            'tipo': 'Treino Funcional',
            'duracao': '30 minutos',
            'frequencia': '3x por semana',
            'exercicios': ['Flexões', 'Agachamentos', 'Prancha', 'Burpees'],
            'observacoes': 'Aumente a intensidade gradualmente',
            'link': f'https://l7personal.com/treinos/{self.objetivo.lower().replace(" ", "-")}',
            'texto_completo': self._gerar_treino_fallback()
        }

    def _gerar_receita_fallback(self):
        """Receita padrão quando IA não disponível"""
        return f"Receita saudável de frango grelhado com legumes, ideal para {self.objetivo}. Tempo: 25 minutos."

    def _gerar_receita_fallback_dict(self):
        """Receita padrão em formato dict"""
        return {
            'nome': 'Frango Grelhado com Legumes',
            'tempo_preparo': '25 minutos',
            'ingredientes': ['Peito de frango', 'Brócolis', 'Cenoura', 'Azeite', 'Temperos'],
            'modo_preparo': ['Tempere o frango', 'Grelhe por 15 min', 'Refogue os legumes'],
            'calorias_porcao': 350,
            'dica_extra': 'Varie os temperos para não enjoar',
            'link': 'https://l7chef.com/receitas/frango-grelhado-legumes',
            'categoria': self._classificar_receita_categoria(),
            'texto_completo': self._gerar_receita_fallback()
        }

    def _gerar_suplemento_fallback(self):
        """Suplemento padrão quando IA não disponível"""
        produto = 'L7Ultra' if self.experiencia_suplementos == 'iniciante' else 'L7Turbo'
        return f"Recomendo {produto} para seu perfil. Ideal para {self.objetivo}."

    def _gerar_suplemento_fallback_dict(self):
        """Suplemento padrão em formato dict"""
        produto = 'L7Ultra' if self.experiencia_suplementos == 'iniciante' else 'L7Turbo'
        return {
            'produto': produto,
            'justificativa': f'{produto} é ideal para seu perfil e objetivo',
            'como_usar': '1 dose 30 minutos antes do treino',
            'beneficios': ['Aumento de energia', 'Melhora do foco', 'Aceleração do metabolismo'],
            'orientacoes': 'Não exceda a dosagem recomendada',
            'link': f'https://l7shop.com/{produto.lower()}',
            'preco_promocional': self._gerar_promocao(),
            'cta_consultivo': 'Para potencializar seus resultados, veja como nosso suplemento pode ajudar. Clique e saiba mais!',
            'texto_completo': self._gerar_suplemento_fallback()
        }

    def _gerar_mensagem_fallback(self):
        """Mensagem motivacional padrão"""
        return f"Olá {self.nome}! Seu plano foi criado 100% para você, com metas, dicas e sugestões personalizadas. O L7Nutri vai te acompanhar em cada passo. Dúvidas? Conte sempre com a gente! Vamos pra cima!"


# Instância global para uso na aplicação
analise_ia = None

def inicializar_analise_ia(modelo_ia=None):
    """
    Inicializa sistema de análise nutricional
    """
    global analise_ia
    analise_ia = AnaliseNutricionalIA({}, modelo_ia)
    return analise_ia

def criar_analise_personalizada(dados_usuario, modelo_ia=None):
    """
    Cria nova instância de análise para usuário específico
    """
    return AnaliseNutricionalIA(dados_usuario, modelo_ia)
        
    def gerar_analise_completa(self, dados_usuario, dados_questionario):
        """
        Gera análise nutricional completa baseada no perfil do usuário
        """
        if not self.modelo_ia:
            return self._gerar_analise_fallback(dados_usuario, dados_questionario)
        
        try:
            # Preparar dados completos para análise
            perfil_completo = self._preparar_perfil_usuario(dados_usuario, dados_questionario)
            
            # Prompt específico para análise nutricional
            prompt = self._gerar_prompt_analise_nutricional(perfil_completo)
            
            # Gerar análise com IA
            resposta = self.modelo_ia.generate_content(prompt)
            
            # Processar resposta e extrair dados estruturados
            analise = self._processar_resposta_ia(resposta.text, perfil_completo)
            
            return analise
            
        except Exception as e:
            print(f"Erro na análise de IA: {str(e)}")
            return self._gerar_analise_fallback(dados_usuario, dados_questionario)
    
    def _preparar_perfil_usuario(self, dados_usuario, dados_questionario):
        """
        Prepara perfil completo do usuário para análise
        """
        perfil = {
            # Dados básicos
            'nome': dados_usuario.get('nome', 'Usuário'),
            'idade': dados_usuario.get('idade', 25),
            'peso': dados_usuario.get('peso', 70),
            'altura': dados_usuario.get('altura', 170),
            'sexo': dados_usuario.get('sexo', 'masculino'),
            'objetivo': dados_usuario.get('objetivo', 'manter peso'),
            'fator_atividade': dados_usuario.get('fator_atividade', 1.4),
            
            # Dados do questionário
            'estilo_alimentar': dados_questionario.get('estilo_alimentar', 'tradicional'),
            'experiencia_suplementos': dados_questionario.get('experiencia_suplementos', 'iniciante'),
            'tempo_treino_meses': dados_questionario.get('tempo_treino_meses', 0),
            'ja_usou_termogenico': dados_questionario.get('ja_usou_termogenico', False),
            'preferencias_alimentares': dados_questionario.get('preferencias_alimentares', []),
            'restricoes_alimentares': dados_questionario.get('restricoes_alimentares', []),
            'horario_treino': dados_questionario.get('horario_treino', 'manha'),
            'disponibilidade_cozinhar': dados_questionario.get('disponibilidade_cozinhar', 'media'),
            'objetivo_principal': dados_questionario.get('objetivo_principal', 'saude'),
            'nivel_estresse': dados_questionario.get('nivel_estresse', 'medio'),
            'qualidade_sono': dados_questionario.get('qualidade_sono', 'boa'),
            'consumo_agua': dados_questionario.get('consumo_agua', 'adequado')
        }
        
        # Calcular métricas básicas
        perfil['imc'] = self._calcular_imc(perfil['peso'], perfil['altura'])
        perfil['tmb'] = self._calcular_tmb(perfil)
        perfil['calorias_objetivo'] = self._calcular_calorias_objetivo(perfil)
        
        return perfil
    
    def _gerar_prompt_analise_nutricional(self, perfil):
        """
        Gera prompt específico para análise nutricional personalizada
        """
        return f"""
        ANÁLISE NUTRICIONAL PERSONALIZADA L7NUTRI
        
        Você é um nutricionista especialista da L7Nutri. Analise o perfil do usuário e gere um plano nutricional COMPLETO e PERSONALIZADO.
        
        PERFIL DO USUÁRIO:
        • Nome: {perfil['nome']}
        • Idade: {perfil['idade']} anos
        • Peso: {perfil['peso']} kg
        • Altura: {perfil['altura']} cm
        • Sexo: {perfil['sexo']}
        • IMC: {perfil['imc']:.1f}
        • Objetivo: {perfil['objetivo']}
        • Nível de atividade: {perfil['fator_atividade']}
        • TMB calculada: {perfil['tmb']:.0f} kcal
        • Meta calórica: {perfil['calorias_objetivo']:.0f} kcal
        
        DADOS DO QUESTIONÁRIO:
        • Estilo alimentar: {perfil['estilo_alimentar']}
        • Experiência com suplementos: {perfil['experiencia_suplementos']}
        • Tempo de treino: {perfil['tempo_treino_meses']} meses
        • Já usou termogênico: {perfil['ja_usou_termogenico']}
        • Horário de treino: {perfil['horario_treino']}
        • Disponibilidade para cozinhar: {perfil['disponibilidade_cozinhar']}
        • Objetivo principal: {perfil['objetivo_principal']}
        • Nível de estresse: {perfil['nivel_estresse']}
        • Qualidade do sono: {perfil['qualidade_sono']}
        • Consumo de água: {perfil['consumo_agua']}
        
        GERE UMA ANÁLISE COMPLETA INCLUINDO:
        
        1. RESUMO DO OBJETIVO (2-3 frases humanizadas)
        2. METAS NUTRICIONAIS DIÁRIAS:
           - Calorias: [valor] kcal
           - Proteína: [valor] g
           - Carboidratos: [valor] g
           - Gorduras: [valor] g
           - Fibras: [valor] g
           - Água: [valor] L
        
        3. DIVISÃO DE REFEIÇÕES (com horários sugeridos):
           - Café da manhã: [horário] - [3 alimentos específicos]
           - Lanche manhã: [horário] - [2 alimentos específicos]
           - Almoço: [horário] - [3 alimentos específicos]
           - Lanche tarde: [horário] - [2 alimentos específicos]
           - Jantar: [horário] - [3 alimentos específicos]
           - Ceia: [horário] - [1 alimento específico]
        
        4. RECOMENDAÇÃO L7CHEF:
           - Nome da receita: [nome específico]
           - Descrição: [1 frase sobre a receita]
           - Link: https://l7chef.com/receita/[nome-da-receita]
        
        5. RECOMENDAÇÃO L7PERSONAL:
           - Tipo de treino: [específico para o objetivo]
           - Duração: [tempo]
           - Frequência: [vezes por semana]
           - Link: https://l7personal.com/treino/[tipo-treino]
        
        6. SUPLEMENTO L7 RECOMENDADO:
           - Produto: L7Ultra, L7Turbo ou L7Nitro
           - Justificativa: [Por que esse produto é ideal]
           - Como usar: [dosagem e horários]
           - Link: https://l7shop.com/[produto]
        
        7. MENSAGEM MOTIVACIONAL:
           - [Mensagem personalizada e humanizada de 2-3 frases]
        
        CRITÉRIOS PARA SUPLEMENTOS:
        - L7Ultra: Iniciantes, primeiro suplemento, foco em energia
        - L7Turbo: Intermediários, já usaram suplementos, foco em performance
        - L7Nitro: Avançados, experientes, foco em resultados máximos
        
        SEJA ESPECÍFICO, PRÁTICO E MOTIVACIONAL. Use o nome do usuário na mensagem.
        """
    
    def _processar_resposta_ia(self, resposta_texto, perfil):
        """
        Processa resposta da IA e extrai dados estruturados
        """
        try:
            # Extrair seções da resposta
            analise = {
                'usuario': {
                    'nome': perfil['nome'],
                    'objetivo': perfil['objetivo'],
                    'imc': perfil['imc'],
                    'tmb': perfil['tmb']
                },
                'resumo_objetivo': self._extrair_secao(resposta_texto, "RESUMO DO OBJETIVO", "METAS NUTRICIONAIS"),
                'metas_nutricionais': self._extrair_metas_nutricionais(resposta_texto),
                'divisao_refeicoes': self._extrair_divisao_refeicoes(resposta_texto),
                'recomendacao_receita': self._extrair_recomendacao_receita(resposta_texto),
                'recomendacao_treino': self._extrair_recomendacao_treino(resposta_texto),
                'suplemento_recomendado': self._extrair_suplemento_recomendado(resposta_texto),
                'mensagem_motivacional': self._extrair_secao(resposta_texto, "MENSAGEM MOTIVACIONAL", ""),
                'analise_completa': resposta_texto,
                'data_criacao': datetime.now().isoformat(),
                'versao': '1.0'
            }
            
            return analise
            
        except Exception as e:
            print(f"Erro ao processar resposta da IA: {str(e)}")
            return self._gerar_analise_fallback(perfil, {})
    
    def _extrair_secao(self, texto, inicio, fim):
        """
        Extrai seção específica do texto da IA
        """
        try:
            inicio_idx = texto.find(inicio)
            if inicio_idx == -1:
                return ""
            
            if fim:
                fim_idx = texto.find(fim, inicio_idx)
                if fim_idx != -1:
                    return texto[inicio_idx + len(inicio):fim_idx].strip()
            
            return texto[inicio_idx + len(inicio):].strip()
            
        except:
            return ""
    
    def _extrair_metas_nutricionais(self, texto):
        """
        Extrai metas nutricionais da resposta
        """
        try:
            import re
            
            metas = {}
            
            # Buscar valores usando regex
            calorias = re.search(r'Calorias:?\s*(\d+)', texto)
            proteina = re.search(r'Proteína:?\s*(\d+)', texto)
            carboidratos = re.search(r'Carboidratos:?\s*(\d+)', texto)
            gorduras = re.search(r'Gorduras:?\s*(\d+)', texto)
            fibras = re.search(r'Fibras:?\s*(\d+)', texto)
            agua = re.search(r'Água:?\s*(\d+(?:\.\d+)?)', texto)
            
            metas['calorias'] = int(calorias.group(1)) if calorias else 2000
            metas['proteina'] = int(proteina.group(1)) if proteina else 150
            metas['carboidratos'] = int(carboidratos.group(1)) if carboidratos else 250
            metas['gorduras'] = int(gorduras.group(1)) if gorduras else 67
            metas['fibras'] = int(fibras.group(1)) if fibras else 25
            metas['agua'] = float(agua.group(1)) if agua else 2.5
            
            return metas
            
        except:
            return {
                'calorias': 2000,
                'proteina': 150,
                'carboidratos': 250,
                'gorduras': 67,
                'fibras': 25,
                'agua': 2.5
            }
    
    def _extrair_divisao_refeicoes(self, texto):
        """
        Extrai divisão de refeições da resposta
        """
        try:
            import re
            
            refeicoes = {}
            
            # Padrões para cada refeição
            padroes = {
                'cafe_manha': r'Café da manhã:?\s*([^\n]+)',
                'lanche_manha': r'Lanche manhã:?\s*([^\n]+)',
                'almoco': r'Almoço:?\s*([^\n]+)',
                'lanche_tarde': r'Lanche tarde:?\s*([^\n]+)',
                'jantar': r'Jantar:?\s*([^\n]+)',
                'ceia': r'Ceia:?\s*([^\n]+)'
            }
            
            for refeicao, padrao in padroes.items():
                match = re.search(padrao, texto, re.IGNORECASE)
                if match:
                    refeicoes[refeicao] = match.group(1).strip()
                else:
                    refeicoes[refeicao] = self._gerar_refeicao_padrao(refeicao)
            
            return refeicoes
            
        except:
            return self._gerar_refeicoes_padrao()
    
    def _extrair_recomendacao_receita(self, texto):
        """
        Extrai recomendação de receita L7Chef
        """
        try:
            import re
            
            nome_match = re.search(r'Nome da receita:?\s*([^\n]+)', texto)
            descricao_match = re.search(r'Descrição:?\s*([^\n]+)', texto)
            
            receita = {
                'nome': nome_match.group(1).strip() if nome_match else 'Frango Grelhado com Legumes',
                'descricao': descricao_match.group(1).strip() if descricao_match else 'Receita prática e saudável para o seu objetivo',
                'link': 'https://l7chef.com/receitas/frango-grelhado-legumes',
                'categoria': 'prato-principal'
            }
            
            return receita
            
        except:
            return {
                'nome': 'Frango Grelhado com Legumes',
                'descricao': 'Receita prática e saudável para o seu objetivo',
                'link': 'https://l7chef.com/receitas/frango-grelhado-legumes',
                'categoria': 'prato-principal'
            }
    
    def _extrair_recomendacao_treino(self, texto):
        """
        Extrai recomendação de treino L7Personal
        """
        try:
            import re
            
            tipo_match = re.search(r'Tipo de treino:?\s*([^\n]+)', texto)
            duracao_match = re.search(r'Duração:?\s*([^\n]+)', texto)
            frequencia_match = re.search(r'Frequência:?\s*([^\n]+)', texto)
            
            treino = {
                'tipo': tipo_match.group(1).strip() if tipo_match else 'Treino Funcional',
                'duracao': duracao_match.group(1).strip() if duracao_match else '45 minutos',
                'frequencia': frequencia_match.group(1).strip() if frequencia_match else '3x por semana',
                'link': 'https://l7personal.com/treinos/funcional-iniciante',
                'categoria': 'funcional'
            }
            
            return treino
            
        except:
            return {
                'tipo': 'Treino Funcional',
                'duracao': '45 minutos',
                'frequencia': '3x por semana',
                'link': 'https://l7personal.com/treinos/funcional-iniciante',
                'categoria': 'funcional'
            }
    
    def _extrair_suplemento_recomendado(self, texto):
        """
        Extrai recomendação de suplemento L7
        """
        try:
            import re
            
            # Buscar qual produto foi recomendado
            if 'L7Ultra' in texto:
                produto = 'L7Ultra'
                link = 'https://l7shop.com/l7ultra'
            elif 'L7Turbo' in texto:
                produto = 'L7Turbo'
                link = 'https://l7shop.com/l7turbo'
            elif 'L7Nitro' in texto:
                produto = 'L7Nitro'
                link = 'https://l7shop.com/l7nitro'
            else:
                produto = 'L7Ultra'
                link = 'https://l7shop.com/l7ultra'
            
            justificativa_match = re.search(r'Justificativa:?\s*([^\n]+)', texto)
            como_usar_match = re.search(r'Como usar:?\s*([^\n]+)', texto)
            
            suplemento = {
                'produto': produto,
                'justificativa': justificativa_match.group(1).strip() if justificativa_match else f'{produto} é ideal para o seu perfil e objetivo',
                'como_usar': como_usar_match.group(1).strip() if como_usar_match else '1 dose 30 minutos antes do treino',
                'link': link,
                'preco_promocional': '20% OFF para novos clientes',
                'categoria': 'termogenico'
            }
            
            return suplemento
            
        except:
            return {
                'produto': 'L7Ultra',
                'justificativa': 'L7Ultra é ideal para quem está começando',
                'como_usar': '1 dose 30 minutos antes do treino',
                'link': 'https://l7shop.com/l7ultra',
                'preco_promocional': '20% OFF para novos clientes',
                'categoria': 'termogenico'
            }
    
    def _calcular_imc(self, peso, altura):
        """
        Calcula IMC
        """
        try:
            altura_m = altura / 100
            return peso / (altura_m ** 2)
        except:
            return 22.0
    
    def _calcular_tmb(self, perfil):
        """
        Calcula Taxa Metabólica Basal (Mifflin-St Jeor)
        """
        try:
            peso = perfil['peso']
            altura = perfil['altura']
            idade = perfil['idade']
            sexo = perfil['sexo']
            
            if sexo.lower() in ['masculino', 'homem', 'male']:
                tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
            else:
                tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
            
            return tmb
            
        except:
            return 1800.0
    
    def _calcular_calorias_objetivo(self, perfil):
        """
        Calcula calorias baseadas no objetivo
        """
        try:
            tmb = perfil['tmb']
            fator_atividade = perfil['fator_atividade']
            objetivo = perfil['objetivo'].lower()
            
            gasto_total = tmb * fator_atividade
            
            if 'emagrecer' in objetivo or 'perder' in objetivo:
                return gasto_total - 500  # Déficit de 500 kcal
            elif 'ganhar' in objetivo or 'massa' in objetivo:
                return gasto_total + 500  # Superávit de 500 kcal
            else:
                return gasto_total  # Manutenção
                
        except:
            return 2000.0
    
    def _gerar_analise_fallback(self, dados_usuario, dados_questionario):
        """
        Gera análise padrão quando IA não está disponível
        """
        nome = dados_usuario.get('nome', 'Usuário')
        objetivo = dados_usuario.get('objetivo', 'manter peso')
        
        return {
            'usuario': {
                'nome': nome,
                'objetivo': objetivo,
                'imc': 22.0,
                'tmb': 1800.0
            },
            'resumo_objetivo': f"Olá {nome}! Seu plano foi criado para {objetivo} de forma saudável e sustentável.",
            'metas_nutricionais': {
                'calorias': 2000,
                'proteina': 150,
                'carboidratos': 250,
                'gorduras': 67,
                'fibras': 25,
                'agua': 2.5
            },
            'divisao_refeicoes': self._gerar_refeicoes_padrao(),
            'recomendacao_receita': {
                'nome': 'Frango Grelhado com Legumes',
                'descricao': 'Receita prática e saudável para o seu objetivo',
                'link': 'https://l7chef.com/receitas/frango-grelhado-legumes',
                'categoria': 'prato-principal'
            },
            'recomendacao_treino': {
                'tipo': 'Treino Funcional',
                'duracao': '45 minutos',
                'frequencia': '3x por semana',
                'link': 'https://l7personal.com/treinos/funcional-iniciante',
                'categoria': 'funcional'
            },
            'suplemento_recomendado': {
                'produto': 'L7Ultra',
                'justificativa': 'L7Ultra é ideal para quem está começando',
                'como_usar': '1 dose 30 minutos antes do treino',
                'link': 'https://l7shop.com/l7ultra',
                'preco_promocional': '20% OFF para novos clientes',
                'categoria': 'termogenico'
            },
            'mensagem_motivacional': f"Olá {nome}! Seu plano foi criado 100% para você, com metas, dicas e sugestões personalizadas. O L7Nutri vai te acompanhar em cada passo. Dúvidas? Conte sempre com a gente! Vamos pra cima!",
            'analise_completa': f"Análise personalizada para {nome} com foco em {objetivo}.",
            'data_criacao': datetime.now().isoformat(),
            'versao': '1.0'
        }
    
    def _gerar_refeicoes_padrao(self):
        """
        Gera divisão padrão de refeições
        """
        return {
            'cafe_manha': '07:00 - Aveia com frutas, ovos mexidos, suco natural',
            'lanche_manha': '10:00 - Iogurte natural, castanhas',
            'almoco': '12:30 - Frango grelhado, arroz integral, salada verde',
            'lanche_tarde': '15:30 - Fruta, whey protein',
            'jantar': '19:00 - Peixe assado, batata doce, legumes refogados',
            'ceia': '21:30 - Caseína ou iogurte natural'
        }
    
    def _gerar_refeicao_padrao(self, refeicao):
        """
        Gera refeição padrão específica
        """
        refeicoes_padrao = self._gerar_refeicoes_padrao()
        return refeicoes_padrao.get(refeicao, 'Refeição balanceada')

# Instância global para uso na aplicação
analise_ia = None

def inicializar_analise_ia(modelo_ia=None):
    """
    Inicializa sistema de análise nutricional
    """
    global analise_ia
    analise_ia = AnaliseNutricionalIA(modelo_ia)
    return analise_ia
