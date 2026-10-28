param(
  [Parameter(Mandatory=$true)][ValidateSet('api','frontend','worker')][string]$Service,
  [string]$ContextId = ''
)
$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$apiPort=8000
$uiPort=5173
$dataDirectory=Join-Path $projectRoot '.local-data'
if($ContextId){
  if($ContextId -notmatch '^demo-[a-f0-9]{24}$'){throw 'Invalid context ID'}
  $contextsRoot=[IO.Path]::GetFullPath((Join-Path $projectRoot '.demo-contexts'))
  $dataDirectory=[IO.Path]::GetFullPath((Join-Path $contextsRoot $ContextId))
  if(-not $dataDirectory.StartsWith($contextsRoot+[IO.Path]::DirectorySeparatorChar)){throw 'Unsafe context path'}
  $marker=Join-Path $dataDirectory 'SYNTHETIC_CONTEXT.json'
  if(-not (Test-Path -LiteralPath $marker)){throw 'Create the marked context first with python -m app.demo new --key <new-run-key>'}
  $contextMarker=Get-Content -LiteralPath $marker -Raw | ConvertFrom-Json
  if(-not $contextMarker.synthetic -or $contextMarker.context_id -ne $ContextId){throw 'Context marker mismatch'}
  $apiPort=8001
  $uiPort=5174
}
$env:SAMANVAY_ENV='demo'
$env:SAMANVAY_DATA_DIR=$dataDirectory
$env:SAMANVAY_CONTEXT_ID=if($ContextId){$ContextId}else{'local-synthetic'}
$env:SAMANVAY_ENABLE_DEMO_CONTROLS=if($ContextId){'1'}else{'0'}
$env:SAMANVAY_API_TARGET="http://127.0.0.1:$apiPort"
$pythonExecutable=Join-Path $projectRoot 'backend\.venv\Scripts\python.exe'
if(-not (Test-Path -LiteralPath $pythonExecutable)){throw 'Run the documented Python environment setup first'}
if($Service -eq 'frontend'){
  Push-Location (Join-Path $projectRoot 'frontend')
  try{& npm.cmd run dev -- --port $uiPort}finally{Pop-Location}
}else{
  Push-Location (Join-Path $projectRoot 'backend')
  try{
    if($Service -eq 'api'){& $pythonExecutable -m uvicorn app.main:app --host 127.0.0.1 --port $apiPort --no-access-log}
    else{& $pythonExecutable -m app.worker}
  }finally{Pop-Location}
}
