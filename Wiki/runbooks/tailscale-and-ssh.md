# Reach the Snapdragon PC through Tailscale and SSH

This runbook explains how teammates reach the Dell Snapdragon deployment laptop from their own computers, open a terminal on it over SSH, and check who has access from the dashboard. [SH-T-036](../plan.md#snapdragon-deployment) tracks verification; [issue #9](https://github.com/davidmoshal/SecondHands/issues/9) assigns Tailscale setup to the remote-access lead.

Tailscale is a private network service. Each device that signs in gets a stable `100.x.y.z` address and a MagicDNS name (a short hostname shown by `tailscale status`) that works from anywhere, without opening router ports. SSH (Secure Shell) is the standard encrypted remote terminal. Here, Tailscale provides the network path and the Windows OpenSSH Server provides the terminal.

## Current state

Observed on the deployment laptop on 2026-10-17:

- **Tailscale:** version 1.104.1 is installed and connected. The PC belongs to the remote-access lead's Tailscale network (a "tailnet"). Read its MagicDNS hostname from `tailscale status`; commands below use `<pc-hostname>` as a placeholder.
- **Sharing:** the PC is shared with two teammates. Shared devices appear in the PC's Tailscale status as `device-of-shared-to-user`.
- **SSH server:** the Windows OpenSSH Server (`sshd`) was already installed. It was set to start automatically and started; it listens on port 22.
- **Firewall:** the Windows rule `OpenSSH-Server-In-TCP` allows SSH only on networks marked Private. The Tailscale adapter is Private and the Wi-Fi is Public, so SSH reaches the PC through Tailscale but not from other devices on the event Wi-Fi.
- **Checked:** from the PC itself, TCP port 22 on its own Tailscale address accepted a connection.
- **Not yet verified:** an SSH login from a teammate's Mac, key-based login, and whether access survives a PC restart.

Tailscale addresses and hostnames, the tailnet's DNS suffix, account emails, and the Windows username are kept out of this public repository. Ask the PC owner for the username, or read the addresses from your own `tailscale status`.

## Members and shares

There are two ways for a person to get access:

| Route | What the person can reach | Example |
| --- | --- | --- |
| Tailnet member (invited user) | Every device in the tailnet, subject to its access rules | The remote-access lead's own laptop and phone |
| Machine share | Only the shared machine. The share is one way: the person can connect to the PC, but the PC cannot reach their devices | two teammates, who connect to the PC from their own tailnets |

A machine share is the smallest grant and is enough for SSH and for an SSH-tunnelled dashboard. To add a teammate, the PC owner opens the [Tailscale admin console](https://login.tailscale.com/admin/machines), selects the PC, chooses **Share**, and sends the invite link. See [Tailscale's sharing documentation](https://tailscale.com/kb/1084/sharing).

## Connect from a Mac

1. Install Tailscale from the [download page](https://tailscale.com/download) and sign in.
2. Accept the share invite link. The PC then appears in the Tailscale menu.
3. Check the network path:

```sh
tailscale status            # the PC should be listed
tailscale ping <pc-hostname> # "pong ... via <ip:port>" is direct; "via DERP(...)" is relayed but works
```

If the `tailscale` command is missing on macOS, use the menu-bar app's **Install CLI** option, or call `/Applications/Tailscale.app/Contents/MacOS/Tailscale`.

## Open an SSH session

```sh
ssh <windows-user>@<pc-hostname>
```

If MagicDNS does not resolve, use the PC's `100.x.y.z` address from `tailscale status`. The session opens Windows `cmd.exe` by default; type `powershell` to switch shells.

Password login is enabled by default. For key-based login, copy the public key from your Mac (`cat ~/.ssh/id_ed25519.pub`, or create one with `ssh-keygen -t ed25519`) and add it on the PC. Windows reads keys for members of the Administrators group from a shared file, not from the user's home folder:

```powershell
# On the PC, in an administrator PowerShell
Add-Content C:\ProgramData\ssh\administrators_authorized_keys '<paste public key line>'
icacls C:\ProgramData\ssh\administrators_authorized_keys /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
```

For a non-administrator account, put the key in `C:\Users\<windows-user>\.ssh\authorized_keys` instead. sshd ignores the administrators file if its permissions allow anyone other than Administrators and SYSTEM.

Tailscale also has a built-in SSH server feature, "Tailscale SSH". It is not used here because it runs only on Linux and macOS hosts ([Tailscale SSH documentation](https://tailscale.com/kb/1193/tailscale-ssh)). Windows uses the OpenSSH Server above.

## Read model files from a separate Windows account

SSH authentication and permission to read a folder are separate. A new standard Windows account can sign in successfully while lacking access to model files stored under the PC owner's profile. Grant read access to the required model directories; administrator membership is not required for this use.

On 2026-10-17, the user requested access to the stored models from a separate SSH account. Read and execute permissions were granted to 11 model directories, including the repository's three main model stores, its two additional ONNX model directories, and model bundles in other local projects and caches. Two standalone compiled gesture exports received individual read grants. Selected parent directories received permission to list that directory only. The account remains a standard user. [The device inventory](../references/models/device-downloads.md#additional-local-model-locations) owns the model categories found during this inspection.

The local, Git-ignored `artifacts/model-locations.txt` lists the exact absolute paths. Ask the PC owner for the checkout location, then read this file from the SSH session:

```powershell
Get-Content 'CHECKOUT_PATH\artifacts\model-locations.txt'
```

Replace `CHECKOUT_PATH` with the actual PC checkout path. Each listed model directory can be opened directly using its absolute path; it does not belong to the SSH account's own profile. Absolute owner-profile paths and the account name remain outside Git.

Permissions were read back on 606 files and directories, with a read grant present on every checked item. The existing OneDrive deny rules concern deletion and do not deny reading. This verifies the filesystem rules; reading a model from a remote SSH session remains unverified. The grants allow reading existing files, not downloading, editing, or deleting models.

The user then explicitly requested access to the PC owner's entire profile folder. An inheritable read and execute grant was applied to that profile for the same standard SSH account. The command completed successfully, and the profile root and its ordinary top-level directories were checked for the read grant. This broader grant covers subfolders and files that inherit profile permissions; protected permissions and Windows compatibility junctions were not reset. It does not grant write access or administrator membership. The profile's absolute path remains outside Git, and a remote SSH read remains unverified.

For a future model directory, the folder owner, or an administrator if needed, can grant access with [Windows `icacls`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls):

```powershell
$remoteAccount = 'LOCAL_SSH_ACCOUNT'
$modelFolder = 'FULL_MODEL_FOLDER_PATH'
icacls $modelFolder /grant "${remoteAccount}:(OI)(CI)RX"
```

Replace both placeholders. `RX` allows reading and executing, and `(OI)(CI)` passes the permission to files and subdirectories that inherit permissions. Use the specific directory whose access the user has requested.

## Use the PC from the session

Commands typed into the SSH session run on the PC, using its checkout, Python environment, camera, and hardware. Change into the PC's SecondHands checkout before running project commands. The [development runbook](mac-and-snapdragon-development.md#send-changes-between-machines) explains how to move changes between the Mac and the PC with Git.

The dashboard services listen only on the PC's loopback address (`127.0.0.1`). To view the PC's dashboard in a browser on the Mac, start the services on the PC, then forward the UI port over SSH:

```sh
ssh -L 5173:127.0.0.1:5173 <windows-user>@<pc-hostname>
# then open http://localhost:5173 on the Mac
```

The UI development server forwards `/api` requests to the Python service on the PC, and the browser's origin is still `localhost:5173`, which the service accepts. With this setup the camera and models run on the PC. The forwarded dashboard has not yet been tested.

## Check access from the dashboard

The [local dashboard](mac-and-snapdragon-development.md#run-the-live-exploration-dashboard) includes a **Tailscale access** panel, which reads Tailscale status on the machine running the Python service:

- **Badge:** connected and the tailnet name, `not installed`, or the current Tailscale state, such as `Stopped` or `NeedsLogin`.
- **People with access:** each person who owns a listed device. A tailnet member owns devices in the PC's tailnet; a shared person has been given this machine. A green dot means at least one of their devices is online.
- **Device table:** this PC first, then the other devices, with online status.
- **Test connections:** runs `tailscale ping` and a TCP connection to port 22 for each online device that this PC can reach. The PC's own row shows whether its SSH server accepts connections. Offline devices and shared teammates' devices are listed but not tested, because a share is one way.

The panel tests only from the PC. Each teammate confirms their side with `tailscale ping <pc-hostname>` and `ssh <windows-user>@<pc-hostname>` from their own machine. The panel's backend returns display names, never login emails, and it is served only on loopback. Implementation: [`src/secondhands/api/tailscale.py`](../../src/secondhands/api/tailscale.py) and [`ui/src/dashboard/TailscalePanel.tsx`](../../ui/src/dashboard/TailscalePanel.tsx).

## PC setup commands

These commands were used on the PC on 2026-10-17. They require an administrator PowerShell; the first was skipped because the capability was already installed.

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Set-Service sshd -StartupType Automatic
Start-Service sshd
```

Check the result:

```powershell
Get-Service sshd                                    # Running, Automatic
Get-NetFirewallRule -Name OpenSSH-Server-In-TCP     # Enabled, Profile Private
Get-NetConnectionProfile                            # Tailscale should be Private
```

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `tailscale ping` times out | PC offline, Tailscale stopped, or the share was not accepted | Check the PC's tray icon or `tailscale status`; re-send the share link |
| Ping works, but SSH times out | `sshd` stopped, or the Tailscale adapter became Public | `Start-Service sshd`; `Set-NetConnectionProfile -InterfaceAlias Tailscale -NetworkCategory Private` |
| `Permission denied (publickey)` | Key placed in the wrong file, or file permissions too open | Use the administrators file and `icacls` command above |
| Hostname does not resolve | MagicDNS disabled on the viewer's tailnet | Use the `100.x.y.z` address |
| Dashboard panel says "Cannot read Tailscale status" | Python dashboard service is not running | Start it as described in the development runbook |
