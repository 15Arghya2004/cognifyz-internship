$ErrorActionPreference = 'Stop'

$taskRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $taskRoot

function Get-PortOwner {
    param([int]$Port)

    $listening = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() |
        Where-Object { $_.Port -eq $Port }
    if (-not $listening) { return $null }

    $owner = [pscustomobject]@{ ProcessId = $null; ProcessName = 'unknown' }
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop | Select-Object -First 1
        $owner.ProcessId = $connection.OwningProcess
        $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        if ($process) { $owner.ProcessName = $process.ProcessName }
    } catch {
        # Port is busy but the owner could not be identified. Still a conflict.
    }
    return $owner
}

# A stale backend on 8000 would keep serving the dashboard silently, and a
# stale Vite on 5173 would open the wrong app. Refuse to start in either case.
foreach ($check in @(
    @{ Port = 8000; Role = 'backend (uvicorn)' },
    @{ Port = 5173; Role = 'dashboard (vite)' }
)) {
    $owner = Get-PortOwner -Port $check.Port
    if ($owner) {
        Write-Host ''
        Write-Host ("Port {0} is already in use, so the {1} cannot start cleanly." -f $check.Port, $check.Role) -ForegroundColor Yellow
        if ($owner.ProcessId) {
            Write-Host ("  Held by PID {0} ({1})" -f $owner.ProcessId, $owner.ProcessName)
            Write-Host ("  Stop it with:  Stop-Process -Id {0}" -f $owner.ProcessId)
        } else {
            Write-Host '  The owning process could not be identified.'
        }
        Write-Host '  Or reuse that process intentionally and skip this script.'
        Write-Host ''
        Write-Host 'Startup cancelled so the dashboard does not attach to an old backend.' -ForegroundColor Yellow
        exit 1
    }
}

Start-Process powershell -ArgumentList @(
    '-NoExit',
    '-Command',
    "Set-Location '$repoRoot'; python -m uvicorn task6_web_scraper.api:app --reload --port 8000"
)

Start-Process powershell -ArgumentList @(
    '-NoExit',
    '-Command',
    "Set-Location '$taskRoot/frontend'; npm run dev"
)

Start-Process 'http://localhost:5173'
Write-Host 'Backend: http://localhost:8000'
Write-Host 'Dashboard: http://localhost:5173'
