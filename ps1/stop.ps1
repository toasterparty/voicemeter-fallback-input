$job_tag = 'voicemeter-fallback-input'

$base_dir = Join-Path $PSScriptRoot '..'
$main_path = Join-Path $base_dir 'main.py'

$pids = Get-CimInstance Win32_Process |
Where-Object {
    $_.Name -in @('pythonw.exe', 'python.exe', 'pyw.exe') -and
    $_.CommandLine -like "*$main_path*" -and
    $_.CommandLine -like "*--job_tag*$job_tag*"
} |
Select-Object -ExpandProperty ProcessId -Unique

$stopped = 0

foreach ($p in $pids) {
    if (Get-Process -Id $p -ErrorAction SilentlyContinue) {
        & taskkill.exe /pid $p /t /f 2>$null | Out-Null
        if (-not (Get-Process -Id $p -ErrorAction SilentlyContinue)) {
            $stopped++
        }
    }
}

if ($stopped -gt 0) { "Stopped $stopped voicemeter-fallback-input instance(s)" }
