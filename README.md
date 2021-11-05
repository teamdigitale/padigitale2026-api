# ProssimaPA API

Vercel serverless functions
- Devono stare su un repo GitHub pubblico o privato che sia
- Due endpoint come functions:
* POST /users: si prende i dati, crea l'entry dell'utente nella mailing list con l'API di Mailgun, invia l'email di conferma sempre con API Mailgun (possibilmente da template) con il link di conferma generato che punta al secondo endpoint
* GET /confirm/user?data=xxxxx: si prende i dati cifrati (con il nome utente) da data e chiama l'API di Mailgun per settare l'equivalente di confirm = true. Ritorna poi una pagina HTML di conferma (o errore)
- L'API key di Mailgun e la chiave privata per generare il link di conferma stanno nelle variabili ambientali di Vercel (che sono cifrate)
- Il sito statico usa il primo endpoint
- Usiamo un custom domain (qualcosa.prossimapa.gov.it) per le functions

## Dev running

```sh
python dev.py
```

Server will be available at [http://0.0.0.0:1234/](http://0.0.0.0:1234/).
