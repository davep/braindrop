# Braindrop ChangeLog

## v0.5.0

**Released: 2025-01-11**

- Fixed title and excerpt content not fully showing if there was text
  wrapped in square brackets within them.
  ([#64](https://github.com/davep/braindrop/issues/64))
- Added <kbd>#</kbd> as an alternative key for pulling up the tag search in
  the command palette. ([#71](https://github.com/davep/braindrop/pull/71))
- Added collection suggestions to the raindrop edit dialog.
  ([#73](https://github.com/davep/braindrop/pull/73))
- Added handling of the Raindrop.IO API rate limit when downloading all the
  data. ([#22](https://github.com/davep/braindrop/issues/22),
  [#72](https://github.com/davep/braindrop/issues/72))
- Fixed a problem where groups were showing the total collection count
  rather than the count of collections in that group.
  ([#77](https://github.com/davep/braindrop/issues/77))
- Fixed a crash after a redownload after a populated collection has been
  deleted. ([#79](https://github.com/davep/braindrop/issues/79))

## v0.4.0

**Released: 2025-01-09**

- Updated the help screen so that the command table shows the command name
  first. ([#53](https://github.com/davep/braindrop/pull/53))
- Updated the help screen so that the commands are sorted by the command
  name. ([#53](https://github.com/davep/braindrop/pull/53))
- Various cosmetic tweaks to the help screen.
  ([#53](https://github.com/davep/braindrop/pull/53))
- Notes are now rendered as a Markdown document.
  ([#60](https://github.com/davep/braindrop/pull/60))
- Fixed a crash caused by Raindrop sometimes including collections without
  parents in the list of child collections.
  ([#61](https://github.com/davep/braindrop/pull/61))

## v0.3.0

**Released: 2025-01-08**

- Fixed doubling-up of the raindrop details panel's help when the raindrop's
  tags have focus. ([#39](https://github.com/davep/braindrop/issues/39))
- Added a `Visit Link` command to the command palette.
  ([#43](https://github.com/davep/braindrop/pull/43))
- Added <kbd>v</kbd> as a global key for visiting a currently-highlighted
  link. ([#43](https://github.com/davep/braindrop/pull/43))
- Added public/private icons to the raindrops list.
  ([#48](https://github.com/davep/braindrop/pull/48))
- Added public/private icons and the collection name to the raindrop detail
  view. ([#48](https://github.com/davep/braindrop/pull/48))
- Fixed a trashed raindrop, while still in trash, thinking its collection is
  the last collection it was in.
  ([#47](https://github.com/davep/braindrop/issues/47))
- Made compact mode sticky.
  ([#51](https://github.com/davep/braindrop/pull/51))

## v0.2.0

**Released: 2025-01-05**

- Small tweaks to the styling of the raindrop details panel.
  ([#30](https://github.com/davep/braindrop/pull/30))
- Improved the way the age and the tags share the line in the raindrops view
  widget. ([#31](https://github.com/davep/braindrop/pull/31))
- Improved the styling of the main panels.
  ([#34](https://github.com/davep/braindrop/pull/34))
- Existing data is now shown a wee bit earlier on startup.
  ([#37](https://github.com/davep/braindrop/pull/37))

## v0.1.1

**Released: 2025-01-04**

- Fixed unnecessary error notifications when asking raindrop.io for
  suggestions for an URL that isn't really an URL.
  ([#21](https://github.com/davep/braindrop/pull/21))
- Suggested URL when making a new raindrop is now taken from the first line
  of the clipboard, ignoring any other text.
  ([#21](https://github.com/davep/braindrop/pull/21))

## v0.1.0

**Released: 2025-01-03**

- Added the ability to add a raindrop. ([#2](https://github.com/davep/braindrop/pull/2))
- Added the ability to edit a raindrop. ([#2](https://github.com/davep/braindrop/pull/2))
- Added the ability to delete a raindrop. ([#2](https://github.com/davep/braindrop/pull/2))
- Changed the redownload decision to work off last update rather than last
  action. ([#2](https://github.com/davep/braindrop/pull/2))

## v0.0.2

**Released: 2024-12-31**

- Initial pre-release version; a read-only client to test and show off the
  UI.

## v0.0.1

**Released: 2024-11-28**

- Initial placeholder package to test that the name is available in PyPI.

[//]: # (ChangeLog.md ends here)
