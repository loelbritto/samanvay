$ErrorActionPreference='Stop'
$projectRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$contextsRoot=[IO.Path]::GetFullPath((Join-Path $projectRoot '.demo-contexts'))
$checkDirectory=[IO.Path]::GetFullPath((Join-Path $contextsRoot ('dependency-check-'+[guid]::NewGuid().ToString('N'))))
if(-not $checkDirectory.StartsWith($contextsRoot+[IO.Path]::DirectorySeparatorChar) -or (Test-Path -LiteralPath $checkDirectory)){throw 'Unsafe or existing check directory'}
$frontendDirectory=Join-Path $checkDirectory 'frontend'
New-Item -ItemType Directory -Path $frontendDirectory | Out-Null
foreach($file in @('package.json','package-lock.json','tsconfig.json','vite.config.ts','index.html')){
  Copy-Item -LiteralPath (Join-Path $projectRoot ('frontend\'+$file)) -Destination $frontendDirectory
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'frontend\src') -Destination $frontendDirectory -Recurse
$evidenceDirectory=Join-Path $projectRoot 'docs\evidence\stage9'
New-Item -ItemType Directory -Path $evidenceDirectory -Force | Out-Null
Push-Location $frontendDirectory
try{
  & npm.cmd ci --prefer-offline --no-fund --no-audit 2>&1 | Tee-Object -FilePath (Join-Path $evidenceDirectory 'clean-frontend-install.log')
  if($LASTEXITCODE -ne 0){throw 'Fresh lockfile frontend installation failed'}
  & npm.cmd run build 2>&1 | Tee-Object -FilePath (Join-Path $evidenceDirectory 'clean-frontend-build.log')
  if($LASTEXITCODE -ne 0){throw 'Fresh frontend build failed'}
}finally{Pop-Location}
$basePython=Join-Path $projectRoot 'backend\.venv\Scripts\python.exe'
$venvDirectory=Join-Path $checkDirectory 'python-venv'
& $basePython -m venv $venvDirectory
if($LASTEXITCODE -ne 0){throw 'Fresh Python environment creation failed'}
$checkPython=Join-Path $venvDirectory 'Scripts\python.exe'
& $checkPython -m pip install --disable-pip-version-check --no-input --no-warn-script-location -r (Join-Path $projectRoot 'backend\requirements.lock') 2>&1 | Tee-Object -FilePath (Join-Path $evidenceDirectory 'clean-python-install.log')
if($LASTEXITCODE -ne 0){throw 'Fresh Python lockfile installation failed'}
& $checkPython -m pip check 2>&1 | Tee-Object -FilePath (Join-Path $evidenceDirectory 'clean-python-check.log')
if($LASTEXITCODE -ne 0){throw 'Fresh Python dependency check failed'}
$priorEnvironment=@{}
foreach($name in @('SAMANVAY_ENV','SAMANVAY_DATA_DIR','SAMANVAY_CONTEXT_ID','SAMANVAY_ENABLE_DEMO_CONTROLS')){$priorEnvironment[$name]=[Environment]::GetEnvironmentVariable($name,'Process')}
$env:SAMANVAY_ENV='demo'
$env:SAMANVAY_DATA_DIR=Join-Path $checkDirectory 'python-smoke-data'
$env:SAMANVAY_CONTEXT_ID='local-synthetic'
$env:SAMANVAY_ENABLE_DEMO_CONTROLS='0'
Push-Location (Join-Path $projectRoot 'backend')
try{
  & $checkPython -m alembic upgrade head
  if($LASTEXITCODE -ne 0){throw 'Fresh migrations failed'}
  & $checkPython -m app.seed
  if($LASTEXITCODE -ne 0){throw 'Fresh add-only seed failed'}
  # The script lives outside backend; explicitly include the current source package.
  & $checkPython -c "import runpy,sys;sys.path.insert(0,'.');runpy.run_path('../scripts/check_clean_runtime.py')" 2>&1 | Tee-Object -FilePath (Join-Path $evidenceDirectory 'clean-python-startup.log')
  if($LASTEXITCODE -ne 0){throw 'Fresh Python startup smoke failed'}
}finally{
  Pop-Location
  foreach($name in $priorEnvironment.Keys){[Environment]::SetEnvironmentVariable($name,$priorEnvironment[$name],'Process')}
}
@{passed=$true;directory=$checkDirectory;frontend='fresh npm ci and build';backend='fresh venv/pinned installation/migration/seed/startup';existing_records_deleted=0}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $evidenceDirectory 'clean-dependencies.json') -Encoding utf8
