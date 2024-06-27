param(
    [string]$url, 
    [Alias("two")]
    [switch]$twoplayers
)

clear-host
if ($twoplayers) {
    python "$PSScriptRoot/src/main.py" 2 $url
} else {
    python "$PSScriptRoot/src/main.py" 1 $url
}