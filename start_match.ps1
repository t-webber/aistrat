param(
    [string]$url, 
    [int]$port,
    [string]$strategy1 = "glouton",
    [string]$strategy2 = "memory",
    [Alias("two")]
    [switch]$twoplayers
)

clear-host

if (!$port) {
    $port = 8080
}

if (!$url) {
    $url = "http://localhost:$port"   
}

Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python $PSscriptRoot/game/server.py $port"

if ($twoplayers) {
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python $PSScriptRoot/strategies/$strategy1/main.py 1 $url"
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python $PSScriptRoot/strategies/$strategy2/main.py 1 $url"
} else {
    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python $PSScriptRoot/strategies/$strategy1/main.py 1 $url"
}
