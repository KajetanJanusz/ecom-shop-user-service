# User Service

## Odpowiedzialność

Zarządzanie użytkownikami i autoryzacją. Serwis pomocniczy — nie jest przedmiotem badań porównawczych brokerów.

---

## Endpointy REST

### `POST /users/register`

Rejestracja nowego użytkownika.

**Request body:**

```json
{
  "email": "user@example.com",
  "username": "jankowalski",
  "password": "plaintext_password"
}
```

**Response `201 Created`:**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "jankowalski",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### `POST /users/token`

Logowanie — zwraca access token i refresh token.

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "plaintext_password"
}
```

**Response `200 OK`:**

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

---

### `POST /users/refresh`

Odświeżenie access tokena na podstawie refresh tokena.

**Request body:**

```json
{
  "refresh_token": "eyJ..."
}
```

**Response `200 OK`:**

```json
{
  "access_token": "eyJ..."
}
```

---

## Model bazy danych

**Tabela: `users`**

|Kolumna|Typ|Ograniczenia|
|---|---|---|
|`id`|`UUID`|PK, `gen_random_uuid()`|
|`email`|`VARCHAR`|UNIQUE, NOT NULL|
|`username`|`VARCHAR`|UNIQUE, NOT NULL|
|`password_hash`|`VARCHAR`|NOT NULL|
|`role`|`VARCHAR`|DEFAULT `'user'`, wartości: `user`, `admin`|
|`is_active`|`BOOLEAN`|DEFAULT `TRUE`|
|`created_at`|`TIMESTAMP`|DEFAULT `NOW()`|
|`updated_at`|`TIMESTAMP`|DEFAULT `NOW()`|

> Brak osobnej tabeli dla tokenów — tokeny są stateless (JWT).

---

## Strategia tokenów

- **Access token TTL:** 15 minut
- **Refresh token TTL:** 7 dni
- **Storage:** tokeny nie są persystowane w bazie ani Redis — dane zakodowane bezpośrednio w JWT (stateless)
- **Revocation:** świadomy trade-off — przez max 15 minut nieaktywny użytkownik może wykonywać operacje; akceptowalne dla celów pracy

### Payload JWT (access token)

```json
{
  "sub": "user_uuid",
  "role": "user",
  "exp": 1234567890
}
```

### Autoryzacja w innych serwisach

Każdy serwis samodzielnie weryfikuje JWT (podpis + expiry) bez odpytywania user-service. Middleware w `shared-lib` — wspólna logika dla wszystkich serwisów.

```
Request → serwis → shared-lib middleware → decode JWT → inject user_id do contextu
```

---

## Eventy

### Publikowane

|Event|Wyzwalacz|Payload|
|---|---|---|
|`user.registered`|rejestracja nowego użytkownika|`user_id`, `email`, `username`, `timestamp`|

### Konsumowane

Brak — user-service nie subskrybuje eventów od innych serwisów.

---

## Zależności

|Zależność|Cel|
|---|---|
|PostgreSQL|persystencja użytkowników|
|Broker (Kafka / RabbitMQ)|publikacja eventów|
|`shared-lib`|klient brokera, middleware JWT|