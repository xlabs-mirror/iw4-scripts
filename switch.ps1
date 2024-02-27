param(
    [string]$version = "",
    [bool]$switch = $true,
    [switch]$force = $false,
    [switch]$killGame = $false,
    [switch]$ignoreRunning = $false,
    [switch]$startGame = $false,
    [string]$gameExe = "iw4x.exe",
    [string]$gameArgs = "-disable-notifies -unprotect-dvars -multiplayer -scriptablehttp -console -nointro +set logfile 0",
    [string]$basePath = (Get-Location).Path,
    [switch]$debug = $false,
    [switch]$help
)

$gameProcessName = $gameExe -split "\." | Select-Object -First 1
$success = $false
$scriptArgs = $MyInvocation.BoundParameters
$argStr = $scriptArgs.GetEnumerator() | ForEach-Object { "-$($_.Key) ""$($_.Value)""" } | ForEach-Object { $_ -join " " }
$scriptPath = $MyInvocation.MyCommand.Path
# $scriptName = $MyInvocation.MyCommand.Name
$gamePath = Join-Path $basePath $gameExe
$versions = @{}

function Log {
    param(
        [string]$message,
        [string]$level = "Info"
    )
    # $message = "$($scriptName): $message"
    switch ($level.ToLower()) {
        "warn" { Write-Warning "[$(Get-Date)] Warning: $message" }
        "warning" { Write-Warning "[$(Get-Date)] Warning: $message" }
        "error" { Write-Host "[$(Get-Date)] Error: $message" -ForegroundColor Red}
        "debug" { if ($debug) { Write-Host "[$(Get-Date)] $message" -ForegroundColor Blue } }
        "success" { Write-Host "[$(Get-Date)] ✅ $message" -ForegroundColor Green }
        default { Write-Host "[$(Get-Date)] $message" }
    }
}

# stdout log:
# Version: PS G:\Steam\steamapps\common\Call of Duty Modern Warfare 2> .\switch.ps1
# [02/27/2024 16:01:36] Read 1 versions from G:\Steam\steamapps\common\Call of Duty Modern Warfare 2\versions.json
# @{r4500=; r4499=; r4432=; 072=}
# WARNING: [02/27/2024 16:01:36] Warning: Detected game version: Unknown
# [02/27/2024 16:01:36] Available versions:
# [02/27/2024 16:01:36]  -

function Convert-JsonToPowershellArray {
    param(
        [Parameter(Mandatory=$true)]
        [string]$JsonFilePath
    )

    # Read the JSON file content
    $jsonContent = Get-Content -Path $JsonFilePath -Raw

    # Convert the JSON content to a PowerShell object
    $jsonObject = $jsonContent | ConvertFrom-Json

    # Initialize an empty hashtable to hold the converted data
    $convertedArray = @{}

    # Iterate over each key-value pair in the JSON object
    foreach ($key in $jsonObject.PSObject.Properties.Name) {
        $convertedArray[$key] = @{}
        foreach ($subKey in $jsonObject.$key.PSObject.Properties.Name) {
            $convertedArray[$key][$subKey] = $jsonObject.$key.$subKey
        }
    }

    # Return the converted array
    return $convertedArray
}
function Get-Versions {
    $versions = @{}
    # Read and convert the versions.json file to a PowerShell object
    $versionsPath = Join-Path $basePath "versions.json"
    $versionsItem = Get-Item -Path $versionsPath -ErrorAction SilentlyContinue
    if ($versionsItem) {
        try {
            $versions = Convert-JsonToPowershellArray -JsonFilePath $versionsPath
            # foreach ($version in $versions_json) {
            #     $versions[$version] = @{}
            #     foreach ($file in $versions_json[$version]) {
            #         $versions[$version][$file] = $versions_json[$version][$file]
            #     }
            # }
            Log "Read $($versions.Count) versions from $versionsPath" -level "Info"
            return $versions
        } catch {
            Log "Error reading or converting JSON file: $_" -level "Error"
        }
    }

    # Import the versions.ps1 file from $basePath to make the $versions array available
    $versionsPath = Join-Path $basePath "versions.ps1"
    $versionsItem = Get-Item -Path $versionsPath -ErrorAction SilentlyContinue
    if ($versionsItem) {
        . $versionsPath
        Log "Read $($versions.Count) versions from $versionsPath" -level "Info"
        return $versions
    }
    Log "Could not read versions from any source (json, ps1), falling back to hardcoded" -level "Error"
    return @{
        "latest" = @{
            "iw4x.dll" = "iw4x_latest.dll"
        }
        "r4432" = @{
            "iw4x.dll" = "iw4x_r4432.dll"
        }
    }
}
$versions = Get-Versions
function List-Versions {
    Log "Available versions:"
    $versions.Keys | ForEach-Object { Log " - $_" }
}

