# UNI2_MASTER_SPEC

# 1. Visión del producto

## Nombre

Uni2

## Descripción

Uni2 es una plataforma de gestión para mutuales escolares.

Inicialmente será utilizada por la mutual del CET 3, pero el modelo queda preparado para soportar más colegios en el futuro.

El sistema permitirá administrar:

- Asociados y adherentes.
- Colegios, cursos e historial escolar.
- Cuotas y pagos.
- Credenciales digitales.
- Beneficios institucionales.
- Comercios adheridos y beneficios comerciales.
- Reportes administrativos básicos.
- Contabilidad simple con asientos y partidas.

En versiones futuras incorporará:

- Productos.
- Pedidos.
- Stock.
- Pagos de pedidos.
- Tickets de consultas.
- Notificaciones push.
- Pago online.
- Contabilidad ampliada.
- Mapa de comercios.

## Objetivo del MVP

El MVP debe permitir que la mutual funcione operativamente:

- Cargar y administrar asociados.
- Generar cuotas mensuales.
- Registrar pagos.
- Consultar deudas.
- Validar credenciales.
- Administrar beneficios y comercios.
- Obtener reportes básicos.

---

# 2. Roles

## Visitante

Usuario no autenticado. Puede consultar:

- Página de inicio.
- Información institucional.
- Beneficios.
- Comercios adheridos.
- Acceso al login.

## Asociado

Usuario autenticado vinculado a un asociado o adherente. Puede:

- Ver su panel.
- Ver su credencial digital.
- Ver estado de cuotas.
- Consultar beneficios.
- Consultar comercios adheridos.

## Administrador

Usuario interno de gestión. Puede:

- Gestionar asociados.
- Importar asociados.
- Crear usuarios para asociados.
- Gestionar colegios y cursos.
- Gestionar cuotas.
- Registrar pagos.
- Gestionar beneficios.
- Gestionar comercios.
- Consultar reportes.
- Registrar o consultar asientos simples.

## Comercio

Usuario vinculado a un comercio adherido. Puede:

- Iniciar sesión.
- Validar credenciales.
- Consultar beneficios propios.

---

# 3. Alcance del MVP

## Incluye

- Sitio público.
- Login.
- Roles básicos.
- Gestión de colegios.
- Gestión de cursos.
- Gestión de asociados y adherentes.
- Curso actual e historial de curso.
- Importación inicial desde Excel/CSV.
- Creación manual de usuarios para asociados.
- Generación de cuotas.
- Registro de pagos de cuotas.
- Pagos parciales de cuotas.
- Deudores.
- Credencial digital.
- Validación de credencial por comercio.
- Beneficios institucionales.
- Comercios adheridos.
- Beneficios de comercios.
- Reportes básicos.
- Contabilidad simple de ingresos.

## No incluye en MVP

- Pedidos.
- Stock.
- Productos para venta.
- Pago de pedidos.
- Tickets de consultas.
- Mensajería.
- PWA.
- Push notifications.
- Pago online.
- Saldo a favor.
- Intereses por mora acumulativos.
- Contabilidad completa.
- Asambleas.
- Votaciones.
- Mapa de comercios.

---

# 4. Decisiones generales cerradas

## Asociados

- El DNI es obligatorio.
- El número de asociado se genera automáticamente.
- `Asociado` representa tanto a asociados como a adherentes.
- No se crean tablas separadas para asociado y adherente.
- Los asociados participan de asambleas.
- Los adherentes no participan de asambleas.

## Estados de asociado

Estados posibles:

- activo
- inactivo
- egresado

## Usuarios

- Asociado no es lo mismo que Usuario.
- Puede existir un asociado sin usuario.
- Primero se puede cargar el padrón de asociados.
- El usuario Django se crea después, desde administración.
- El listado de asociados debe mostrar si tiene usuario.
- El listado debe mostrar último acceso si tiene usuario.

## Cursos

- Se guarda `curso_actual` en Asociado para facilitar consultas.
- Se guarda historial en `InscripcionCurso` para no perder información histórica.
- Cuando cambia el año, no se pisa el dato anterior: se crea una nueva inscripción.

## Credencial

