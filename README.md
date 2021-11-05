# ProssimaPA API

# `POST /api/users` 
```json
{
 "address": "email.address@example.org",
 "representative": "Name Lastname",
 "ente": "Foobar",
 "enteSelect": "Baz",
 "message": "Hello world"
}
```

# `PUT /api/users/<address>/confirm`
```json
{"jwt": "..."}
```

## Dev running

```sh
python dev.py
```

Server will be available at [http://0.0.0.0:1234/](http://0.0.0.0:1234/).
