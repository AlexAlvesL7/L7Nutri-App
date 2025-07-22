# Script de testes automatizado para Windows PowerShell
# Ativa o ambiente virtual, sobe o servidor Flask, executa os testes e mostra o log

$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

Write-Host "Ativando ambiente virtual..."
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    . .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Ambiente virtual não encontrado. Criando venv..."
    python -m venv venv
    . .\venv\Scripts\Activate.ps1
}

Write-Host "Instalando dependências..."
pip install -r requirements.txt

Write-Host "Iniciando servidor Flask em background..."

Write-Host "Iniciando servidor Flask em background..."
$flaskProcess = Start-Process python -ArgumentList "app.py" -PassThru
$flaskPid = $flaskProcess.Id
Set-Content -Path flask_pid.txt -Value $flaskPid
Start-Sleep -Seconds 5

Write-Host "Executando testes com pytest..."
pytest --html=tests/relatorio_testes.html > test_log.txt

Write-Host "Finalizando servidor Flask..."
if (Test-Path "flask_pid.txt") {
    $flaskPidValue = Get-Content flask_pid.txt
    Stop-Process -Id $flaskPidValue -Force
    Remove-Item flask_pid.txt
}

Write-Host "Exibindo log dos testes:"
Get-Content test_log.txt
Write-Host "Relatório HTML gerado em tests/relatorio_testes.html"
