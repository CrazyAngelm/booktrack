# health_check.ps1

# �������������� ��������
$success = 0
$total   = 0

# 60 �������� � ���������� � 60 ������
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
        # ����� ������ (404, ������� � �.�.) � ������� ��� �������
    }

    $total++
    Start-Sleep -Seconds 60
}

# ��������� �������
if ($total -gt 0) {
    $uptime = [math]::Round(($success * 100) / $total, 2)
    Write-Output "Uptime: $uptime %"
}
else {
    Write-Output "No checks performed."
}
