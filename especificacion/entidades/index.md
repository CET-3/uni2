# Entidades

* [Usuario](usuario.md) - Usuario de autenticación de Django. Se recomienda usar el sistema estandar inicialmente.
* [CicloLectivo](ciclo-lectivo.md) - Representa un año lectivo. Se usa como referencia en inscripciones y períodos de cuota.
* [Curso](curso.md) - Representa un curso comisión de la escuela.
* [Asociado](asociado.md) - Representa a una persona asociada o adherente a la mutual.
* [SolicitudAsociacion](solicitud-asociacion.md) - Preinscripción pública separada del padrón hasta completar el alta presencial.
* [LimiteSolicitudPublica](limite-solicitud-publica.md) - Contador técnico compartido para limitar acciones públicas sin guardar la dirección o token crudos.
* [ClasificacionAdherente](clasificacion-adherente.md) - Clasifica la relación institucional de una persona adherente.
* [PeríodoCuota](periodo-cuota.md) - Representa un período mensual de cuota.
* [Cuota](cuota.md) - Representa una cuota concreta de un asociado para un período.
* [Pago](pago.md) - Representa un ingreso de dinero.
* [PagoCuota](pago-cuota.md) - Aplicación de un pago a una cuota.
* [Donacion](donacion.md) - Registra el excedente voluntario recibido en un cobro.
* [CategoriaProductoServicio](categoria-producto-servicio.md) - Agrupa productos y servicios publicados por la mutual.
* [ProductoServicio](producto-servicio.md) - Representa un producto o servicio publicado por la mutual.
* [Publicidad](publicidad.md) - Card destacada con foto para la home pública.
* [ActividadComercial](actividad-comercial.md) - Clasifica el rubro o actividad principal de un comercio adherido.
* [Comercio](comercio.md) - Comercio adherido a la mutual.
* [EstadoDatosStaging](estado-datos-staging.md) - Marcador técnico que habilita una copia endurecida en staging.
* [EventoAuditoria](evento-auditoria.md) - Hecho inmutable que identifica una operación y los cambios producidos sobre una entidad.
* [Comunicacion](comunicacion.md) - Mensaje lógico originado por un hecho de negocio.
* [EntregaComunicacion](entrega-comunicacion.md) - Intento de entrega de una comunicación mediante un canal.
