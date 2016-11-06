# pianodb [![Build Status](https://img.shields.io/travis/reillysiemens/pianodb/master.svg?style=flat-square&label=build)](https://travis-ci.org/reillysiemens/pianodb) [![Coverage Status](https://img.shields.io/coveralls/reillysiemens/pianodb/master.svg?style=flat-square&label=coverage)](https://coveralls.io/github/reillysiemens/pianodb?branch=coverage)

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
`~/.config/pianobar/pianodb.yml`. A sample client configuration might look like
this:
```yaml
---
client:
    remote:
        host: pianodb.example.tld
        port: 8080
    threshold: 10
    token: CB80CB12CC0F41FC87CA6F2AC989E27E
```
If you just want to run `pianodb` locally you may omit the `remote` and `token`
mappings altogether and specify a `database` mapping.

A sample server configuration might look like this:
```yaml
---
server:
    interface: 10.0.0.1
    port: 8080
    workers: 4
    api_prefix: /api/v1
    token: CB80CB12CC0F41FC87CA6F2AC989E27E
    database: sqlite:////var/db/piano.db
```

### Configuring Databases
Thanks to [peewee] `pianodb` supports SQLite, MySQL, and PostgreSQL
backends. Technically peewee supports even more [schemes][db_url schemes], but
`pianodb` limits its testing to the aforementioned three. Here are some example
database configuration schemes:
```yaml
database: sqlite:////home/username/.config/pianobar/piano.db
# or
database: mysql://user:password@mysql.example.tld:3306/pianodb
# or
database: postgres://user:password@postgres.example.tld:5432/pianodb
```
Notice that the scheme component of the URI (`sqlite://`, etc.) **MUST** be
present and in the case of SQLite specify an absolute path.

## Credits

This package was created with help from [Cookiecutter].

[pianobar]: https://6xq.net/pianobar
[peewee]: http://docs.peewee-orm.com/
[db_url schemes]: http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#db-url
[Cookiecutter]: https://github.com/audreyr/cookiecutter
