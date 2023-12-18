import argparse
import os
from pathlib import Path
import subprocess
import plistlib


def list_snapshots(volume):
    try:
        result = subprocess.run(
            ["tmutil", "listlocalsnapshots", volume],
            capture_output=True,
            text=True,
            check=True,
        )
        snapshots = result.stdout.strip().split("\n")
        return snapshots
    except subprocess.CalledProcessError as e:
        print(f"Error listing snapshots: {e}")
        return None


def create_snapshot(volume):
    try:
        subprocess.run(
            ["tmutil", "localsnapshot", volume],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Snapshot created for volume {volume}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating snapshot: {e}")


def delete_snapshot(snapshot_id):
    try:
        subprocess.run(
            ["tmutil", "deletelocalsnapshots", snapshot_id],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Snapshot {snapshot_id} deleted")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting snapshot: {e}")


def elevated(*args, **kwargs) -> subprocess.CompletedProcess:
    if os.getuid() == 0 != None:
        return subprocess.run(*args, **kwargs)
    else:
        return subprocess.run(["sudo"] + [args[0][0]] + args[0][1:], **kwargs)


def get_root_vol():
    try:
        root_partition_info = plistlib.loads(
            subprocess.run("diskutil info -plist /".split(),
                           stdout=subprocess.PIPE)
            .stdout.decode()
            .strip()
            .encode()
        )
        root_mount_path = root_partition_info["DeviceIdentifier"]
        root_mount_path = (
            root_mount_path[:-
                            2] if root_mount_path.count("s") > 1 else root_mount_path
        )
        return root_mount_path

    except subprocess.CalledProcessError as e:
        print(f"Error obtaining boot volume info: {e}")
        return None


def check_if_root_is_apfs_snapshot():
    root_partition_info = plistlib.loads(
        subprocess.run("diskutil info -plist /".split(),
                       stdout=subprocess.PIPE)
        .stdout.decode()
        .strip()
        .encode()
    )
    try:
        is_snapshotted = root_partition_info["APFSSnapshot"]
    except KeyError:
        is_snapshotted = False
    return is_snapshotted


def _mount_root_vol() -> bool:
    """
    Attempts to mount the booted APFS volume as a writable volume
    at /System/Volumes/Update/mnt1

    Manual invocation:
        'sudo mount -o nobrowse -t apfs  /dev/diskXsY /System/Volumes/Update/mnt1'

    Returns:
        bool: True if successful, False if not
    """
    
    mount_location = "/System/Volumes/Update/mnt1"
    mount_extensions = f"{mount_location}/System/Library/Extensions"

    root_supports_snapshot = check_if_root_is_apfs_snapshot()

    # Returns boolean if Root Volume is available
    root_mount_path = get_root_vol()
    if root_mount_path.startswith("disk"):
        print(f"- Found Root Volume at: {root_mount_path}")
        if Path(mount_extensions).exists():
            print("- Root Volume is already mounted")
            return True
        else:
            if root_supports_snapshot is True:
                print("- Mounting APFS Snapshot as writable")
                result = elevated(["mount", "-o", "nobrowse", "-t", "apfs", f"/dev/{
                                  root_mount_path}", mount_location], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                if result.returncode == 0:
                    print(
                        f"- Mounted APFS Snapshot as writable at: {mount_location}")
                    if Path(mount_extensions).exists():
                        print("- Successfully mounted the Root Volume")
                        return True
                    else:
                        print("- Root Volume appears to have unmounted unexpectedly")
                else:
                    print("- Unable to mount APFS Snapshot as writable")
                    print("Reason for mount failure:")
                    print(result.stdout.decode().strip())
        return False

# Set up the argument parser
parser = argparse.ArgumentParser(description="Manage macOS snapshots.")
parser.add_argument(
    "action",
    choices=["list", "create", "delete", "get-root-vol", "mount-root-vol"],
    help="Action to perform (list, create, delete, get-root-vol, mount-root-vol)",
)
parser.add_argument(
    "--volume",
    help="The volume to create a snapshot of or list snapshots for",
    default="/",
)
parser.add_argument(
    "--id",
    help="The ID of the snapshot to delete (required for delete action)",
    required=False,
)

# Parse the arguments
args = parser.parse_args()

# Perform the action
if args.action == "list":
    snapshots = list_snapshots(args.volume)
    if snapshots:
        print("Snapshots:")
        for snapshot in snapshots:
            print(snapshot)
elif args.action == "create":
    create_snapshot(args.volume)
elif args.action == "delete":
    if not args.id:
        parser.error("The --id parameter is required for the delete action.")
    delete_snapshot(args.id)
elif args.action == "get-root-vol":
    root_vol = get_root_vol()
    if root_vol:
        print(f"Current root volume: {root_vol}")
elif args.action == "mount-root-vol":
    _mount_root_vol()
