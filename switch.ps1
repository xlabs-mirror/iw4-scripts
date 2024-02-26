param(
    [string]$version = "",
    [bool]$switch = $true,
    [bool]$force = $false,
    [bool]$killGame = $false,
    [bool]$ignoreRunning = $false,
    [bool]$startGame = $false,
    [string]$gameExe = "iw4x.exe",
    [string]$basePath = (Get-Location).Path,
    [switch]$help
)

$versions = @{
    "r4500" = @{
        "replacements" = @{
            "iw4x.dll" = "iw4x_r4500.dll"
            # "iw4x" = "iw4x_r4500" # folder
        }
    }
    "r4499" = @{
        "replacements" = @{
            "iw4x.dll" = "iw4x_r4499.dll"
            # "iw4x" = "iw4x_r4499" # folder
        }
    }
    "r4432" = @{
        "replacements" = @{
            "iw4x.dll" = "iw4x_r4432.dll"
            # "iw4x" = "iw4x_r4432" # folder
        }
    }
    "072" = @{
        "replacements" = @{
            "iw4x.dll" = "iw4x_072.dll"
            "iw4x" = "iw4x_072" # folder
        }
    }
}

$gameProcessName = $gameExe -split "\." | Select-Object -First 1
$success = $false
$scriptArgs = $args

function List-Versions {
    Write-Host "Available versions:"
    $versions.Keys | ForEach-Object { Write-Host " - $_" }
}

function Show-Help {
    $params = $scriptArgs
    $paramlist = $()
    foreach ($param in $params.Keys) {
        $paramType = $params[$param].ParameterType.Name
        $paramstr = "[-$param] <$paramType>"
        Write-Host "Param: $param, Type: $paramType"
        $paramlist += " $paramstr"
    }
    $paramstr = $paramlist -join " "
    Write-Host "Usage: switch.ps1 $paramstr"
    foreach ($param in $params.Keys) {
        $paramType = $params[$param].ParameterType.Name
        Write-Host "  -$param <$paramType>    $($params[$param].Attributes[0].NamedArguments.Value[0].TypedValue.Value)"
    }
}

function Get-Current-Version {
    $currentVersion = "Unknown"
    foreach ($version in $versions.Keys) {
        $firstItem = $versions[$version]["replacements"].Keys | Select-Object -First 1
        $targetPath = Join-Path $basePath $firstItem
        $targetItem = Get-Item -Path $targetPath -ErrorAction SilentlyContinue
        if ($targetItem) {
            $sourcePath = $targetItem.Target
            $sourceVersion = $sourcePath -split "_" | Select-Object -Last 1
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

# Function to switch to a specified version
function Switch-GameVersion {
    param(
        [string]$version
    )
    if (-not $ignoreRunning) {
        $runningProcesses = Get-Process | Where-Object { $_.ProcessName -eq $gameProcessName }
        if ($runningProcesses.Count -gt 0) {
            if ($killGame) {
                Write-Host "Killing $gameProcessName..."
                Stop-Process -Name $gameProcessName
            } else {
                Write-Host "Error: $gameExe is running. Please close it before switching versions or use -killGame to close it automatically."
                $userInput = Read-Host "Kill $gameExe? (y/n)"
                if ($userInput -eq "y") {
                    Write-Host "Killing $gameProcessName..."
                    Stop-Process -Name $gameProcessName
                } else {
                    return $false
                }
            }
        }
    }
    if (-not $versions.ContainsKey($version)) {
        Write-Host "Version $version does not exist."
        List-Versions
        return $false
    }
    if ($currentVersion -eq $version -and -not $force) {
        Write-Host "Already on version $version."
        return $true
    }
    if (-not $switch) {
        Write-Warning "Switching is disabled by ""-switch false""."
        return $false
    }
    foreach ($target in $versions[$version]["replacements"].Keys) {
        $targetPath = Join-Path $basePath $target
        $targetIsFolder = $targetPath -notmatch "\."
        $targetType = if ($targetIsFolder) { "folder" } else { "file" }
        $sourcePath = Join-Path $basePath $versions[$version]["replacements"][$target]
        $targetItem = Get-Item -Path $targetPath -ErrorAction SilentlyContinue
        $goodTarget = if ($targetItem) { $targetItem.LinkType -eq "SymbolicLink" } else { $true }

        if (-not $goodTarget) {
            Write-Error "Error: $targetPath exists, but is not a symlink."
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
    Write-Host "Switched to version $version."
}

Write-Host "Current version: $currentVersion"
if ($help) {
    Show-Help
    return
} elseif ($version -ne "") {
    # If version is provided as an argument, use it
    $success = Switch-GameVersion -version $version
} elseif ($args.Count -gt  0) {
    # If arguments are provided, use the first one as the version
    $success = Switch-GameVersion -version $args[0]
} else {
    # If no arguments, prompt the user to select a version
    List-Versions
    $userInput = Read-Host "Version"
    if ($userInput -ne "") {
        $success = Switch-GameVersion -version $userInput
    } else { Write-Host "No version selected." }
}
if (-not $success) {
    Write-Host "Failed to switch to version $version."
} else {
    if ($startGame) {
        $filePath = Join-Path $basePath $gameExe
        Start-Process -FilePath $filePath
    }
}