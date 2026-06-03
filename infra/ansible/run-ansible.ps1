# PowerShell script to run Ansible commands inside the docker container on Windows.

# Ensure the image is built (will be fast if cached)
docker build -t ansible-control -f Dockerfile.ansible (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Mount workspace and SSH keys, and run the command
# We map the local directory containing playbooks to /workspace inside the container.
# If .ssh directory exists, we mount it to allow SSH connections to target hosts.
$sshVolume = @()
$sshPath = Join-Path $HOME ".ssh"
if (Test-Path $sshPath) {
    $sshVolume = @("-v", "${sshPath}:/root/.ssh:ro")
}

docker run --rm -it `
  -v "${PWD}:/workspace" `
  -v /var/run/docker.sock:/var/run/docker.sock `
  $sshVolume `
  ansible-control $args
