$job_tag = 'voicemeter-fallback-input'

$base_dir = Join-Path $PSScriptRoot '..'
$stop_path = Join-Path $PSScriptRoot 'stop.ps1'
$main_path = Join-Path $base_dir 'main.py'

. $stop_path

Start-Process -WindowStyle Hidden -FilePath 'pyw' -ArgumentList @(
    $main_path
    '--job_tag'
    $job_tag
)
