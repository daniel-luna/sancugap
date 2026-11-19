# Sancugap API

API RESTful desarrollada con **FastAPI** y **SQLAlchemy 2** para la gestión de
usuarios e incidencias geolocalizadas, con autenticación mediante **JWT** y
control de acceso basado en roles (`admin` y `user`).

## Características

- Autenticación con OAuth2 (contraseña) y tokens JWT.
- Gestión de usuarios con roles (`admin`, `user`) y estado activo/inactivo.
- Catálogo de tipos y subtipos de incidencia.
- Registro de incidencias con coordenadas (`latitude`/`longitude`), almacenadas
  como `POINT` en MySQL o `BLOB` local en SQLite.
- Control de permisos: los usuarios solo ven sus propias incidencias; los
  administradores ven todas.
- Documentación interactiva automática en `/docs`.

## Tecnologías

- Python 3.12
- FastAPI
- SQLAlchemy 2
- MySQL (PyMySQL) y SQLite para desarrollo local
- Pydantic / pydantic-settings
- Passlib + bcrypt, python-jose
- Shapely (geometrías)
- pytest + httpx (pruebas sobre SQLite en memoria)

## Requisitos

- **Python 3.12** (el `python3` del sistema puede ser 3.14 y no tener las
  dependencias instaladas).
- Un servidor **MySQL** accesible para usar MySQL; no es necesario para el
  modo local con SQLite.
- `pip` para instalar las dependencias.

## Instalación

1. Clona el repositorio y entra en el directorio:

   ```bash
   git clone <url-del-repositorio> sancugap
   cd sancugap
   ```

2. Instala las dependencias:

   ```bash
   python3.12 -m pip install -r requirements.txt
   ```

3. Crea el archivo `.env` a partir del ejemplo:

   ```bash
   cp .env.example .env
   ```

4. Edita `.env` con tus valores:

   ```env
   DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/sancugap
   SECRET_KEY=cambia-esta-clave-en-produccion
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

   > `DATABASE_URL` y `SECRET_KEY` son obligatorios y no tienen valor por
   > defecto.

5. Crea la base de datos y las tablas desde cero con el esquema SQL inicial:

   ```bash
   mysql -u root -p < migrations/001_initial_schema.sql
   ```

   El script crea `sancugap` si no existe, junto con las tablas, índices y
   claves foráneas que usa la API. La aplicación también ejecuta
   `Base.metadata.create_all()` al arrancar; el proyecto no incluye todavía
   una herramienta de migraciones versionadas.

6. Crea el usuario administrador inicial (idempotente):

   ```bash
   python3.12 create_admin.py
   ```

   Credenciales por defecto:

   - Usuario: `admin`
   - Contraseña: `admin123`
   - Correo: `admin@sancugap.com`

   > Cambia la contraseña en cuanto arranques en un entorno real.

## Ejecución

```bash
source venv/bin/activate
python -m uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000` y la documentación en
`http://localhost:8000/docs`.

### Desarrollo local con SQLite

Para probar la API sin MySQL, desde la raíz del proyecto ejecuta:

```bash
source venv/bin/activate
DATABASE_URL=sqlite:///./sancugap-local.db python -m uvicorn main:app --reload
```

La aplicación crea `sancugap-local.db` y sus tablas al arrancar. Para crear el
administrador inicial, ejecuta en otra terminal, también desde la raíz:

```bash
source venv/bin/activate
DATABASE_URL=sqlite:///./sancugap-local.db python create_admin.py
```

## Pruebas

Las pruebas se ejecutan sobre SQLite en memoria, por lo que **no necesitan
MySQL** (aunque sí requieren el archivo `.env`):

```bash
python3.12 -m pytest
```

Para ejecutar un fichero o una prueba concreta:

```bash
python3.12 -m pytest tests/test_users.py
python3.12 -m pytest tests/test_users.py -k nombre_de_la_prueba
```

> No uses los binarios `pytest` o `uvicorn` directamente: sus shebangs apuntan
> a Python 3.14 y fallarán.

## Endpoints

Prefijo base: `/api/v1`.

### Autenticación

| Método | Ruta             | Descripción                          | Permiso |
| ------ | ---------------- | ------------------------------------ | ------- |
| POST   | `/auth/login`    | Obtiene un token JWT (form OAuth2)   | Público |
| POST   | `/auth/register` | Registra un nuevo usuario            | Admin   |

### Usuarios

