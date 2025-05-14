# health_check.ps1

# Инициализируем счётчики
$success = 0
$total   = 0

# 60 проверок с интервалом в 60 секунд
for ($i = 1; $i -le 60; $i++) {
    try {
        $response = Invoke-WebRequest `
            -Uri "http://localhost:8000/health" `
            -UseBasicParsing `
            -ErrorAction Stop

        if ($response.StatusCode -eq 200) {
            $success++
        }
    }
    catch {
        # Любая ошибка (404, таймаут и т.п.) — считаем как неуспех
    }

    $total++
    Start-Sleep -Seconds 60
}

# Вычисляем процент
if ($total -gt 0) {
    $uptime = [math]::Round(($success * 100) / $total, 2)
    Write-Output "Uptime: $uptime %"
}
else {
    Write-Output "No checks performed."
}