- La credencial usa un token UUID aleatorio.
- El QR debe apuntar a una URL pública de validación que use ese token.
- No se deben exponer IDs internos ni números correlativos en URLs o QR.

## Cuotas y pagos

- Se permiten pagos parciales de cuotas.
- Los pagos se aplican a la deuda más antigua.
- No se permite registrar un pago mayor que la deuda seleccionada.
- Los asociados inactivos o egresados no generan nuevas cuotas, salvo decisión administrativa futura.
- Si una cuota no queda cancelada al vencimiento, se aplica un recargo fijo por mora una sola vez.

## Comercios

- Los comercios tienen dirección y datos geográficos.
- Los comercios pueden informar una URL de presencia web o redes sociales.
- Se guardan latitud y longitud para un futuro mapa.
- Los beneficios de comercios no van como texto dentro de Comercio.
- Se modelan con una entidad separada: `BeneficioComercio`.

## Contabilidad

- El MVP incluye contabilidad simple, no contabilidad completa.
- Un asiento contable tiene cabecera y partidas.
- Cada partida se imputa contra una cuenta contable.
- El diseño debe permitir que un asiento se origine en distintos tipos de pago presentes o futuros.

---

# 5. Modelo de datos MVP

## Usuario

Usuario de autenticación de Django.

Se recomienda usar el sistema estándar de Django inicialmente.

Grupos sugeridos:

- Administradores
- Asociados
- Comercios

Campos relevantes del User estándar:

- username
- email
- password
- first_name
- last_name
- is_active
- is_staff
- last_login
- date_joined

---

## Colegio

Representa una institución educativa.

Campos:

- id
- nombre
- direccion
- telefono
- email
- activo

Notas:

- Inicialmente existirá CET 3.
- Se agrega desde el inicio para dejar preparado el sistema para otros colegios.

---

## Curso

Representa un curso de un colegio.

Campos:

- id
- colegio
- nombre
- activo

Ejemplos:

- 1° 1°
- 1° 2°
- 3° 2°
- 5° 1°

Relación:

- Colegio 1 ─── N Curso

---

## Asociado

Representa a una persona asociada o adherente a la mutual.

Campos:

- id
- usuario
- nombre
- apellido
- dni
- email
- telefono
- fecha_nacimiento
- tipo
- numero_asociado
- token_credencial
- curso_actual
- estado
- fecha_alta
- fecha_inicio_cobro
- fecha_baja
- motivo_baja

Tipos:

- asociado
- adherente

Estados:

- activo
- inactivo
- egresado

Reglas:

- DNI obligatorio.
- DNI único.
- Número de asociado automático.
- Token de credencial UUID único.
- Usuario opcional.
- Curso actual opcional para adherentes.
- Para asociados alumnos, curso actual debería estar definido.

---

## InscripcionCurso

Historial académico del asociado.

Campos:

- id
- asociado
- curso
- ciclo_lectivo
- activa
- fecha_desde
- fecha_hasta

Reglas:

- Un asociado puede tener varias inscripciones históricas.
- Solo debería haber una inscripción activa por asociado para un ciclo lectivo.
- Cuando cambia el año, se crea una nueva inscripción.
- Si repite curso, igualmente se crea una nueva inscripción para el nuevo ciclo lectivo.

Ejemplo:

- Juan Pérez - 2026 - 3° 2° - no activa
- Juan Pérez - 2027 - 4° 2° - activa

---

## PeriodoCuota

Representa un período mensual de cuota.

Campos:

- id
- mes
- anio
- importe
- importe_recargo_mora
- fecha_vencimiento
- activo

Ejemplo:

- Mayo 2026 - $3000 - vence 10/05/2026

Reglas:

- El importe del período sirve como base para generar cuotas.
- El período define también el recargo fijo por mora a aplicar una sola vez si la cuota vence impaga.
- La cuota generada debe copiar el importe para conservar historial.
- La cuota generada debe copiar también el recargo por mora para conservar historial.
- El cambio de importe en un período futuro no debe modificar cuotas ya generadas.

---

## Cuota

Representa una cuota concreta de un asociado para un período.

Campos:

- id
- asociado
- periodo
- importe
- importe_recargo_mora
- importe_pagado
- estado
- fecha_generacion

Estados:

- pendiente
- parcial
- pagada
- vencida
- bonificada