| Método | Ruta                | Descripción                        | Permiso              |
| ------ | ------------------- | ---------------------------------- | -------------------- |
| GET    | `/users`            | Lista todos los usuarios           | Admin                |
| GET    | `/users/me`         | Devuelve el usuario autenticado    | Usuario activo       |
| GET    | `/users/{user_id}`  | Obtiene un usuario                 | Admin o el propio    |
| PUT    | `/users/{user_id}`  | Actualiza un usuario               | Admin o el propio    |
| DELETE | `/users/{user_id}`  | Elimina un usuario                 | Admin                |

> Solo un administrador puede modificar `role` e `is_active` de otros usuarios.

### Tipos de incidencia

| Método | Ruta                            | Descripción                  | Permiso |
| ------ | ------------------------------- | ---------------------------- | ------- |
| POST   | `/incidence-types/`             | Crea un tipo de incidencia   | Admin   |
| GET    | `/incidence-types/`             | Lista los tipos              | Admin   |
| GET    | `/incidence-types/{id}`         | Obtiene un tipo              | Admin   |
| PUT    | `/incidence-types/{id}`         | Actualiza un tipo            | Admin   |
| DELETE | `/incidence-types/{id}`         | Elimina un tipo              | Admin   |

### Subtipos de incidencia

| Método | Ruta                                | Descripción                    | Permiso |
| ------ | ----------------------------------- | ------------------------------ | ------- |
| POST   | `/incidence-sub-types/`             | Crea un subtipo                | Admin   |
| GET    | `/incidence-sub-types/`             | Lista los subtipos             | Admin   |
| GET    | `/incidence-sub-types/{id}`         | Obtiene un subtipo             | Admin   |
| PUT    | `/incidence-sub-types/{id}`         | Actualiza un subtipo           | Admin   |
| DELETE | `/incidence-sub-types/{id}`         | Elimina un subtipo             | Admin   |

### Incidencias

| Método | Ruta                    | Descripción                          | Permiso             |
| ------ | ----------------------- | ------------------------------------ | ------------------- |
| POST   | `/incidences/`          | Crea una incidencia                  | Usuario activo      |
| GET    | `/incidences/`          | Lista incidencias (propias o todas)  | Usuario activo      |
| GET    | `/incidences/{id}`      | Obtiene una incidencia               | Admin o propietario |
| PUT    | `/incidences/{id}`      | Actualiza una incidencia             | Admin o propietario |
| DELETE | `/incidences/{id}`      | Elimina una incidencia               | Admin o propietario |

Ejemplo de creación de una incidencia:

```json
{
  "type_id": 1,
  "sub_type_id": 2,
  "latitude": 40.4168,
  "longitude": -3.7038,
  "active": true
}
```

### Salud

| Método | Ruta          | Descripción          |
| ------ | ------------- | -------------------- |
| GET    | `/`           | Información de la API |
| GET    | `/api/health` | Comprobación de estado |

## Uso rápido de la API

1. Inicia sesión para obtener el token:

   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -d "username=admin&password=admin123"
   ```

2. Usa el token en las peticiones protegidas:

   ```bash
   curl http://localhost:8000/api/v1/users \
     -H "Authorization: Bearer <TOKEN>"
   ```

## Estructura del proyecto

```
.
├── api/
│   └── v1/
│       ├── endpoints/        # Manejadores de rutas
│       │   ├── auth.py
│       │   ├── users.py
│       │   ├── incidence_types.py
│       │   ├── incidence_sub_types.py
│       │   └── incidences.py
│       └── router.py         # Enrutador principal de la v1
├── core/
│   ├── auth.py               # JWT, hash de contraseñas y dependencias
│   ├── config.py             # Configuración (pydantic-settings)
│   ├── database.py           # Motor, sesión y Base de SQLAlchemy
│   ├── models.py             # Modelos ORM (incluye PointColumn)
│   └── schemas.py            # Esquemas Pydantic
├── tests/                    # Pruebas con pytest (SQLite)
├── create_admin.py           # Bootstrap del administrador
├── main.py                   # Punto de entrada de FastAPI
├── requirements.txt
└── .env.example
```

## Notas

- La columna `coordinate` usa el tipo `POINT` de MySQL; las rutas de incidencias
  aceptan y devuelven `latitude`/`longitude`.
- El paquete `bcrypt` está fijado a `<4.1.0` de forma intencionada por
  incompatibilidad con `passlib` 1.7.4. No lo actualices de forma aislada.
- No hay herramienta de migraciones: los cambios en los modelos requieren
  recrear o migrar la base de datos manualmente.
