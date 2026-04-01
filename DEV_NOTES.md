[Fecha] 03/30/2026

## Problema
JWT permite acceso a tokens (refresh/access) de tipo incorrecto según endpoint.

## Causa
Mala configuración inicial, ausencia de validación antes del endpoint.

## Solución
- Se agregó un endpoint para refresh tokens.
- Se agregaron validaciones en `auth.py` para el método `create_user()`.
- Se agregó una validación en endpoint `/me` para evitar acceso con refresh tokens.

## Nota
Refresh Token sigue permitiendo reusarse, corregir esto a futuro.

---

[Fecha] 03/31/2026

## Problema
Importaciones rotas en `routes/users.py` y falta total de endpoint + lógica para almacenar los refresh tokens hasheados en la base de datos (`store_refresh_token`, `verify_refresh_token` y `UserToken`).

## Causa
- Imports incorrectos/duplicados y referencias a funciones que no existían en `core/auth.py`.
- El endpoint `/refresh` existía solo de nombre pero no tenía la lógica de validación ni persistencia del hash del refresh token.
- No se guardaba ningún refresh token en la tabla `user_tokens` → no había revocación ni control de sesión.

## Solución
- Se corrigieron todas las importaciones en `app/routes/users.py`.
- Se completó y limpió `app/core/auth.py` con:
  - Modelo `UserToken`.
  - Funciones `store_refresh_token` y `verify_refresh_token`.
  - `decode_refresh_token` centralizado.
  - Creación segura de access y refresh tokens.
- Se implementó correctamente el endpoint `/users/refresh` con validación de hash en BD.
- Ahora el flujo completo funciona: login → guarda hash del refresh + devuelve ambos tokens.

## Nota de seguridad (pendiente)
Refresh Token todavía permite reutilización (reuse attack). Próxima mejora: implementar Refresh Token Rotation (invalidar el usado y emitir uno nuevo en cada `/refresh`).

---

[Fecha] 03/31/2026

## Problema
Falta de protección en rutas y dependencia `get_current_user` no implementada.

## Causa
- No existía `get_current_user()` para extraer usuario desde access token.
- Faltaba `get_db()` en `database.py` para inyectar sesiones.
- Endpoints no tenían autenticación.

## Solución
- Se creó `get_db()` en `core/database.py`.
- Se creó `get_current_user()` en `core/dependencies.py` con decode de access token y búsqueda en BD.
- Se protegió endpoint `/users/me` con `Depends(get_current_user)`.

## Estado actual
- `/me` requiere token válido.
- 401 si token falta, expira o es inválido.
- Dependencia lista para proteger más endpoints.

---

[Fecha] 04/01/2026

## Problema
Alembic no podía generar ni aplicar migraciones por incompatibilidad con el motor asíncrono de SQLAlchemy (error `MissingGreenlet`).

## Causa
- El proyecto usa `create_async_engine` con `asyncpg`.
- Alembic, por defecto, solo funciona con motores síncronos.

## Solución
- Se modificó `migrations/env.py` para que Alembic utilice un motor síncrono (`create_engine` con `psycopg2`) solo durante las migraciones.
- Se generó la migración automática con `alembic revision --autogenerate -m "fix created_at timezone"`.
- Se aplicó la migración con `alembic upgrade head`, actualizando la columna `created_at` de la tabla `user_tokens` a `TIMESTAMP WITH TIME ZONE` con valor por defecto `now()`.

## Resultado
- La base de datos está sincronizada con los modelos.
- La aplicación sigue funcionando con `asyncpg` sin cambios.
- El flujo de migraciones ahora es compatible con el proyecto.
