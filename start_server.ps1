param(
    [int]$port,
    [Alias("two")]
    [switch]$twoplayers
)

clear-host

if (!$port) {
    $port = 8080
}


    Start-Process PowerShell -ArgumentList "-NoExit", "-Command", "python $PSscriptRoot/game/server.py $port"
