param(
    [string]$Source = (Join-Path $PSScriptRoot 'examples\papers'),
    [string]$Output = (Join-Path $PSScriptRoot 'demo-output')
)

$ErrorActionPreference = 'Stop'
$PythonCommand = Get-Command py -ErrorAction SilentlyContinue
$PythonArguments = @('-3')
if (-not $PythonCommand) {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
    $PythonArguments = @()
}
if (-not $PythonCommand) {
    throw 'Python 3.10 or newer is required. Install Python, then run this script again.'
}

& $PythonCommand.Source @PythonArguments (Join-Path $PSScriptRoot 'run.py') $Source --output $Output
exit $LASTEXITCODE
