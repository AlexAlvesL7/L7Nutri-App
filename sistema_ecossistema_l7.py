#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 SISTEMA ECOSSISTEMA L7 INTELIGENTE
IA que analisa perfil e recomenda todo universo L7
"""

import json
from datetime import datetime, timedelta
import random

class EcossistemaL7Inteligente:
    """
    IA central que analisa perfil do usuário e recomenda
    todo o ecossistema L7 de forma personalizada
    """
    
    def __init__(self):
        self.produtos_l7 = {
            'l7ultra': {
                'nome': 'L7Ultra',
                'descricao': 'Termogênico ideal para iniciantes',
                'indicado_para': ['iniciante', 'primeira_vez', 'sensibilidade_baixa'],
                'beneficios': ['Acelera metabolismo', 'Queima gordura', 'Dá energia'],
                'link': 'https://l7shop.com/l7ultra',
                'preco': 'R$ 89,90'
            },
            'l7turbo': {
                'nome': 'L7Turbo', 
                'descricao': 'Para quem já se adaptou e quer mais resultado',
                'indicado_para': ['intermediario', 'segunda_compra', 'platô'],
                'beneficios': ['Potência máxima', 'Quebra platô', 'Resultados acelerados'],
                'link': 'https://l7shop.com/l7turbo',
                'preco': 'R$ 129,90'
            },
            'l7nitro': {
                'nome': 'L7Nitro',
                'descricao': 'Máxima potência para resultados extremos',
                'indicado_para': ['avancado', 'objetivo_intenso', 'experiencia_termogenicos'],
                'beneficios': ['Poder máximo', 'Foco intenso', 'Definição extrema'],
                'link': 'https://l7shop.com/l7nitro',
                'preco': 'R$ 169,90'
            }
        }
        
        self.treinos_personalizados = {
            'emagrecimento': {
                'foco': 'Queima de gordura',
                'treinos': ['HIIT 15min', 'Cardio dance', 'Funcional'],
                'frequencia': '5x por semana',
                'link': 'https://l7personal.com/emagrecimento'
            },
            'ganho_massa': {
                'foco': 'Construção muscular',
                'treinos': ['Musculação em casa', 'Calistenia', 'Resistência'],
                'frequencia': '4x por semana',
                'link': 'https://l7personal.com/ganho-massa'
            },
            'condicionamento': {
                'foco': 'Preparo físico',
                'treinos': ['Circuito funcional', 'Cardio intervalado'],
                'frequencia': '6x por semana',
                'link': 'https://l7personal.com/condicionamento'
            }
        }
        
        self.receitas_chef = {
            'low_carb': {
                'estilo': 'Baixo carboidrato',
                'receitas': ['Frango grelhado com legumes', 'Salada de atum', 'Omelete de espinafre'],
                'link': 'https://l7chef.com/low-carb'
            },
            'vegano': {
                'estilo': 'Plant-based',
                'receitas': ['Bowl de quinoa', 'Curry de grão-de-bico', 'Smoothie verde'],
                'link': 'https://l7chef.com/vegano'
            },
            'tradicional': {
                'estilo': 'Equilibrado',
                'receitas': ['Peito de frango com batata doce', 'Salmão grelhado', 'Arroz integral com feijão'],
                'link': 'https://l7chef.com/tradicional'
            }
        }

    def analisar_perfil_completo(self, dados_usuario):
        """Análise completa do perfil para recomendações do ecossistema"""
        
        # Dados básicos
        idade = dados_usuario.get('idade', 30)
        peso = dados_usuario.get('peso', 70)
        altura = dados_usuario.get('altura', 170)
        objetivo = dados_usuario.get('objetivo', 'emagrecimento')
        experiencia = dados_usuario.get('experiencia_suplementos', 'iniciante')
        estilo_alimentar = dados_usuario.get('estilo_alimentar', 'tradicional')
        nivel_atividade = dados_usuario.get('fator_atividade', 1.375)
        
        # Análise de estágio
        estagio = self._determinar_estagio(dados_usuario)
        
        # Gerar recomendações
        recomendacoes = {
            'perfil_analisado': self._gerar_analise_personalizada(dados_usuario),
            'suplemento_recomendado': self._recomendar_suplemento(estagio, objetivo, experiencia),
            'treino_personalizado': self._recomendar_treino(objetivo, nivel_atividade),
            'receitas_sugeridas': self._recomendar_receitas(estilo_alimentar, objetivo),
            'plano_nutricional': self._gerar_plano_nutricional(dados_usuario),
            'proximos_passos': self._definir_proximos_passos(estagio, objetivo),
            'mensagem_motivacional': self._gerar_mensagem_motivacional(dados_usuario)
        }
        
        return recomendacoes

    def _determinar_estagio(self, dados_usuario):
        """Determina o estágio do usuário para recomendação de produto"""
        
        experiencia = dados_usuario.get('experiencia_suplementos', 'iniciante')
        tempo_treino = dados_usuario.get('tempo_treino_meses', 0)
        ja_usou_termogenico = dados_usuario.get('ja_usou_termogenico', False)
        
        if experiencia == 'iniciante' or tempo_treino < 3 or not ja_usou_termogenico:
            return 'iniciante'
        elif tempo_treino >= 6 and ja_usou_termogenico:
            return 'avancado'
        else:
            return 'intermediario'

    def _recomendar_suplemento(self, estagio, objetivo, experiencia):
        """Recomenda suplemento L7 baseado no perfil"""
        
        if estagio == 'iniciante':
            produto = self.produtos_l7['l7ultra']
            motivo = "Ideal para quem está começando a jornada do emagrecimento. Fórmula balanceada e segura."
        elif estagio == 'intermediario':
            produto = self.produtos_l7['l7turbo']  
            motivo = "Você já tem experiência! Hora de potencializar seus resultados com uma fórmula mais intensa."
        else:
            produto = self.produtos_l7['l7nitro']
            motivo = "Para quem busca o máximo de resultados. Fórmula premium para objetivos ambiciosos."
        
        return {
            'produto': produto,
            'motivo_recomendacao': motivo,
            'cta': f"Conheça o {produto['nome']} - Seu aliado perfeito",
            'urgencia': "Oferta especial por tempo limitado!"
        }

    def _recomendar_treino(self, objetivo, nivel_atividade):
        """Recomenda treinos L7Personal baseado no objetivo"""
        
        if objetivo in ['perder_peso', 'emagrecimento']:
            treino = self.treinos_personalizados['emagrecimento']
        elif objetivo in ['ganhar_massa', 'ganho_muscular']:
            treino = self.treinos_personalizados['ganho_massa']
        else:
            treino = self.treinos_personalizados['condicionamento']
        
        # Personalizar intensidade baseado no nível de atividade
        if nivel_atividade < 1.4:
            intensidade = "Comece devagar e vá evoluindo gradualmente"
        elif nivel_atividade < 1.6:
            intensidade = "Intensidade moderada, perfeita para seus objetivos"
        else:
            intensidade = "Alta intensidade, você está preparado(a)!"
        
        return {
            'programa': treino,
            'intensidade_recomendada': intensidade,
            'treino_hoje': self._gerar_treino_do_dia(objetivo),
            'cta': "Acesse seus treinos personalizados agora"
        }

    def _recomendar_receitas(self, estilo_alimentar, objetivo):
        """Recomenda receitas L7Chef baseado no estilo alimentar"""
        
        if estilo_alimentar == 'low_carb':
            receitas = self.receitas_chef['low_carb']
        elif estilo_alimentar in ['vegano', 'vegetariano']:
            receitas = self.receitas_chef['vegano']
        else:
            receitas = self.receitas_chef['tradicional']
        
        return {
            'categoria': receitas,
            'receita_destaque': self._escolher_receita_do_dia(receitas['receitas']),
            'dica_chef': self._gerar_dica_culinaria(objetivo),
            'cta': "Veja todas as suas receitas personalizadas"
        }

    def _gerar_plano_nutricional(self, dados_usuario):
        """Gera resumo do plano nutricional personalizado"""
        
        # Cálculos básicos (usando dados já implementados)
        tmb = self._calcular_tmb(dados_usuario)
        calorias_objetivo = tmb * dados_usuario.get('fator_atividade', 1.375)
        
        # Ajustar por objetivo
        objetivo = dados_usuario.get('objetivo', 'manter_peso')
        if objetivo in ['perder_peso', 'emagrecimento']:
            calorias_objetivo -= 500
        elif objetivo in ['ganhar_massa', 'ganho_muscular']:
            calorias_objetivo += 500
        
        return {
            'meta_calorica': round(calorias_objetivo),
            'distribuicao_macros': {
                'proteinas': '30%',
                'carboidratos': '45%', 
                'gorduras': '25%'
            },
            'refeicoes_sugeridas': 5,
            'hidratacao': f"{round(dados_usuario.get('peso', 70) * 35)}ml por dia",
            'resumo': f"Plano personalizado para {objetivo} com {round(calorias_objetivo)} kcal/dia"
        }

    def _gerar_treino_do_dia(self, objetivo):
        """Gera treino específico para hoje"""
        
        treinos_emagrecimento = [
            "HIIT 15min: 30s ativo, 30s descanso",
            "Caminhada rápida 20min + exercícios funcionais",
            "Dança fitness 25min - queime calorias se divertindo!"
        ]
        
        treinos_massa = [
            "Treino de braços: flexões, triceps, bíceps (3x12)",
            "Pernas e glúteos: agachamentos, afundos (3x15)",
            "Core e abdômen: prancha, mountain climber (3x30s)"
        ]
        
        if objetivo in ['perder_peso', 'emagrecimento']:
            return random.choice(treinos_emagrecimento)
        else:
            return random.choice(treinos_massa)

    def _escolher_receita_do_dia(self, receitas):
        """Escolhe receita em destaque para hoje"""
        return random.choice(receitas)

    def _gerar_dica_culinaria(self, objetivo):
        """Gera dica culinária baseada no objetivo"""
        
        dicas_emagrecimento = [
            "Use temperos naturais como alho, cebola e ervas - dão sabor sem calorias!",
            "Prefira métodos de cocção como grelhados, assados ou cozidos no vapor",
            "Beba água antes das refeições para aumentar a saciedade"
        ]
        
        dicas_massa = [
            "Inclua uma fonte de proteína em cada refeição para construir músculos",
            "Carboidratos complexos fornecem energia duradoura para seus treinos",
            "Não esqueça das gorduras boas: abacate, nuts, azeite"
        ]
        
        if objetivo in ['perder_peso', 'emagrecimento']:
            return random.choice(dicas_emagrecimento)
        else:
            return random.choice(dicas_massa)

    def _definir_proximos_passos(self, estagio, objetivo):
        """Define evolução e próximos produtos/serviços"""
        
        proximos_passos = []
        
        if estagio == 'iniciante':
            proximos_passos.extend([
                "✅ Complete 30 dias com L7Ultra",
                "📈 Avalie seus resultados",
                "🚀 Considere evoluir para L7Turbo",
                "💪 Intensifique seus treinos"
            ])
        elif estagio == 'intermediario':
            proximos_passos.extend([
                "🔥 Maximize resultados com L7Turbo",
                "📊 Monitore seu progresso semanalmente", 
                "⭐ Próximo nível: L7Nitro em 60 dias",
                "🏆 Estabeleça novas metas desafiadoras"
            ])
        
        return proximos_passos

    def _gerar_mensagem_motivacional(self, dados_usuario):
        """Gera mensagem motivacional personalizada"""
        
        nome = dados_usuario.get('nome', 'Guerreiro(a)')
        objetivo = dados_usuario.get('objetivo', 'transformação')
        
        mensagens = [
            f"{nome}, sua jornada de {objetivo} começa agora! Cada escolha conta. 💪",
            f"Acredite em você, {nome}! Seu objetivo de {objetivo} está mais próximo do que imagina! 🌟",
            f"{nome}, o sucesso é a soma de pequenos esforços repetidos diariamente. Vamos juntos! 🚀",
            f"Sua determinação é sua maior força, {nome}! O {objetivo} que você sonha está se tornando realidade! ⭐"
        ]
        
        return random.choice(mensagens)

    def _gerar_analise_personalizada(self, dados_usuario):
        """Gera análise personalizada do perfil"""
        
        idade = dados_usuario.get('idade', 30)
        objetivo = dados_usuario.get('objetivo', 'emagrecimento')
        atividade = dados_usuario.get('fator_atividade', 1.375)
        
        analise = f"""
        🔍 ANÁLISE DO SEU PERFIL:
        
        Com {idade} anos e objetivo de {objetivo}, você está no momento ideal para começar sua transformação.
        
        Seu nível de atividade indica que você {'já tem uma rotina ativa' if atividade > 1.5 else 'pode aumentar a atividade física'}.
        
        Baseado no seu perfil, criamos um plano 100% personalizado que combina:
        ✅ Nutrição estratégica 
        ✅ Treinos adequados ao seu ritmo
        ✅ Suplementação inteligente
        ✅ Receitas práticas e saborosas
        """
        
        return analise.strip()

    def _calcular_tmb(self, dados_usuario):
        """Calcula TMB usando fórmula de Mifflin-St Jeor"""
        
        peso = dados_usuario.get('peso', 70)
        altura = dados_usuario.get('altura', 170) 
        idade = dados_usuario.get('idade', 30)
        sexo = dados_usuario.get('sexo', 'masculino')
        
        if sexo.lower() in ['masculino', 'm', 'male']:
            tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
        else:
            tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161
            
        return tmb

# Instância global para uso na aplicação
ecossistema_l7 = EcossistemaL7Inteligente()
