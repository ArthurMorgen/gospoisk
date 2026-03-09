# Создание чистого архива для развертывания на сервере

$archiveName = "parserbot_deploy.zip"

# Удаляем старый архив
if (Test-Path $archiveName) {
    Remove-Item $archiveName
}

# Создаем временную папку для архива
$tempDir = "temp_deploy"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Копируем основные файлы
Copy-Item "bot_interactive.py" $tempDir
Copy-Item "config.py" $tempDir
Copy-Item "database.py" $tempDir
Copy-Item "requirements.txt" $tempDir

# Копируем parsers (без __pycache__)
New-Item -ItemType Directory -Path "$tempDir\parsers" | Out-Null
Get-ChildItem -Path "parsers" -File | Where-Object {
    $_.Extension -ne ".pyc"
} | ForEach-Object {
    Copy-Item $_.FullName "$tempDir\parsers\"
}

# Создаем архив из временной папки
Compress-Archive -Path "$tempDir\*" -DestinationPath $archiveName

# Удаляем временную папку
Remove-Item -Recurse -Force $tempDir

Write-Host "✅ Архив создан: $archiveName"
Write-Host ""
Write-Host "Содержимое:"
Add-Type -A 'System.IO.Compression.FileSystem'
[IO.Compression.ZipFile]::OpenRead($archiveName).Entries.FullName | ForEach-Object {
    Write-Host "  $_"
}
