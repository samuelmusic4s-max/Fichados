#Proyect Fichados:

Entities:

1. Player
2. Match
3. Request
4. PaymentValidator
5. Field
6. City
7. Puntuacion
8. Team

Player:

- Id
- Name
- Age
- Puntuacion / Confiabilidad
- Ubicacion
- Posición
- Photo
- cityId

Match:

- Id
- teams
- CurrentQuantityPlayers
- MaxQuantityPlayers
- FieldId
- price
- time
- organizador
- date
- cityId
- location

Team:

- Id
- name
- players[]
- numPlayers

Request:

- Id
- playerId
- matchId
- comentario
- teamId

PaymentValidator:

- Id
- payment methods
- comprobante de pago

Field:

- Id
- Location
- Photo
- phoneNumber
- name
- address
- cityId

City:

- Id
- name
- codigo postal

Puntuacion:

- Id
- jugadorCalificadoId
- jugadorCalificadorId
- puntuation
- comentario
