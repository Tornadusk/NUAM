//// ========= ENUMS =========
Enum TipoDocumento {
  RUT        // Chile
  DNI        // Perú
  CC         // Colombia (Cédula de Ciudadanía)
  CE         // Cédula/Carné de Extranjería
  PASAPORTE
}

Enum EstadoCorredora {
  activa
  inactiva
}

Enum EstadoUsuario {
  activo
  bloqueado
}

Enum EstadoCalificacion {
  borrador
  validada
  publicada
  pendiente
}

Enum TipoCarga {
  manual
  masiva
}

Enum EstadoCarga {
  validando
  importando
  reconciliando
  done
  failed
}

Enum EstadoLinea {
  ok
  rechazo
}

Enum TipoValorFactor {
  factor
  monto
  tasa
}

Enum EntidadAuditoria {
  CALIFICACION
  CARGA
  CARGA_DETALLE
  INSTRUMENTO
  USUARIO
  OTRA
}

//// ========= TABLAS NUEVAS (con ID + código único) =========
Table pais {
  id_pais int [pk, increment]
  codigo char(3) [unique, not null]            // ISO-3166-1 alpha-3: CHL, PER, COL
  nombre varchar(100) [not null]
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]
}

Table moneda {
  id_moneda int [pk, increment]
  codigo char(3) [unique, not null]            // ISO-4217: CLP, PEN, COP, USD
  nombre varchar(60) [not null]
  decimales smallint [not null, default: 2]    // p.ej., CLP=0
  vigente boolean [not null, default: true]
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]
}

Table moneda_pais {
  id_moneda_pais int [pk, increment]
  id_moneda int [ref: > moneda.id_moneda]      // FK robusta (antes codigo_moneda)
  id_pais   int [ref: > pais.id_pais]          // FK robusta (antes codigo_pais)
  vigente_desde date
  vigente_hasta date
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_moneda, id_pais) [unique]
    (id_pais)
  }
}

//// ========= TABLAS EXISTENTES (con mínimos ajustes NUAM) =========
Table corredora {
  id_corredora int [pk, increment]
  nombre varchar(150) [not null]
  estado EstadoCorredora [not null, default: 'activa']
  id_pais int [ref: > pais.id_pais]            // país de domicilio (ISO vive en pais.codigo)
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes { (id_pais) }
}
Table persona {
  id_persona int [pk, increment]
  primer_nombre varchar(80) [not null]
  segundo_nombre varchar(80)                  // opcional
  apellido_paterno varchar(80) [not null]
  apellido_materno varchar(80)                // opcional
  genero varchar(30)                          // opcional
  fecha_nacimiento date [not null]            // para validar mayoría de edad
  nacionalidad char(3)                        // ISO-3166-1 alpha-3 (opcional)
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]
}

Table usuario {
  id_usuario   int [pk, increment]
  id_persona   int [ref: > persona.id_persona]
  username     varchar(60) [unique, not null]
  hash_password varchar(255)
  estado       EstadoUsuario [default: 'activo']
  creado_en    timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_persona)
  }
}

Table rol {
  id_rol int [pk, increment]
  nombre varchar(50) [unique, not null]
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]
}

Table usuario_rol {
  id bigint [pk, increment]
  id_usuario int [ref: > usuario.id_usuario]
  id_rol int [ref: > rol.id_rol]
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_usuario, id_rol) [unique]
    (id_rol)
  }
}

Table mercado {
  id_mercado int [pk, increment]
  codigo varchar(30) [unique, not null]
  nombre varchar(120) [not null]
  id_pais int [ref: > pais.id_pais]            // país del mercado
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes { (id_pais) }
}


Table instrumento {
  id_instrumento int [pk, increment]
  id_mercado int [ref: > mercado.id_mercado]
  codigo varchar(60) [unique, not null]
  nombre varchar(150) [not null]
  tipo varchar(60)
  emisor varchar(100)
  id_moneda int [ref: > moneda.id_moneda]      // FK robusta (reemplaza moneda char(3))
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_mercado)
    (id_moneda)
  }
}

Table fuente {
  id_fuente int [pk, increment]
  codigo varchar(30) [unique, not null]
  nombre varchar(80) [not null]
  descripcion text
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]
}

Table evento_capital {
  id_evento int [pk, increment]
  id_instrumento int [ref: > instrumento.id_instrumento]
  secuencia_evento varchar(40) [not null]
  fecha_pago date
  descripcion text
  valor_historico decimal(20,8)
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_instrumento)
    (id_instrumento, secuencia_evento) [unique]
  }
}