Restricciones:

- No puede existir más de una cuota para el mismo asociado y período.

Reglas:

- Si importe_pagado es 0, la cuota puede estar pendiente o vencida.
- Si importe_pagado es mayor que 0 pero menor que importe, queda parcial.
- Si importe_pagado es igual a importe, queda pagada.
- Si se bonifica, queda bonificada.
- Si al vencimiento no fue cancelada por completo, pasa a exigir `importe + importe_recargo_mora`.

---

## Pago

Representa un ingreso de dinero.

Campos:

- id
- asociado
- fecha
- importe
- metodo
- observaciones
- registrado_por

Métodos:

- efectivo
- billetera_virtual

Reglas:

- En el MVP se usa para pagos de cuotas.
- En V2 también podrá aplicarse a pedidos mediante PagoPedido.

---

## PagoCuota

Aplicación de un pago a una cuota.

Campos:

- id
- pago
- cuota
- importe

Ejemplo:

Pago de $6000:

- PagoCuota: cuota marzo $3000
- PagoCuota: cuota abril $3000

Reglas:

- Permite saber qué cuotas fueron cubiertas por cada pago.
- Permite pagos parciales.
- Un pago puede aplicarse a varias cuotas.
- Una cuota puede tener varios pagos parciales.

---

## Beneficio

Beneficio institucional de la mutual.

Campos:

- id
- titulo
- descripcion
- activo
- orden

---

## Comercio

Comercio adherido a la mutual.

Campos:

- id
- usuario
- nombre
- responsable
- email
- telefono
- direccion
- url_presencia_web
- ciudad
- provincia
- latitud
- longitud
- activo

Reglas:

- Puede tener usuario de acceso.
- Puede validar credenciales.
- Puede tener múltiples beneficios.
- Puede informar una URL pública de sitio web o redes sociales.
- Latitud y longitud se guardan para mapa futuro.

---

## BeneficioComercio

Beneficio ofrecido por un comercio.

Campos:

- id
- comercio
- titulo
- descripcion
- tipo_descuento
- valor_descuento
- condiciones
- fecha_desde
- fecha_hasta
- activo

Tipos de descuento:

- porcentaje
- monto_fijo
- promocion
- otro

Ejemplos:

- 10% de descuento en útiles escolares.
- $1000 de descuento en compras mayores a $10000.
- 2x1 en anillados.

Reglas:

- Un comercio puede tener varios beneficios.
- Los beneficios vencidos no se muestran.
- Los beneficios futuros no se muestran hasta la fecha correspondiente.

---

## Notificacion

Notificación interna del sistema.

Campos:

- id
- usuario
- titulo
- mensaje
- leida
- fecha_creacion

Notas:

- En el MVP puede usarse como notificación interna.
- Push notifications quedan para una versión futura.

---

## CuentaContable

Cuenta utilizada para imputar partidas contables.

Campos:

- id
- codigo
- nombre
- tipo
- activa

Tipos:

- activo
- pasivo
- patrimonio
- ingreso
- egreso

---

## Asiento

Cabecera de un asiento contable simple.

Campos:

- id
- fecha
- descripcion
- tipo
- importe
- origen

Tipos:

- ingreso
- egreso

Reglas:

- Un asiento puede originarse en un pago de cuota y en futuras versiones en otros tipos de pago.
- Un asiento debe estar compuesto por 2 o más partidas.
- La suma del debe y del haber debe coincidir.
- El importe del asiento debe coincidir con el total balanceado de sus partidas.
- No reemplaza una contabilidad completa.

---

## PartidaAsiento

Línea contable perteneciente a un asiento.

Campos:

- id
- asiento
- cuenta_contable
- movimiento
- importe
- detalle

Movimientos:

- debe
- haber

Reglas:

- Un asiento puede tener 2 o más partidas.
- Cada partida debe imputarse a una cuenta contable.

---

# 6. Relaciones del MVP

