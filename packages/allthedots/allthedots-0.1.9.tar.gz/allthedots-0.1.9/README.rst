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

Changelog
=========

0.1.5 (2016-01-24)
------------------

- Next travis test. [Christian Jurke]

- Use rst instead of markdown. [Christian Jurke]

0.1.3 (2016-01-24)
------------------

- Adding true script. [Christian Jurke]

0.1.2 (2016-01-24)
------------------

- Added pypi deploy. [Christian Jurke]

- Adding empty req-file. [Christian Jurke]

- Adding travis file. [Christian Jurke]

- Merge branch 'master' of github.com:cjrk/AllTheDots. [Christian Jurke]

  # Conflicts:
  #	allthedots.py

- Bugfix: Files might be recognized as parents. [Christian Jurke]

  /home/user/foo was recognized as parent of /home/user/foobar
  Therefore only /home/user/foo was saved.
  Fixed.

- Bugfix: Config dir is created directly in home. [Christian Jurke]

- Readme added. [Christian Jurke]

- Feature: Changed CLI and added backup via rsync. [Christian Jurke]


