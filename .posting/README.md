# Posting collections

This directory contains some [Posting](https://posting.sh)
[collections](https://posting.sh/guide/collections/) to help in testing and
viewing the results of calling on the [Raindrop
API](https://developer.raindrop.io/v1/raindrops).

If you want to use them there's a `Makefile` target in the root `Makefile`
of this repository:

```sh
make api
```

Of course you will also have to have Posting itself installed. You will also
need to have a `.env` file in the root of the repository directory, with
`API_TOKEN` set it it -- this will be your own Raindrop API token.

Eg:

```
API_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

[//]: # (README.md ends here)