- Colegio 1 ─── N Curso
- Usuario 1 ─── 0..1 Asociado
- Curso 1 ─── N Asociado como curso_actual
- Asociado 1 ─── N InscripcionCurso
- Curso 1 ─── N InscripcionCurso
- PeriodoCuota 1 ─── N Cuota
- Asociado 1 ─── N Cuota
- Asociado 1 ─── N Pago
- Pago 1 ─── N PagoCuota
- Cuota 1 ─── N PagoCuota
- Usuario 1 ─── N Notificacion
- Usuario 1 ─── 0..1 Comercio
- Comercio 1 ─── N BeneficioComercio
- CuentaContable 1 ─── N PartidaAsiento
- Asiento 1 ─── N PartidaAsiento
- Pago 1 ─── 0..N Asiento como origen posible

---

# 7. Reglas de negocio

## Asociados

### RN-001 Tipo de asociado

Un asociado puede ser de tipo:

- asociado
- adherente

### RN-002 Participación en asambleas

Los asociados participan de asambleas.

Los adherentes no participan de asambleas.

### RN-003 Historial

Los asociados inactivos o egresados conservan su historial.

### RN-004 Generación de cuotas por estado

Solo los asociados activos generan nuevas cuotas.

Los asociados inactivos o egresados no generan nuevas cuotas.

### RN-005 DNI obligatorio

Todo asociado debe tener DNI.

### RN-006 DNI único

No puede existir más de un asociado con el mismo DNI.

### RN-007 Número de asociado automático

El número de asociado debe generarse automáticamente.

### RN-008 Usuario opcional

Un asociado puede existir sin usuario de acceso.

---

## Cursos

### RN-009 Curso actual

El curso actual se guarda en Asociado para simplificar consultas.

### RN-010 Historial de curso

El historial se guarda en InscripcionCurso.

### RN-011 Cambio de año

Cuando un alumno cambia de curso, se crea una nueva InscripcionCurso y se actualiza curso_actual.

### RN-012 Repetición de curso

Si un alumno repite, igualmente se crea una nueva InscripcionCurso para el nuevo ciclo lectivo.

---

## Altas

### RN-013 Alta antes del día 15

Si el alta ocurre antes del día 15, el asociado paga el mes actual.

### RN-014 Alta después del día 15

Si el alta ocurre después del día 15, comienza a pagar desde el mes siguiente.

### RN-015 Fecha de inicio de cobro

La fecha de alta y la fecha de inicio de cobro son independientes.

El sistema debe usar fecha_inicio_cobro para generar cuotas.

---

## Cuotas

### RN-016 Cuota única por período

No puede existir más de una cuota por asociado y período.

### RN-017 Importe histórico

Cada cuota almacena su propio importe.

### RN-018 Estados de cuota

Una cuota puede estar:

- pendiente
- parcial
- pagada
- vencida
- bonificada

### RN-019 Generación de cuotas

Se generan cuotas para asociados activos cuya fecha_inicio_cobro sea menor o igual al período generado.

### RN-020 Cuota ya generada

Si la cuota ya existe para el asociado y período, no debe generarse otra.

### RN-020 bis Recargo por mora

Si al vencimiento la cuota no está totalmente cancelada, se aplica un recargo fijo por mora una sola vez.

### RN-020 ter Historial de mora

El recargo por mora debe copiarse desde `PeriodoCuota` a `Cuota` al momento de generar la cuota.

---

## Pagos

### RN-021 Aplicación a deuda más antigua

Los pagos se aplican a la deuda más antigua primero.

### RN-022 Pago parcial

Se permiten pagos parciales de cuotas.

### RN-023 Pago mayor a deuda

No se permite registrar un pago mayor que la deuda seleccionada.

### RN-023 bis Pago fuera de término

Si el pago se registra después del vencimiento y la cuota no había sido cancelada, la deuda exigible incluye el recargo fijo por mora.

### RN-024 Pago de múltiples cuotas

Un pago puede aplicarse a varias cuotas mediante PagoCuota.

### RN-025 Método de pago

Los métodos permitidos en MVP son:

- efectivo
- billetera_virtual

---

## Usuarios

### RN-026 Creación separada de usuario

Crear asociado no crea automáticamente un usuario.

### RN-027 Creación manual de usuario

El administrador puede crear un usuario para un asociado existente.

### RN-028 Asociado con usuario existente

No se puede crear un nuevo usuario para un asociado que ya tiene usuario vinculado.

### RN-029 Username sugerido

El username puede ser el DNI.