function Show-Help {
    Invoke-Expression "Get-Help ""$scriptPath"" -detailed"
}

function Get-Current-Version {
    $currentVersion = "Unknown"
    foreach ($version in $versions.Keys) {
        $firstItem = $versions[$version].Keys | Select-Object -First 1
        $targetPath = Join-Path $basePath $firstItem
        $targetItem = Get-Item -Path $targetPath -ErrorAction SilentlyContinue
        if ($targetItem) {
            $sourcePath = $targetItem.Target
            $sourceVersion = $sourcePath -split "_" | Select-Object -Last 1
            $sourceVersion = $sourceVersion -split "\." | Select-Object -First 1
            Write-Debug "Found symlink for $firstItem ($targetItem): $sourceVersion ($sourcePath)"
            if (-not $sourceVersion -eq "") {
                $currentVersion = $sourceVersion
            }
            break
        }
    }
    return $currentVersion
}
$currentVersion = Get-Current-Version

function Kill-Game {
    $runningProcesses = Get-Process | Where-Object { $_.ProcessName -eq $gameProcessName }
    if ($runningProcesses.Count -gt 0) {
        Log "Killing $gameProcessName..." -level "Warning"
        Stop-Process -Name $gameProcessName
        Start-Sleep -Seconds 1
    }
}

# Function to switch to a specified version
function Switch-GameVersion {
    param(
        [string]$version
    )
    if (-not $ignoreRunning) {
        $runningProcesses = Get-Process | Where-Object { $_.ProcessName -eq $gameProcessName }
        if ($runningProcesses.Count -gt 0) {
            if ($killGame) {
                Kill-Game
            } else {
                Log "Error: $gameExe is running. Please close it before switching versions or use -killGame to close it automatically."
                $userInput = Read-Host "Kill $gameExe? (y/n)"
                if ($userInput -eq "y") {
                    Kill-Game
                } else {
                    return $false
                }
            }
        }
    }
    if (-not $versions.ContainsKey($version)) {
        Log "Version $version does not exist."
        List-Versions
        return $false
    }
    if ($currentVersion -eq $version -and -not $force) {
        Log "Already on version $version."
        return $true
    }
    if (-not $switch) {
        Write-Warning "Switching is disabled by ""-switch false""." -level "Error"
        return $false
    }
    foreach ($target in $versions[$version].Keys) {
        $targetPath = Join-Path $basePath $target
        $targetIsFolder = $targetPath -notmatch "\."
        $targetType = if ($targetIsFolder) { "folder" } else { "file" }
        $sourcePath = Join-Path $basePath $versions[$version][$target]
        $targetItem = Get-Item -Path $targetPath -ErrorAction SilentlyContinue
        $goodTarget = if ($targetItem) { $targetItem.LinkType -eq "SymbolicLink" } else { $true }

        if (-not $goodTarget) {
            Write-Error "Error: $targetPath exists, but is not a symlink." -level "Error"
            return $false
        }
        if ($targetItem) {
            Write-Debug "Removing old symlink $targetPath"
            Remove-Item $targetPath
        }
        Write-Debug "Symlinking $targetType $sourcePath to $targetPath"
        if ($targetIsFolder) {
            New-Item -ItemType SymbolicLink -Path $targetPath -Target $sourcePath -Force
        } else {
            New-Item -ItemType SymbolicLink -Path $targetPath -Target $sourcePath
        }
    }
    Log "Switched to version $version." -level "Success"
}

Log "Script: ""$scriptPath"" $argStr $args" -level "Debug"
Log "Game: ""$gamePath"" $gameArgs" -level "Debug"
Log "Path: $basePath" -level "Debug"
if ($currentVersion -eq "Unknown") {
    Log "Detected game version: $currentVersion" -level "Warning"
} else {
    Log "Detected game version: $currentVersion" -level "Success"
}
if ($help) {
    Show-Help
    return
} elseif ($version -ne "") {
    # If version is provided as an argument, use it
    $success = Switch-GameVersion -version $version
} elseif ($args.Count -eq 1 -and $args[0] -ne "") {
    # If arguments are provided, use the first one as the version
    $version = $args[0]
    $success = Switch-GameVersion -version $version
} else {
    # If no arguments, prompt the user to select a version
    List-Versions
    $userInput = Read-Host "Version"
    if ($userInput -ne "") {
        $version = $userInput
        $success = Switch-GameVersion -version $version
    } else { Log "No version selected." -level "Error" }
}
if (-not $success) {
    Log "Failed to switch to version $version." -level "Error"
} else {
    if ($startGame) {
        Log "Starting $gameExe $gameArgs"
        Start-Process -FilePath $gamePath -ArgumentList $gameArgs
    }
}