Table calificacion {
  id_calificacion  bigint [pk, increment]
  id_corredora     int    [ref: > corredora.id_corredora]
  id_instrumento   int    [ref: > instrumento.id_instrumento]
  id_fuente        int    [ref: > fuente.id_fuente]
  id_evento        int    [ref: > evento_capital.id_evento] // opcional
  ejercicio        int
  fecha_pago       date
  descripcion      text
  secuencia_evento varchar(40)
  factor_actualizacion decimal(20,8)
  valor_historico  decimal(20,8)
  ingreso_por_montos boolean
  acogido_sfut     boolean
  estado           EstadoCalificacion [default: 'borrador']
  observaciones    text
  id_moneda        int [ref: > moneda.id_moneda]  // “foto” de moneda al momento de la calificación
  creado_por       int [ref: > usuario.id_usuario]
  actualizado_por  int [ref: > usuario.id_usuario]
  creado_en        timestamp [default: `now()`]
  actualizado_en   timestamp [default: `now()`]

  indexes {
    (id_instrumento)
    (id_corredora)
    (id_fuente)
    (id_evento)
    (id_corredora, id_instrumento, ejercicio, secuencia_evento) [unique]
  }
}

Table factor_def {
  id_factor int [pk, increment]
  codigo_factor varchar(10) [unique, not null]
  nombre_corto varchar(40) [not null]
  descripcion text
  tipo_valor TipoValorFactor [default: 'factor']
  orden_visual int
  aplica_en_suma boolean [default: false]
  vigente_desde date
  vigente_hasta date
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]
}

Table calificacion_monto_detalle {
  id bigint [pk, increment]
  id_calificacion bigint [ref: > calificacion.id_calificacion]
  id_factor int [ref: > factor_def.id_factor]
  valor_monto decimal(20,8)
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_calificacion)
    (id_factor)
    (id_calificacion, id_factor) [unique]
  }
}

Table calificacion_factor_detalle {
  id bigint [pk, increment]
  id_calificacion bigint [ref: > calificacion.id_calificacion]
  id_factor int [ref: > factor_def.id_factor]
  valor_factor decimal(20,8)
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_calificacion)
    (id_factor)
    (id_calificacion, id_factor) [unique]
  }
}

Table carga {
  id_carga bigint [pk, increment]
  id_corredora int [ref: > corredora.id_corredora]
  creado_por int [ref: > usuario.id_usuario]
  id_fuente int [ref: > fuente.id_fuente]
  tipo TipoCarga
  nombre_archivo varchar(255)
  filas_total int
  insertados int
  actualizados int
  rechazados int
  estado EstadoCarga
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_corredora)
    (id_fuente)
    (creado_por)
  }
}

Table carga_detalle {
  id_detalle bigint [pk, increment]
  id_carga bigint [ref: > carga.id_carga]
  linea int
  estado_linea EstadoLinea
  mensaje_error text
  id_calificacion bigint [ref: > calificacion.id_calificacion] // opcional
  hash_linea varchar(64)
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_carga)
    (id_carga, linea) [unique]
    (id_carga, hash_linea) [unique]
  }
}

Table homologacion_campo {
  id_homologacion int [pk, increment]
  origen varchar(10)
  certificado varchar(10)
  campo_origen varchar(120)
  campo_destino varchar(120)
  transform varchar(200)
  obligatorio boolean
  vigente_desde date
  vigente_hasta date
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]
}

Table auditoria {
  id_auditoria bigint [pk, increment]
  actor_id int [ref: > usuario.id_usuario]
  entidad EntidadAuditoria
  entidad_id bigint
  accion varchar(20)
  fecha timestamp [default: `now()`]
  fuente varchar(50)
  valores_antes json
  valores_despues json
  creado_en timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (actor_id)
  }
}