### RN-030 Último acceso

El listado de asociados debe mostrar el último acceso usando `User.last_login`.

---

## Comercios

### RN-031 Múltiples beneficios

Un comercio puede ofrecer múltiples beneficios.

### RN-032 Vigencia de beneficios

Los beneficios pueden tener fecha de inicio y fecha de fin.

### RN-033 Comercio activo

Solo comercios activos pueden validar credenciales.

---

## Credenciales

### RN-034 Credencial válida

Solo asociados activos poseen credenciales válidas.

### RN-035 Token de credencial

La credencial debe validarse con un token UUID aleatorio.

### RN-036 QR inválido

Si el token no existe o no es válido, debe mostrarse credencial inválida.

### RN-037 Datos visibles para comercio

El comercio solo debe ver:

- válida/inválida
- nombre y apellido
- tipo
- estado

No debe ver deuda ni datos sensibles.

---

## Asientos

### RN-038 Asiento por pago

Cada pago de cuota puede generar un asiento de ingreso.

### RN-039 Partidas contables

Todo asiento debe tener al menos dos partidas.

### RN-040 Balance contable

La suma del debe debe ser igual a la suma del haber.

### RN-041 Importe del asiento

El importe del asiento debe coincidir con el total balanceado de sus partidas.

### RN-042 Contabilidad simple

El MVP no implementa contabilidad completa.

---

# 8. Casos de uso MVP

## CU-001 Consultar sitio público

Actor: Visitante

Flujo principal:

1. Ingresa al sitio.
2. Consulta información institucional.
3. Consulta beneficios y comercios.

Modelos afectados:

- Beneficio
- Comercio
- BeneficioComercio

---

## CU-002 Ver credencial

Actor: Asociado

Flujo principal:

1. Inicia sesión.
2. Ingresa a Mi Credencial.
3. El sistema muestra credencial digital con QR.

Reglas relacionadas:

- RN-034
- RN-035

Modelos afectados:

- Asociado
- Usuario

---

## CU-003 Ver estado de cuotas

Actor: Asociado

Flujo principal:

1. Inicia sesión.
2. Ingresa a Mis Cuotas.
3. Visualiza cuotas pagadas, parciales, pendientes y vencidas.

Reglas relacionadas:

- RN-016
- RN-017
- RN-018

Modelos afectados:

- Cuota
- PeriodoCuota
- PagoCuota

---

## CU-004 Crear asociado

Actor: Administrador

Flujo principal:

1. Ingresa al panel de administración.
2. Carga datos personales.
3. Selecciona tipo: asociado o adherente.
4. Selecciona curso actual si corresponde.
5. Define fecha de alta.
6. El sistema calcula o permite definir fecha_inicio_cobro.
7. Guarda el asociado.
8. Si tiene curso, crea InscripcionCurso.

Reglas relacionadas:

- RN-001
- RN-005
- RN-006
- RN-007
- RN-013
- RN-014
- RN-015

Situaciones especiales:

- DNI duplicado.
- Curso inexistente.
- Alta después del día 15.
- Asociado sin usuario.

Modelos afectados:

- Asociado
- Curso
- InscripcionCurso

---

## CU-005 Importar asociados

Actor: Administrador

Flujo principal:

1. Sube archivo Excel/CSV.
2. El sistema valida columnas.
3. El sistema valida DNI, tipo y curso.
4. El sistema informa errores y advertencias.
5. El administrador confirma importación.
6. El sistema crea asociados e inscripciones.

Reglas relacionadas:

- RN-005
- RN-006
- RN-007
- RN-009
- RN-010

Situaciones especiales:

- DNI duplicado.
- Curso inexistente.
- Asociado ya existente.
- Email faltante.
- Teléfono faltante.
- Tipo inválido.

Modelos afectados:

- Asociado
- Curso
- InscripcionCurso

---

## CU-006 Crear usuario para asociado

Actor: Administrador

Flujo principal:

1. Busca asociado.
2. Verifica que no tenga usuario.
3. Presiona Crear usuario.
4. El sistema crea User.
5. El sistema vincula User con Asociado.
6. El sistema agrega al usuario al grupo Asociados.

Reglas relacionadas:

- RN-026
- RN-027
- RN-028
- RN-029

