# Braindrop

> [!NOTE]
> This is still pre-release. Right now the client works read-only; Raindrop
> creation and editing is being added at the moment. The repository is
> available so anyone can have a play with the client UI.
>
> This also means I'm not accepting any code contributions right now, as the
> code is still under very active development. On the other hand feedback
> and ideas are **very** welcome.

![Braindrop](.images/braindrop.png)

## Introduction

Braindrop is a terminal-based client application for the [raindrop.io
bookmarking service](https://raindrop.io/). It provides the ability to
manage and search your bookmarks in the terminal.

Braindrop is and generally always will be fairly opinionated about the
"best" way to make use of Raindrop (AKA how I like to use it); but where
possible I want to keep it quite general so it will be useful to anyone.

## Installing

### pipx

The package can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
$ pipx install braindrop
```

Once installed run the `braindrop` command.

### Homebrew

The package is available via Homebrew. Use the following commands to install:

```sh
$ brew tap davep/homebrew
$ brew install braindrop
```

Once installed run the `braindrop` command.

## Getting started

Braindrop only works if you have a [raindrop.io](https://raindrop.io/)
account; there is a perfectly usable free tier. If you don't have an
account, go get one first.

To use Braindrop you will need an API access token. You can generate one in
your account settings, under `Integrations`. In `Integrations`:

- Look for the `For Developers` section
- Click on `Create new app`
- Enter a name for the new app (call it `Braindrop` for example, so you know
  what you're using it for).
- Accept the API use terms and guidelines and press `Create`
- Click on the freshly-created application in the list
- Near the bottom of the dialog that appears, click on `Create test token`
  and say `OK`.
- Copy the test token to your clipboard (or don't worry if you misplace it,
  you can always come back here to get it again).

Having done the above, when you run up Braindrop the first time it will ask
for this token:

![Raindrop API token entry dialog](.images/raindrop-token-entry.png)

Paste the token into the input field and select `Conttect`. Braindrop will
then download your data and you will be good to go.

*NOTE: if it's your preference, you can set the token in an environment
variable called `BRAINDROP_API_TOKEN`.*

## Using Tinboard

The best way to get to know Tinboard is to read the help screen, once in the
main application you can see this by pressing <kbd>F1</kbd>.

![Braindrop help](.images/braindrop-help.png)

## Getting help

If you need help, or have any ideas, please feel free to [raise an
issue](https://github.com/davep/braindrop/issues) or [start a
discussion](https://github.com/davep/braindrop/discussions).

## TODO

Things I'm considering adding or addressing:

- [X] Textual's help system is keyboard-hostile despite being of most use to
      keyboard-first users. Replace the current slide-in help panel with
      something useful and helpful.
      [#1](https://github.com/davep/braindrop/issues/1)
- [ ] Add the ability to add a Raindrop (current WIP)
- [ ] Add the ability to edit a Raindrop (current WIP)
- [ ] Add the ability to delete a Raindrop (current WIP)
- [ ] Add a user information dialog. There's some useful information about
      the user, so add a little dialog that will show it.

[//]: # (README.md ends here)
