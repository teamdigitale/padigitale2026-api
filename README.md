# ProssimaPA API

## `POST /api/users` 
```json
{
 "address": "email.address@example.org",
 "representative": "Name Lastname",
 "ente": "Foobar",
 "enteSelect": "Baz",
 "messageSelect": "foo-bar",
 "message": "Hello world"
}
```

### Response
#### Ok
HTTP code 200
```json
{"message": "ok"}
```
#### Recipient already registered
HTTP code 400
```json
{"message": "Address already exists 'email.address@example.org'"}
```

## `PUT /api/users/<address>/confirm`
```json
{"jwt": "..."}
```

### Response
#### Ok
HTTP code 200
```json
{"message": "ok"}
```
#### Signature verification failed
HTTP code 400
```json
{"message":"Signature verification failed"}
```

## Dev running

```sh
python dev.py
```

Server will be available at [http://0.0.0.0:1234/](http://0.0.0.0:1234/).