Situaciones especiales:

- Asociado ya posee usuario.
- DNI inexistente.
- Username duplicado.
- Email vacío.

Modelos afectados:

- User
- Asociado

---

## CU-007 Generar período de cuota

Actor: Administrador

Flujo principal:

1. Crea PeriodoCuota con mes, año, importe y vencimiento.
2. Ejecuta generación de cuotas.
3. El sistema genera cuotas para asociados activos alcanzados por fecha_inicio_cobro.
4. El sistema evita duplicados.

Reglas relacionadas:

- RN-004
- RN-016
- RN-017
- RN-019
- RN-020

Situaciones especiales:

- Asociado inactivo.
- Asociado egresado.
- Fecha de inicio de cobro posterior.
- Cuota ya generada.

Modelos afectados:

- PeriodoCuota
- Cuota
- Asociado

---

## CU-008 Registrar pago de cuota

Actor: Administrador

Flujo principal:

1. Busca asociado.
2. Visualiza deuda.
3. Ingresa importe y método.
4. El sistema aplica pago a la deuda más antigua.
5. El sistema actualiza importe_pagado y estado de cuotas.
6. El sistema crea PagoCuota.
7. El sistema puede generar Asiento.

Reglas relacionadas:

- RN-021
- RN-022
- RN-023
- RN-024
- RN-025
- RN-038

Situaciones especiales:

- Pago parcial.
- Pago exacto.
- Pago para múltiples cuotas.
- Pago mayor a deuda.
- Asociado sin deuda.

Modelos afectados:

- Pago
- PagoCuota
- Cuota
- Asiento

---

## CU-009 Dar de baja asociado

Actor: Administrador

Flujo principal:

1. Busca asociado.
2. Selecciona baja.
3. Carga fecha y motivo.
4. El sistema cambia estado a inactivo.
5. El sistema conserva cuotas, pagos e historial.

Reglas relacionadas:

- RN-003
- RN-004

Situaciones especiales:

- Baja con deuda.
- Baja sin deuda.
- Asociado con usuario.

Modelos afectados:

- Asociado

---

## CU-010 Marcar asociado como egresado

Actor: Administrador

Flujo principal:

1. Busca asociado.
2. Cambia estado a egresado.
3. El sistema conserva historial.
4. El sistema deja de generar nuevas cuotas.

Reglas relacionadas:

- RN-003
- RN-004

Modelos afectados:

- Asociado
- InscripcionCurso

---

## CU-011 Cambiar curso

Actor: Administrador

Flujo principal:

1. Busca asociado.
2. Selecciona nuevo curso y ciclo lectivo.
3. El sistema desactiva inscripción anterior si corresponde.
4. El sistema crea nueva InscripcionCurso.
5. El sistema actualiza curso_actual.

Reglas relacionadas:

- RN-009
- RN-010
- RN-011
- RN-012

Situaciones especiales:

- Promoción normal.
- Repite curso.
- Cambio de división.

Modelos afectados:

- Asociado
- Curso
- InscripcionCurso

---

## CU-012 Validar credencial

Actor: Comercio

Flujo principal:

1. Escanea QR o ingresa token.
2. El sistema busca asociado por token_credencial.
3. El sistema verifica estado.
4. Muestra resultado.

Reglas relacionadas:

- RN-031
- RN-033
- RN-034
- RN-035
- RN-036
- RN-037

Situaciones especiales:

- QR inválido.
- Asociado inactivo.
- Asociado egresado.
- Comercio inactivo.

Modelos afectados:

- Asociado
- Comercio

---

## CU-013 Gestionar comercio

Actor: Administrador

Flujo principal:

1. Crea o edita comercio.
2. Carga datos de contacto.
3. Carga dirección.
4. Opcionalmente carga latitud y longitud.
5. Activa o desactiva comercio.

Reglas relacionadas:

- RN-031
- RN-033

Modelos afectados:

- Comercio

---

## CU-014 Gestionar beneficio de comercio

Actor: Administrador

Flujo principal:

1. Selecciona comercio.
2. Crea beneficio.
3. Define título, descripción, condiciones, tipo y valor.
4. Define vigencia.
5. Activa beneficio.

Reglas relacionadas:

- RN-031
- RN-032

Situaciones especiales:

- Beneficio vencido.
- Beneficio futuro.
- Comercio inactivo.

Modelos afectados:

- Comercio
- BeneficioComercio

---

# 9. Casos borde y situaciones especiales

## CB-001 Alta a mitad de mes

Se resuelve con fecha_inicio_cobro.

- Alta antes del día 15: cobra mes actual.
- Alta después del día 15: cobra desde mes siguiente.
- El administrador puede ajustar fecha_inicio_cobro si corresponde.

## CB-002 Asociado sin usuario

Situación válida.

El asociado existe en el padrón, pero no puede iniciar sesión hasta que se cree un User vinculado.

## CB-003 Usuario desactivado

Puede existir asociado activo con usuario desactivado.

Esto bloquea acceso, pero no borra datos del asociado.

## CB-004 Cambio de curso

No se pisa historial.

Se crea una nueva InscripcionCurso.

## CB-005 Repite curso

Aunque el curso sea el mismo, se crea una nueva InscripcionCurso para el nuevo ciclo lectivo.

## CB-006 Baja con deuda

Permitida.

La deuda se conserva.

No se generan nuevas cuotas.

## CB-007 Egresado con deuda

Permitido.

La deuda se conserva.

No se generan nuevas cuotas.

## CB-008 Cuota ya generada

No generar duplicados.

## CB-009 Pago parcial

Permitido para cuotas.

Actualiza importe_pagado y estado parcial.

## CB-010 Pago mayor a deuda

No permitido en MVP.

No se maneja saldo a favor.

## CB-011 Asociado sin deuda

No debería permitirse registrar pago de cuota.

## CB-012 QR inválido

Mostrar credencial inválida.

## CB-013 Comercio inactivo

No puede validar credenciales.

## CB-014 Beneficio vencido

No se muestra públicamente.

## CB-015 Beneficio futuro

No se muestra hasta fecha_desde.

---

# 10. Reportes MVP

Reportes mínimos:

- Asociados activos.
- Asociados inactivos.
- Asociados egresados.
- Asociados por curso.
- Asociados por tipo.
- Asociados con usuario.
- Asociados sin usuario.
- Últimos accesos.
- Altas por mes.
- Bajas por mes.
- Cuotas generadas.
- Cuotas pagadas.
- Cuotas parciales.
- Cuotas vencidas.
- Deudores.
- Deudores por curso.
- Recaudación por período.
- Recaudación por método de pago.
- Comercios adheridos.
- Beneficios vigentes.

---

# 11. Pantallas MVP

## Sitio público

- Inicio.
- Beneficios.
- Comercios.
- Login.

## Asociado

- Panel.
- Mi credencial.
- Mis cuotas.
- Beneficios.
- Comercios adheridos.

## Administrador

- Dashboard.
- Listado de asociados.
- Nuevo asociado.
- Importar asociados.
- Detalle de asociado.
- Crear usuario para asociado.
- Cursos.
- Colegios.
- Períodos de cuota.
- Generar cuotas.
- Registrar pago.
- Deudores.
- Beneficios.
- Comercios.
- Beneficios de comercio.
- Reportes.

## Comercio

- Login.
- Validar credencial.
- Resultado de validación.

---

# 12. Diseño aprobado para Versión 2: pedidos, productos y stock

Este módulo queda fuera del MVP, pero el diseño queda aprobado para una segunda versión.

## Entidades V2

- Producto
- VarianteProducto
- MovimientoStock
- Pedido
- ItemPedido
- PagoPedido

---

## Producto

Representa un producto o servicio vendible.

Campos sugeridos:

- id
- nombre
- descripcion
- precio
- activo
- controla_stock

Ejemplos:

- Remera Uni2.
- Apunte Matemática.
- Cuadernillo Inglés.

---

## VarianteProducto

Representa variantes de un producto.

Campos sugeridos:

- id
- producto
- nombre
- sku
- activo

Ejemplos:

Producto: Remera Uni2

- Talle S
- Talle M
- Talle L
- Talle XL

Producto: Apunte Matemática

- Variante única

---

## MovimientoStock

Historial de movimientos de stock.

Campos sugeridos:

- id
- variante
- tipo
- cantidad
- fecha
- descripcion

Tipos:

- ingreso
- egreso
- ajuste
- devolucion

Decisión:

- El stock se descuenta al entregar el pedido.
- No se descuenta al crear pedido.
- No se descuenta al pagar pedido.

---

## Pedido

Representa una compra de un asociado.

Campos sugeridos:

- id
- asociado
- fecha
- estado
- estado_pago
- total
- observaciones

Estados de pedido:

- pendiente
- en_preparacion
- entregado
- cancelado

Estados de pago:

- pendiente
- pagado

Decisiones:

- No se permiten pagos parciales de pedidos en V2 inicial.
- No se entregan pedidos impagos.
- No se cancelan pedidos entregados.

---

## ItemPedido

Detalle de productos del pedido.

Campos sugeridos:

- id
- pedido
- variante
- cantidad
- precio_unitario
- subtotal

---

## PagoPedido

Aplicación de un pago a un pedido.

Campos sugeridos:

- id
- pago
- pedido
- importe

Relación futura:

- Pago 1 ─── N PagoCuota
- Pago 1 ─── N PagoPedido

Decisión:

- Se conserva un único modelo Pago para ingresos de dinero.
- PagoCuota explica qué cuota se pagó.
- PagoPedido explica qué pedido se pagó.

---

## Reglas V2

### RV2-001 Pedido sin stock

No se permite crear pedido si no hay stock suficiente.

### RV2-002 Descuento de stock

El stock se descuenta al entregar el pedido.

### RV2-003 Entrega de pedido

No se puede entregar un pedido impago.

### RV2-004 Pago parcial de pedido

No se permite pago parcial de pedidos en V2 inicial.

### RV2-005 Cancelación

No se puede cancelar un pedido entregado.

### RV2-006 Productos sin stock

Algunos productos pueden no controlar stock, por ejemplo apuntes digitales o servicios.

---

## Casos de uso V2

### CU-V2-001 Crear pedido

Actor: Asociado

Flujo:

1. Ingresa a productos.
2. Selecciona producto y variante.
3. Indica cantidad.
4. El sistema valida stock.
5. Confirma pedido.

### CU-V2-002 Registrar pago de pedido

Actor: Administrador

Flujo:

1. Busca pedido.
2. Registra pago completo.
3. El sistema marca pedido como pagado.
4. El sistema crea Pago y PagoPedido.

### CU-V2-003 Entregar pedido

Actor: Administrador

Flujo:

1. Busca pedido.
2. Verifica que esté pagado.
3. Marca como entregado.
4. El sistema descuenta stock.
5. El sistema crea MovimientoStock.

### CU-V2-004 Ver estado de pedidos

Actor: Asociado

Flujo:

1. Ingresa a Mis pedidos.
2. Consulta estado de pedido y pago.

---

## Reportes V2

- Pedidos pendientes.
- Pedidos pagados.
- Pedidos entregados.
- Ventas por producto.
- Stock actual.
- Movimientos de stock.

---

# 13. Roadmap

## MVP

- Asociados.
- Colegios.
- Cursos.
- Inscripciones de curso.
- Usuarios vinculados a asociados.
- Cuotas.
- Pagos de cuotas.
- Credenciales digitales.
- Comercios.
- Beneficios de comercios.
- Beneficios institucionales.
- Reportes básicos.
- Asientos simples.

## Versión 2

- Productos.
- Variantes.
- Pedidos.
- Items de pedido.
- PagoPedido.
- MovimientoStock.
- Reportes de ventas y stock.

## Versión 3

- PWA.
- Notificaciones push.
- Mapa de comercios.
- Pago online.
- Contabilidad completa.
- Tickets de consultas.
- Mensajería.
- Asambleas.
- Votaciones.

---

# 14. Prompt sugerido para Codex

Usar este documento como fuente de verdad.

Primer pedido recomendado:

```text
Tomá UNI2_MASTER_SPEC.md como fuente de verdad.

Generá la estructura inicial de un proyecto Django para el MVP de Uni2.

Crear:
- apps recomendadas
- modelos del MVP
- relaciones
- choices
- constraints
- métodos de negocio principales
- configuración básica del admin

No implementar todavía vistas ni frontend.
```
