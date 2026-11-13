"""Las 15 consultas (reportes) del aplicativo. 7 usan JOIN (requisito: al menos 6 de 10).
Son SELECT de solo lectura y se ejecutan sin parametros."""

CONSULTAS = [
    {"id": 1, "titulo": "Total de investigadores", "usa_join": False, "sql": """
SELECT COUNT(*) AS total_investigadores_unicos
FROM investigador"""},

    {"id": 2, "titulo": "Escuelas profesionales con más investigadores", "usa_join": False, "sql": """
SELECT escuela_profesional, COUNT(*) AS total_miembros
FROM investigador
GROUP BY escuela_profesional
ORDER BY total_miembros DESC"""},

    {"id": 3, "titulo": "Directorio de investigadores con datos personales", "usa_join": True, "sql": """
SELECT i.codigo_ucsm,
       CONCAT(p.apellido_paterno, ' ', p.apellido_materno, ', ', p.nombres) AS nombre_completo,
       p.dni, p.genero, i.correo_elec, i.n_celular, i.escuela_profesional
FROM investigador i
JOIN persona p ON i.dni = p.dni
ORDER BY nombre_completo"""},

    {"id": 4, "titulo": "Investigadores sin patentes asociadas", "usa_join": True, "sql": """
SELECT i.codigo_ucsm, p.nombres, p.apellido_paterno
FROM investigador i
JOIN persona p ON i.dni = p.dni
LEFT JOIN formato_investigador fi ON i.codigo_ucsm = fi.codigo_ucsm
LEFT JOIN formato_patente_investigador fpi ON fi.n_formato_inv = fpi.n_formato_inv
WHERE fpi.n_formato_pat IS NULL
ORDER BY p.apellido_paterno"""},

    {"id": 5, "titulo": "Evolución de publicaciones por año", "usa_join": False, "sql": """
SELECT publication_year, COUNT(*) AS total_publicaciones
FROM historico
GROUP BY publication_year
ORDER BY publication_year ASC"""},

    {"id": 6, "titulo": "Producción por tipo de documento", "usa_join": False, "sql": """
SELECT type, COUNT(*) AS cantidad
FROM historico
GROUP BY type
ORDER BY cantidad DESC"""},

    {"id": 7, "titulo": "Publicaciones recientes por fecha de creación", "usa_join": False, "sql": """
SELECT uuid, title, publication_year, create_date, portal_url
FROM historico
WHERE create_date IS NOT NULL
ORDER BY create_date DESC
LIMIT 10"""},

    {"id": 8, "titulo": "Publicaciones por idioma", "usa_join": False, "sql": """
SELECT language, COUNT(*) AS total
FROM historico
GROUP BY language
ORDER BY total DESC"""},

    {"id": 9, "titulo": "Reportes generados por coordinador", "usa_join": True, "sql": """
SELECT c.codigo_ucsm, p.nombres, p.apellido_paterno, COUNT(r.dia) AS total_reportes_emitidos
FROM coordinador_repositorios c
JOIN persona p ON c.dni = p.dni
LEFT JOIN reporte r ON c.codigo_ucsm = r.codigo_ucsm_coordinador
GROUP BY c.codigo_ucsm, p.nombres, p.apellido_paterno
ORDER BY c.codigo_ucsm"""},

    {"id": 10, "titulo": "Enlaces de cada publicación", "usa_join": True, "sql": """
SELECT h.title, l.link_type, l.url, l.description
FROM historico h
JOIN historico_links l ON h.uuid = l.uuid
ORDER BY h.title"""},

    {"id": 11, "titulo": "Investigadores asociados a cada ODS", "usa_join": False, "sql": """
SELECT ods, COUNT(*) AS total_asociaciones
FROM formato_inv_ods
GROUP BY ods
ORDER BY total_asociaciones DESC"""},

    {"id": 12, "titulo": "Patentes por país de registro y editorial", "usa_join": False, "sql": """
SELECT pais, editorial, COUNT(*) AS total_patentes
FROM patente
GROUP BY pais, editorial
ORDER BY total_patentes DESC"""},

    {"id": 13, "titulo": "Investigadores con sus ODS vinculados", "usa_join": True, "sql": """
SELECT i.codigo_ucsm,
       p.apellido_paterno || ' ' || p.apellido_materno || ', ' || p.nombres AS investigador,
       i.escuela_profesional,
       string_agg(o.ods, ' | ' ORDER BY o.ods) AS ods_vinculados
FROM investigador i
JOIN persona p ON p.dni = i.dni
JOIN formato_investigador fi ON fi.codigo_ucsm = i.codigo_ucsm
JOIN formato_inv_ods o ON o.n_formato_inv = fi.n_formato_inv
GROUP BY i.codigo_ucsm, p.apellido_paterno, p.apellido_materno, p.nombres, i.escuela_profesional
ORDER BY investigador"""},

    {"id": 14, "titulo": "Patentes con sus inventores registrados", "usa_join": True, "sql": """
SELECT pa.n_patente, pa.titulo_patente, pa.pais,
       p.apellido_paterno || ' ' || p.apellido_materno || ', ' || p.nombres AS inventor,
       i.escuela_profesional
FROM patente pa
JOIN formato_patente fp ON fp.n_patente = pa.n_patente
JOIN formato_patente_investigador fpi ON fpi.n_formato_pat = fp.n_formato_pat
JOIN formato_investigador fi ON fi.n_formato_inv = fpi.n_formato_inv
JOIN investigador i ON i.codigo_ucsm = fi.codigo_ucsm
JOIN persona p ON p.dni = i.dni
ORDER BY pa.fecha_registro DESC, pa.n_patente"""},

    {"id": 15, "titulo": "Formatos de investigador y coordinador que los valida", "usa_join": True, "sql": """
SELECT fi.n_formato_inv,
       pinv.apellido_paterno || ' ' || pinv.apellido_materno || ', ' || pinv.nombres AS investigador,
       pcoo.apellido_paterno || ' ' || pcoo.apellido_materno || ', ' || pcoo.nombres AS coordinador_validador,
       c.funcion
FROM formato_investigador fi
JOIN investigador i ON i.codigo_ucsm = fi.codigo_ucsm
JOIN persona pinv ON pinv.dni = i.dni
JOIN coordinador_repositorios c ON c.codigo_ucsm = fi.codigo_ucsm_coordinador
JOIN persona pcoo ON pcoo.dni = c.dni
ORDER BY coordinador_validador, investigador"""},
]