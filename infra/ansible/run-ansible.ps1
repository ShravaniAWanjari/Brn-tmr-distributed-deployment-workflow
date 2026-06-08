# PowerShell script to run Ansible commands inside the docker container on Windows.

# Ensure the image is built (will be fast if cached)
docker build -t ansible-control -f Dockerfile.ansible (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Mount workspace and SSH keys, and run the command
# We map the project root to /workspace inside the container.
# If .ssh directory exists, we mount it to allow SSH connections to target hosts.
$sshVolume = @()
$sshPath = Join-Path $HOME ".ssh"
if (Test-Path $sshPath) {
    $sshVolume = @("-v", "${sshPath}:/root/.ssh:ro")
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path

# Calculate relative path from project root to current directory
$relativePath = ""
if ($PWD.Path -ne $projectRoot) {
    $relativePath = [System.IO.Path]::GetRelativePath($projectRoot, $PWD.Path).Replace('\', '/')
}

$workdir = "/workspace"
if ($relativePath -ne "") {
    $workdir = "/workspace/$relativePath"
}

docker run --rm -it `
  -v "${projectRoot}:/workspace" `
  -w $workdir `
  -v /var/run/docker.sock:/var/run/docker.sock `
  $sshVolume `
  ansible-control $args
