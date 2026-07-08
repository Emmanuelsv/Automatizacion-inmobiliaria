SAMPLE_MESSAGES = [
    {
        "id": "solicitud_completa",
        "text": """Solicitud de Propiedad – Apartamento 🏡
📍 Ubicación deseada: Loma del Chocho, El Campestre, Zúñiga, Santa María de Los Ángeles, El Esmeraldal, Escobero, Loma de Los Balsos hasta San Lucas
💰 Presupuesto máximo: $700.000.000
💳 Modo de pago: Crédito hipotecario aprobado + fondo de pensiones voluntario
🔑 Características:
\t•\tÁrea desde 80 m² en adelante
\t•\tMínimo 2 habitaciones
\t•\tAdministración máximo $600.000
\t•\tSin registro
\t• piso alto con buena vista

👩‍💼 Cliente: Valentina Carvajal
👨‍💼 Asesor: Emmanuel Sanchez
📱 Contacto: 3021222188
MYE Inmobiliaria 🏡""",
        "expected": {
            "es_solicitud": True,
            "tipo_inmueble": ["Apartamento"],
            "presupuesto_exact": 700_000_000,
            "habitaciones_min": 2,
            "area_min": 80,
            "administracion_max": 600_000,
            "asesor": "Emmanuel Sanchez",
            "cliente": "Valentina Carvajal",
            "telefono": "3021222188",
            "min_barrios": 6,
        },
    },
    {
        "id": "solicitud_corta",
        "text": """Busco casa en El Poblado o Laureles
Presupuesto: 500 millones
3 habitaciones mínimo
Asesor: Carlos Pérez
Cel: 3107654321""",
        "expected": {
            "es_solicitud": True,
            "tipo_inmueble": ["Casa"],
            "presupuesto_exact": 500_000_000,
            "habitaciones_min": 3,
            "asesor": "Carlos Pérez",
            "telefono": "3107654321",
            "min_barrios": 2,
        },
    },
    {
        "id": "no_solicitud",
        "text": "Buenos días grupo, ¿alguien sabe si hay disponibilidad en el edificio Torres del Este?",
        "expected": {
            "es_solicitud": False,
        },
    },
    {
        "id": "solicitud_informal",
        "text": """Necesito un apto en Sabaneta, por Aves María o Calle Larga
Máximo 400M
2 hab, 60m² mínimo
Contacto: 3001234567
Asesor: María López""",
        "expected": {
            "es_solicitud": True,
            "tipo_inmueble": ["Apartamento"],
            "presupuesto_exact": 400_000_000,
            "habitaciones_min": 2,
            "area_min": 60,
            "telefono": "3001234567",
            "min_barrios": 2,
        },
    },
    {
        "id": "solicitud_con_apostrofe",
        "text": """Solicitud de Propiedad – Apartamento
Ubicación: Laureles, Estadio
Presupuesto: $850'000.000
Área mínima 100 m²
3 habitaciones
Administración máximo $800.000
Asesor: Pedro Martínez
Contacto: 3209876543
MYE Inmobiliaria""",
        "expected": {
            "es_solicitud": True,
            "tipo_inmueble": ["Apartamento"],
            "presupuesto_exact": 850_000_000,
            "habitaciones_min": 3,
            "area_min": 100,
            "administracion_max": 800_000,
            "telefono": "3209876543",
            "min_barrios": 2,
        },
    },
]
