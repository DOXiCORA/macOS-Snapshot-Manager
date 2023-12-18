# macOS Snapshot Manager

This Python script provides a command-line interface (CLI) for managing APFS snapshots on macOS. It allows users to list, create, and delete snapshots, as well as to get the current root volume identifier and mount the root volume if necessary.

## Features

- List all snapshots for a given volume.
- Create a snapshot for a given volume.
- Delete a specific snapshot by its identifier.
- Retrieve the current root volume identifier.
- Mount the root volume to a writable location if it's an APFS snapshot.

## Requirements

- Python 3.x
- macOS with APFS filesystem
- Command-line tools: `tmutil`, `diskutil`

## Usage

To use this script, run it from the command line with the desired action and options.

### Actions

- `list`: List all snapshots for the specified volume.
- `create`: Create a snapshot for the specified volume.
- `delete`: Delete a specified snapshot by its identifier.
- `get-root-vol`: Get the current root volume identifier.
- `mount-root-vol`: Mount the root volume to a writable location if it's an APFS snapshot.

### Options

- `--volume`: Specify the volume for listing or creating snapshots (default is `/`).
- `--id`: Specify the snapshot identifier for the delete action.

## Important Notes
Running some of these actions may require administrative privileges. Use sudo if necessary.
Be careful when deleting snapshots, as this cannot be undone.
Ensure you understand the implications of mounting the root volume as writable, especially in system locations

### Examples

List all snapshots for the root volume:
```bash
python snapshot_manager.py list --volume /
python snapshot_manager.py create --volume /
python snapshot_manager.py delete --id <snapshot_id>
python snapshot_manager.py get-root-vol
python snapshot_manager.py mount-root-vol