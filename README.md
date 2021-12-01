# PA digitale 2026 API

## `POST /api/messages`

```json
{
  "address": "email.address@example.org",
  "representative": "other",
  "messageSelect": "foo-bar",
  "message": "Hello world",
  "captcha": "xxxx"
}
```
### Response

#### Ok

HTTP code 200

```json
{ "message": "ok" }
```
#### Captcha verification failed

HTTP code 400

```json
{ "message": "Captcha verification failed" }
```
## `POST /api/users`

```json
{
  "address": "email.address@example.org",
  "representative": "other",
  "ente": "Foobar",
  "enteType": "Foo",
  "enteSelect": "Baz"
}
```

### Response

#### Ok

HTTP code 200

```json
{ "message": "ok" }
```


## `PUT /api/users/<address>/confirm`

```json
{ "jwt": "..." }
```

### Response

#### Ok

HTTP code 200

```json
{ "message": "ok" }
```

#### Signature verification failed

HTTP code 400

```json
{ "message": "Signature verification failed" }
```

## Dev running

```sh
python dev.py
```

Server will be available at [http://0.0.0.0:1234/](http://0.0.0.0:1234/).
