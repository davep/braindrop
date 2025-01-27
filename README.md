# Braindrop

![Braindrop](https://raw.githubusercontent.com/davep/braindrop/refs/heads/main/.images/braindrop-social-banner.png)

## Introduction

Braindrop is a terminal-based client application for the [raindrop.io
bookmarking service](https://raindrop.io/). It provides the ability to
manage and search your bookmarks in the terminal.

Braindrop is and generally always will be fairly opinionated about the
"best" way to make use of Raindrop (AKA how I like to use it); but where
possible I want to keep it quite general so it will be useful to anyone.

> [!NOTE]
> Braindrop isn't designed as a thin client for the Raindrop API; it isn't a
> terminal-based browser that does all the work on the server. It is
> designed to download your data if it looks like it's newer on the server,
> and then work locally, sending updates back to the server.
>
> If you have a *huge* Raindrop collection then this might not be the tool
> for you.

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

![Raindrop API token entry dialog](https://raw.githubusercontent.com/davep/braindrop/refs/heads/main/.images/raindrop-token-entry.png)

Paste the token into the input field and select `Connect`. Braindrop will
then download your data and you will be good to go.

*NOTE: if it's your preference, you can set the token in an environment
variable called `BRAINDROP_API_TOKEN`.*

## Using Braindrop

The best way to get to know Braindrop is to read the help screen, once in the
main application you can see this by pressing <kbd>F1</kbd>.

![Braindrop help](https://raw.githubusercontent.com/davep/braindrop/refs/heads/main/.images/braindrop-help.png)

## File locations

Braindrop stores files in a `braindrop` directory within both
[`$XDG_DATA_HOME` and
`$XDG_CONFIG_HOME`](https://specifications.freedesktop.org/basedir-spec/latest/).
If you wish to fully remove anything to do with Braindrop you will need to
remove those directories too.

Expanding for the common locations, the files normally created are:

- `~/.config/braindrop/configuration.json` -- The configuration file.
- `~/.local/share/braindrop/.token` -- The file that hold your API token.
- `~/.local/share/braindrop/raindrops.json` -- The locally-held Raindrop data.

## Getting help

If you need help, or have any ideas, please feel free to [raise an
issue](https://github.com/davep/braindrop/issues) or [start a
discussion](https://github.com/davep/braindrop/discussions).

## TODO

See [the TODO tag in
issues](https://github.com/davep/braindrop/issues?q=is%3Aissue+is%3Aopen+label%3ATODO)
to see what I'm planning.

[//]: # (README.md ends here)
