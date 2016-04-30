# pianodb

A database companion to [pianobar].

- Free Software: ISC License

## Features

- TODO

## Quickstart
You can install `pianodb` with
```
pip install git+git://github.com/reillysiemens/pianodb.git@master
```

- TODO

## Configuration
`pianodb` uses a YAML configuration file which, by default, is located in
`~/.config/pianobar/pianodb.yml`. A sample configuration might look like this:
```yaml
---
client:
    remote:
        host: pianodb.example.tld
        port: 8000
    threshold: 10
    token: CB80CB12CC0F41FC87CA6F2AC989E27E
    database: /home/username/.config/pianobar/piano.db
server:
    interface: 10.0.0.1
    port: 8000
    workers: 4
    token: CB80CB12CC0F41FC87CA6F2AC989E27E
    database: /var/db/piano.db
```
The `client` and `server` mappings can be stored in the same file. When run as
`pianodb server` `pianodb` will look at only the key-value pairs in the
`server` mapping. Otherwise `pianodb` uses the key-value pairs in the `client`
mapping.

## Credits

This package was created with help from [Cookiecutter].

[pianobar]: https://6xq.net/pianobar
[Cookiecutter]: https://github.com/audreyr/cookiecutter
