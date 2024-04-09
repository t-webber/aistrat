param(
    [string]$url, 
    [Alias("two")]
    [switch]$twoplayers
)

if ($twoplayers) {
    python "$PSScriptRoot/2players.py" $url
} else {
    python "$PSScriptRoot/1player.py" $url
}