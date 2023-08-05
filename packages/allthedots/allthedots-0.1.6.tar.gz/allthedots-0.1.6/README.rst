AllTheDots
==========

This is a small script I use to make regular backups of my config-files.

Add ``/home/user/.ssh`` to the backup-list at ``<XDG_CONF>/AllTheDots/savelist.txt``::

	$ atd add /home/user/.ssh

Copy all files in the backup-list via rsync::

	$ atd backup user@hostname:/data/backups

ATD uses rsync to make a copy of all files and dirs in the backup-list to the specified target. The full path is preserved.
This means this two commands would create a backup of ``/home/user/.ssh`` in ``/data/backups/home/user/.ssh`` at the specified machine.
The backup can be made using any rsync compatible destination.

FYI: The rsync command used by the script is::

	$ rsync -arvPh --delete-delay --update --files-from $BACKUPLIST / $TARGET

