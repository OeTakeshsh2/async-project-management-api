## [Fecha]
03/30/2026
### Problema
JWT permite acceso a tokens(refresh/access) de tipo incorrecto segun endpoint

### Causa
Mala configuracion inicial, ausencia de validacion antes del endpoint

### Solución
Se agrego un endpoint para refresh tokens
Se agregaron validaciones en auth.py para el metodo create_user()
Se agrego una validacion en endpoint /me para evitar acceso con refresh tokens

### Nota
!Refresh Token sigue permitiendo reusarse, corregi esto a futuro

