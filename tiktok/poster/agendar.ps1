# Registra 3 tarefas diarias (09:00, 14:00, 19:00) que postam 1 Short cada.
# Rode UMA vez, num PowerShell normal (nao precisa admin p/ tarefa do usuario):
#   powershell -ExecutionPolicy Bypass -File tiktok\poster\agendar.ps1
# Para remover: Unregister-ScheduledTask -TaskName "PalavraViva-TikTok-*" -Confirm:$false

$rodar = "C:\Users\NOTE\Desktop\Projetos\Palavra-Viva-3x\tiktok\poster\rodar.ps1"
$horarios = @("09:00", "14:00", "19:00")

foreach ($h in $horarios) {
    $nome = "PalavraViva-TikTok-$($h.Replace(':',''))"
    $acao = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$rodar`""
    $gatilho = New-ScheduledTaskTrigger -Daily -At $h
    $cfg = New-ScheduledTaskSettingsSet -StartWhenAvailable `
        -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
    Register-ScheduledTask -TaskName $nome -Action $acao -Trigger $gatilho `
        -Settings $cfg -Description "Posta 1 Short do Palavra Viva no TikTok" `
        -Force | Out-Null
    Write-Output "Tarefa criada: $nome  ($h todos os dias)"
}
Write-Output ""
Write-Output "Pronto. O PC precisa estar LIGADO nesses horarios."
Write-Output "Ver/gerenciar: Agendador de Tarefas do Windows (taskschd.msc)."