//// ========= NUEVO: M:N usuario <-> corredora =========
Table usuario_corredora {
  id            bigint [pk, increment]                 
  id_usuario    int    [ref: > usuario.id_usuario]
  id_corredora  int    [ref: > corredora.id_corredora]
  es_principal  boolean [default: false]
  creado_en     timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (id_usuario, id_corredora) [unique]               // evita duplicar la relación
    (id_usuario)
    (id_corredora)
  }
}
//// ========= NUEVO: identificador fiscal por país (RUT/RUC/NIT) =========
Table corredora_identificador {
  id           int [pk, increment]
  id_corredora int [ref: > corredora.id_corredora]
  tipo         varchar(10) [not null]          // 'RUT' | 'RUC' | 'NIT'
  numero       varchar(30)  [not null]         // normalizado (sin puntos)
  id_pais      int [ref: > pais.id_pais, not null] // país que emite el identificador
  es_principal boolean [not null, default: true]
  creado_en    timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]

  indexes {
    (tipo, numero, id_pais) [unique]
    (id_corredora)
  }
}

Table colaborador {
  id_colaborador int [pk, increment]
  id_usuario     int [ref: > usuario.id_usuario, not null, unique]  // 1:1 con usuario
  gmail          varchar(254) [not null, unique]                     // Gmail corporativo
  creado_en      timestamp [default: `now()`]
  actualizado_en timestamp [default: `now()`]
}

// ========= OPCIONAL: REFS EXPLÍCITOS (actualizadas a ID) =========
 // Core usuario/roles
// Ref: usuario.id_persona > persona.id_persona [delete: restrict, update: restrict]
// Ref: usuario_rol.id_usuario > usuario.id_usuario [delete: cascade, update: restrict]
// Ref: usuario_rol.id_rol > rol.id_rol [delete: restrict, update: restrict]
// Ref: usuario_corredora.id_usuario > usuario.id_usuario [delete: cascade, update: restrict]
// Ref: usuario_corredora.id_corredora > corredora.id_corredora [delete: restrict, update: restrict]

 // País / Moneda por ID
// Ref: corredora.id_pais > pais.id_pais [delete: restrict, update: restrict]
// Ref: mercado.id_pais > pais.id_pais [delete: restrict, update: restrict]
// Ref: instrumento.id_moneda > moneda.id_moneda [delete: restrict, update: restrict]
// Ref: moneda_pais.id_moneda > moneda.id_moneda [delete: cascade, update: restrict]
// Ref: moneda_pais.id_pais > pais.id_pais [delete: cascade, update: restrict]

 // Identificadores de corredora por ID de país
// Ref: corredora_identificador.id_corredora > corredora.id_corredora [delete: cascade, update: restrict]
// Ref: corredora_identificador.id_pais > pais.id_pais [delete: restrict, update: restrict]

 // Mercado / Instrumento / Eventos
// Ref: instrumento.id_mercado > mercado.id_mercado [delete: restrict, update: restrict]
// Ref: evento_capital.id_instrumento > instrumento.id_instrumento [delete: cascade, update: restrict]

 // Calificaciones
// Ref: calificacion.id_corredora > corredora.id_corredora [delete: restrict, update: restrict]
// Ref: calificacion.id_instrumento > instrumento.id_instrumento [delete: restrict, update: restrict]
// Ref: calificacion.id_fuente > fuente.id_fuente [delete: restrict, update: restrict]
// Ref: calificacion.id_evento > evento_capital.id_evento [delete: set null, update: restrict]
// Ref: calificacion.id_moneda > moneda.id_moneda [delete: restrict, update: restrict]   // “foto” de moneda
// Ref: calificacion.creado_por > usuario.id_usuario [delete: restrict, update: restrict]
// Ref: calificacion.actualizado_por > usuario.id_usuario [delete: restrict, update: restrict]

 // Factores / Detalles
// Ref: calificacion_monto_detalle.id_calificacion > calificacion.id_calificacion [delete: cascade, update: restrict]
// Ref: calificacion_monto_detalle.id_factor > factor_def.id_factor [delete: restrict, update: restrict]
// Ref: calificacion_factor_detalle.id_calificacion > calificacion.id_calificacion [delete: cascade, update: restrict]
// Ref: calificacion_factor_detalle.id_factor > factor_def.id_factor [delete: restrict, update: restrict]

 // Cargas
// Ref: carga.id_corredora > corredora.id_corredora [delete: restrict, update: restrict]
// Ref: carga.creado_por > usuario.id_usuario [delete: restrict, update: restrict]
// Ref: carga.id_fuente > fuente.id_fuente [delete: restrict, update: restrict]
// Ref: carga_detalle.id_carga > carga.id_carga [delete: cascade, update: restrict]
// Ref: carga_detalle.id_calificacion > calificacion.id_calificacion [delete: set null, update: restrict]
