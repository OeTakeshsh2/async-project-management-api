[Fecha]
03/30/2026
Problema
JWT permite acceso a tokens(refresh/access) de tipo incorrecto segun endpoint

Causa
Mala configuracion inicial, ausencia de validacion antes del endpoint

Solución
Se agrego un endpoint para refresh tokens
Se agregaron validaciones en auth.py para el metodo create_user()
Se agrego una validacion en endpoint /me para evitar acceso con refresh tokens

Nota
!Refresh Token sigue permitiendo reusarse, corregi esto a futuro




[Fecha]
03/31/2026

Problema
Importaciones rotas en routes/users.py y falta total de endpoint + lógica para almacenar los refresh tokens hasheados en la base de datos (store_refresh_token, verify_refresh_token y UserToken).

Causa
- Imports incorrectos/duplicados y referencias a funciones que no existían en core/auth.py.
- El endpoint /refresh existía solo de nombre pero no tenía la lógica de validación ni persistencia del hash del refresh token.
- No se guardaba ningún refresh token en la tabla user_tokens → no había revocación ni control de sesión.

Solución
- Se corrigieron **todas las importaciones** en `app/routes/users.py`.
- Se completó y limpió `app/core/auth.py` con:
  - Modelo `UserToken`
  - Funciones `store_refresh_token` y `verify_refresh_token`
  - `decode_refresh_token` centralizado
  - Creación segura de access y refresh tokens
- Se implementó correctamente el endpoint `/users/refresh` con validación de hash en BD.
- Ahora el flujo completo funciona: login → guarda hash del refresh + devuelve ambos tokens.

Nota de seguridad (pendiente)
- Refresh Token todavía permite reutilización (reuse attack). Próxima mejora: implementar Refresh Token Rotation (invalidar el usado y emitir uno nuevo en cada /refresh).
