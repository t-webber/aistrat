param(
    [string]$url, 
    [int]$port,
    [Alias("strat1")]
    [string]$strategy1 = "glouton",
    [Alias("strat2")]
    [string]$strategy2 = "memory",
    [Alias("two")]
    [switch]$twoplayers, 
    [Alias("h")]
    [switch]$help
)

clear-host
if (!$port) {
    $port = 8080
}

if (!$url) {
    $url = "http://localhost:$port"   
}

if ($help) {
    write-output "Usage: start_match.ps1 [-url <url>] [-port <port>] [-strat1 <strategy1>] [-strat2 <strategy2>] [-two] [-h]" 
} elseif ($twoplayers) {
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python $PSscriptRoot/game/server.py $port"
    start-sleep 1
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python $PSScriptRoot/strategies/$strategy1/main.py 1 $url"
    start-sleep 1
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python $PSScriptRoot/strategies/$strategy2/main.py 1 $url"
} else {
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python $PSScriptRoot/strategies/$strategy1/main.py 1 $url"
}
