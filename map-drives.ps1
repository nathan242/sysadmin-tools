# Network drives
# Name = (Prefered letter, Path, (Alternate paths - will not map if already mapped on one of these))
$netdrvs = @{
    "Files" = ("F:", "\\server.local\Files", @("\\server\Files", "\\10.0.0.1\Files"));
    "Backup" = ("B:", "\\server.local\Backup", @("\\server\Backup", "\\10.0.0.1\Backup"))
}

# Drives for each group
# (Group, Drive Name)
$grpdrvs = @(
    ("domain.local\shares_files", "Files"),
    ("domain.local\shares_backup", "Backup")
)

# Valid drive letters
$letters = @("A:", "B:", "C:", "D:", "E:", "F:", "G:", "H:", "I:", "J:", "K:", "L:", "M:", "N:", "O:", "P:", "Q:", "R:", "S:", "T:", "U:", "V:", "W:", "X:", "Y:", "Z:")

# Get groups that current user is a member of
$headers = 0
$groups = @()
foreach ($i in $(whoami /GROUPS)) {
    #Write-Output "LINE: $i"
    if ($headers -eq 1) {
        $x = $i -split "   "
        $groups += $x[0]
    }
    elseif ($i -Like "===*") {
        $headers = 1
    }
}

# Get list of already mounted shares
$sharesmounted = @()
foreach ($i in $(net use)) {
    $x = $i -split "  "
    foreach ($j in $x) {
        if ($j -Like "\\*") {
            $sharesmounted += $j.Replace(" Microsoft Windows Network","").Trim()
        }
    }
}

# Get used drive letters
$drives = @()
foreach ($i in Get-PSDrive | Where-Object { $_.Provider -like "Microsoft.PowerShell.Core\FileSystem" } | Select-Object Name) {
    $drives += $i.Name+":"
}

# Mount drives
foreach ($gd in $grpdrvs) {
    # Are we in this group?
    if ($groups -contains $gd[0]) {
        # Is it currently not mapped?
        $mappath = $netdrvs[$gd[1]][1]
        $altpaths = $netdrvs[$gd[1]][2]
        if ($sharesmounted -notcontains $mappath -and (Compare-Object $sharesmounted $altpaths -IncludeEqual -ExcludeDifferent -passthru).length -lt 1) {
            $mapdrive = $netdrvs[$gd[1]][0]
            # Is the prefered letter already in use?
            $looped = 0
            while ($drives -contains $mapdrive) {
                # Get another free drive letter
                $li = [array]::IndexOf($letters, $mapdrive)+1
                if ($looped -eq 1 -and $li -ge [array]::IndexOf($letters,$netdrvs[$gd[1]][0])) {
                    write-output "Out of available drive letters. Aborting..."
                    exit
                } elseif ($li -ge $letters.length) {
                    $mapdrive = $letters[0]
                    $looped = 1
                } else {
                    $mapdrive = $letters[$li]
                }
            }
            # Map the drive
            write-output "Mapping $mapdrive -> $mappath ..."
            net use $mapdrive "$mappath"
            $sharesmounted += $mappath
            $drives += $mapdrive
        }
    }
}
