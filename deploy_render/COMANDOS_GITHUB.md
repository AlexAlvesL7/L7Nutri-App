# COMANDOS PARA SUBIR PARA O GITHUB

## Depois de criar o repositório L7Nutri-App no GitHub, execute estes comandos:

```bash
# Substituir SEU_USUARIO pelo seu nome de usuário do GitHub
git remote add origin https://github.com/SEU_USUARIO/L7Nutri-App.git
git branch -M main
git push -u origin main
```

## Se der erro de autenticação, use:
```bash
git config --global user.email "seu@email.com"
git config --global user.name "Seu Nome"
```

## Depois de subir para o GitHub:
1. Vá para render.com
2. Clique em "New Web Service"
3. Conecte seu repositório GitHub
4. Configure as variáveis de ambiente:
   - SECRET_KEY = uma_chave_secreta_qualquer
   - JWT_SECRET_KEY = outra_chave_secreta
   - GEMINI_API_KEY = sua_chave_da_api_gemini
