# Ciudades válidas del área metropolitana de Medellín
CIUDADES: dict[str, str] = {
    "medellin": "Medellín",
    "envigado": "Envigado",
    "sabaneta": "Sabaneta",
    "bello": "Bello",
    "itagui": "Itagüí",
    "la estrella": "La Estrella",
    "caldas": "Caldas",
    "copacabana": "Copacabana",
}

ALIAS_CIUDADES: dict[str, str] = {
    "med": "Medellín",
    "mede": "Medellín",
    "medallo": "Medellín",
    "medellin": "Medellín",
    "envigado": "Envigado",
    "saba": "Sabaneta",
    "sabaneta": "Sabaneta",
    "itag": "Itagüí",
    "itagüí": "Itagüí",
    "itagui": "Itagüí",
    "la estrella": "La Estrella",
    "estrella": "La Estrella",
    "bello": "Bello",
    "caldas": "Caldas",
    "copa": "Copacabana",
    "copacabana": "Copacabana",
}

# Barrios/sectores mapeados a su ciudad.
# NOTA: Esta lista es INICIAL. Ampliar con todos los barrios que maneja Jhaen Inmobiliarios.
BARRIOS: dict[str, dict[str, str]] = {
        # === ENVIGADO ===
    # =========================================
    # ENVIGADO - SEPARADO POR SECTORES
    # =========================================
# =========================================
    # PUNTOS DE INTERÉS / HITOS URBANOS (POIs)
    # =========================================
    "viva envigado": {"nombre": "viva envigado", "ciudad": "Envigado"},
    "exito envigado": {"nombre": "viva envigado", "ciudad": "Envigado"},
    "exito de envigado": {"nombre": "viva envigado", "ciudad": "Envigado"},
    "cc viva envigado": {"nombre": "viva envigado", "ciudad": "Envigado"},
    "centro comercial viva envigado": {"nombre": "viva envigado", "ciudad": "Envigado"},
    
    "viva palmas": {"nombre": "Alto de Las Palmas", "ciudad": "Envigado"},
    "cc viva palmas": {"nombre": "Alto de Las Palmas", "ciudad": "Envigado"},
    "centro comercial viva palmas": {"nombre": "Alto de Las Palmas", "ciudad": "Envigado"},

    

    # =========================================
    # ENVIGADO POR ZONA (ALTA / BAJA)
    # Conceptos amplios que se expanden a barrios reales en matcher.py
    # =========================================

    # Envigado parte alta / zona de loma
    "envigado alto": {"nombre": "envigado alto", "ciudad": "Envigado"},
    "envigado parte alta": {"nombre": "envigado alto", "ciudad": "Envigado"},
    "parte alta de envigado": {"nombre": "envigado alto", "ciudad": "Envigado"},
    "parte alta envigado": {"nombre": "envigado alto", "ciudad": "Envigado"},
    "zona alta de envigado": {"nombre": "envigado alto", "ciudad": "Envigado"},
    "zona alta envigado": {"nombre": "envigado alto", "ciudad": "Envigado"},
    "envigado zona alta": {"nombre": "envigado alto", "ciudad": "Envigado"},
    "sector alto de envigado": {"nombre": "envigado alto", "ciudad": "Envigado"},
    "loma de envigado": {"nombre": "envigado alto", "ciudad": "Envigado"},
    "lomas de envigado": {"nombre": "envigado alto", "ciudad": "Envigado"},

    # Envigado parte baja / zona plana
    "envigado bajo": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "envigado parte baja": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "parte baja de envigado": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "parte baja envigado": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "zona baja de envigado": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "zona baja envigado": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "envigado zona baja": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "envigado parte plana": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "parte plana de envigado": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "parte plana envigado": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "zona plana de envigado": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "zona plana envigado": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "envigado zona plana": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "sector plano de envigado": {"nombre": "envigado bajo", "ciudad": "Envigado"},
    "envigado plano": {"nombre": "envigado bajo", "ciudad": "Envigado"},

    # Envigado zona centro 
    "envigado centro": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "centro de envigado": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "zona centro de envigado": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "centro envigado": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "envigado zona centro": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "parte centro de envigado": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "parte centro envigado": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "sector centro de envigado": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "Envigado parte centro": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "Envigado parte central": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "zona central de envigado": {"nombre": "envigado centro", "ciudad": "Envigado"},
    "Envigado central": {"nombre": "envigado centro", "ciudad": "Envigado"},



    # =========================================
    # SECTOR: FRONTERA / ZÚÑIGA / ABAJO
    # =========================================

    "zuñiga": {"nombre": "Zúñiga", "ciudad": "Envigado"},
    "zuniga": {"nombre": "Zúñiga", "ciudad": "Envigado"},
    "zúñiga": {"nombre": "Zúñiga", "ciudad": "Envigado"},

    "la frontera": {"nombre": "La Frontera", "ciudad": "Envigado"},
    "frontera": {"nombre": "La Frontera", "ciudad": "Envigado"},
    "el portal": {"nombre": "El Portal", "ciudad": "Envigado"},
    "el dorado": {"nombre": "El Dorado", "ciudad": "Envigado"},
    "otra parte": {"nombre": "Otra Parte", "ciudad": "Envigado"},
    "otraparte": {"nombre": "Otra Parte", "ciudad": "Envigado"},

    "el campestre": {"nombre": "El Campestre", "ciudad": "Envigado"},
    "campestre": {"nombre": "El Campestre", "ciudad": "Envigado"},

    "santa maria de los angeles": {"nombre": "Santa María de Los Ángeles", "ciudad": "Envigado"},
    "santa maria": {"nombre": "Santa María de Los Ángeles", "ciudad": "Envigado"},
    "los angeles": {"nombre": "Santa María de Los Ángeles", "ciudad": "Envigado"},


    # =========================================
    # SECTOR: INTERMEDIO / RESIDENCIAL
    # =========================================

    "la abadia": {"nombre": "La Abadía", "ciudad": "Envigado"},
    "abadia": {"nombre": "La Abadía", "ciudad": "Envigado"},
    "la abadía": {"nombre": "La Abadía", "ciudad": "Envigado"},
    "abadía": {"nombre": "La Abadía", "ciudad": "Envigado"},

    "las orquideas": {"nombre": "Las Orquídeas", "ciudad": "Envigado"},
    "orquideas": {"nombre": "Las Orquídeas", "ciudad": "Envigado"},
    "las orquídeas": {"nombre": "Las Orquídeas", "ciudad": "Envigado"},
    "orquídeas": {"nombre": "Las Orquídeas", "ciudad": "Envigado"},
    "la intermedia": {"nombre": "La Intermedia", "ciudad": "Envigado"},
    "intermedia": {"nombre": "La Intermedia", "ciudad": "Envigado"},

    "la calleja": {"nombre": "La Calleja", "ciudad": "Envigado"},
    "calleja": {"nombre": "La Calleja", "ciudad": "Envigado"},
    "las callejas": {"nombre": "La Calleja", "ciudad": "Envigado"},
    "las antillas": {"nombre": "Las Antillas", "ciudad": "Envigado"},
    "la paz": {"nombre": "La Paz", "ciudad": "Envigado"},
    "la sebastiana": {"nombre": "La Sebastiana", "ciudad": "Envigado"},
    "alcala": {"nombre": "Alcalá", "ciudad": "Envigado"},
    "alcalá": {"nombre": "Alcalá", "ciudad": "Envigado"},
    "jardin": {"nombre": "Jardines", "ciudad": "Envigado"},
    "jardin de envigado": {"nombre": "Jardines", "ciudad": "Envigado"},
    "jardines": {"nombre": "Jardines", "ciudad": "Envigado"},
    "san marcos": {"nombre": "San Marcos", "ciudad": "Envigado"},
    "mesa": {"nombre": "Mesa", "ciudad": "Envigado"},
    "loma de los mesa": {"nombre": "Mesa", "ciudad": "Envigado"},
    "centro": {"nombre": "Centro", "ciudad": "Medellín"},
    "la magnolia": {"nombre": "La Magnolia", "ciudad": "Envigado"},
    "magnolia": {"nombre": "La Magnolia", "ciudad": "Envigado"},



    # =========================================
    # SECTOR: LOMA DEL CHOCHO / ESMERALDAL
    # =========================================

    "loma del chocho": {"nombre": "Loma del Chocho", "ciudad": "Envigado"},
    "el chocho": {"nombre": "Loma del Chocho", "ciudad": "Envigado"},

    "el esmeraldal": {"nombre": "El Esmeraldal", "ciudad": "Envigado"},
    "loma del esmeraldal": {"nombre": "El Esmeraldal", "ciudad": "Envigado"},
    "esmeraldal": {"nombre": "El Esmeraldal", "ciudad": "Envigado"},
    "esmeraldaln": {"nombre": "El Esmeraldal", "ciudad": "Envigado"},

    "loma de los yarumos": {"nombre": "Loma de los Yarumos", "ciudad": "Envigado"},
    "yarumos": {"nombre": "Loma de los Yarumos", "ciudad": "Envigado"},
    "loma de los balsos": {"nombre": "Loma de Los Balsos", "ciudad": "Envigado"},
    "los balsos": {"nombre": "Loma de Los Balsos", "ciudad": "Envigado"},
    "balsos": {"nombre": "Loma de Los Balsos", "ciudad": "Envigado"},


    # =========================================
    # SECTOR: LOMA DE LAS BRUJAS
    # =========================================

    "las brujas": {"nombre": "Las Brujas", "ciudad": "Envigado"},
    "loma de las brujas": {"nombre": "Las Brujas", "ciudad": "Envigado"},
    "loma de brujas": {"nombre": "Las Brujas", "ciudad": "Envigado"},

    "loma del atravesado": {"nombre": "Loma del Atravesado", "ciudad": "Envigado"},
    "atravesado": {"nombre": "Loma del Atravesado", "ciudad": "Envigado"},


    # =========================================
    # SECTOR: ESCOBERO / ALTA MONTAÑA
    # =========================================

    "escobero": {"nombre": "Escobero", "ciudad": "Envigado"},
    "el escobero": {"nombre": "Escobero", "ciudad": "Envigado"},
    "loma del escobero": {"nombre": "Escobero", "ciudad": "Envigado"},

    "el salado": {"nombre": "El Salado", "ciudad": "Envigado"},
    "salado": {"nombre": "El Salado", "ciudad": "Envigado"},

    "las palmas envigado": {"nombre": "Alto de Las Palmas", "ciudad": "Envigado"},
    "palmas envigado": {"nombre": "Alto de Las Palmas", "ciudad": "Envigado"},
    "alto de palmas": {"nombre": "Alto de Las Palmas", "ciudad": "Envigado"},
    "alto de las palmas": {"nombre": "Alto de Las Palmas", "ciudad": "Envigado"},


    # =========================================
    # SECTOR: ADICIONALES IMPORTANTES
    # =========================================

    "loma del barro": {"nombre": "Loma del Barro", "ciudad": "Envigado"},
    "barro": {"nombre": "Loma del Barro", "ciudad": "Envigado"},

    "cumbres": {"nombre": "Cumbres", "ciudad": "Envigado"},
    "las cumbres": {"nombre": "Cumbres", "ciudad": "Envigado"},

    "la cuenca": {"nombre": "La Cuenca", "ciudad": "Envigado"},
    "cuenca": {"nombre": "La Cuenca", "ciudad": "Envigado"},

    "milan": {"nombre": "Milán", "ciudad": "Envigado"},
    "milán": {"nombre": "Milán", "ciudad": "Envigado"},

    "pontevedra": {"nombre": "Pontevedra", "ciudad": "Envigado"},
    "san jose": {"nombre": "San José", "ciudad": "Envigado"},
    "san josé": {"nombre": "San José", "ciudad": "Envigado"},

    # =========================================
    # MEDELLÍN - ZONA SUR SEPARADA POR SECTORES
    # =========================================


    # =========================================
    # SECTOR: EL POBLADO
    # =========================================

    "el poblado": {"nombre": "El Poblado", "ciudad": "Medellín"},
    "poblado": {"nombre": "El Poblado", "ciudad": "Medellín"},

    # Poblado por zona (alto/bajo)
    "poblado alto": {"nombre": "Poblado Alto", "ciudad": "Medellín"},
    "zona alta del poblado": {"nombre": "Poblado Alto", "ciudad": "Medellín"},
    "poblado zona alta": {"nombre": "Poblado Alto", "ciudad": "Medellín"},
    "sector alto del poblado": {"nombre": "Poblado Alto", "ciudad": "Medellín"},

    "poblado bajo": {"nombre": "Poblado Bajo", "ciudad": "Medellín"},
    "poblado no muy alto": {"nombre": "Poblado Bajo", "ciudad": "Medellín"},
    "poblado que no sea alto": {"nombre": "Poblado Bajo", "ciudad": "Medellín"},
    "zona baja del poblado": {"nombre": "Poblado Bajo", "ciudad": "Medellín"},
    "poblado zona baja": {"nombre": "Poblado Bajo", "ciudad": "Medellín"},
    "zona plana del poblado": {"nombre": "Poblado Bajo", "ciudad": "Medellín"},
    "poblado zona plana": {"nombre": "Poblado Bajo", "ciudad": "Medellín"},
    "sector plano del poblado": {"nombre": "Poblado Bajo", "ciudad": "Medellín"},

    "vizcaya": {"nombre": "Vizcaya", "ciudad": "Medellín"},
    "san lucas": {"nombre": "San Lucas", "ciudad": "Medellín"},
    "castropol": {"nombre": "Castropol", "ciudad": "Medellín"},
    "manila": {"nombre": "Manila", "ciudad": "Medellín"},
    "patio bonito": {"nombre": "Patio Bonito", "ciudad": "Medellín"},
    "las palmas": {"nombre": "Las Palmas", "ciudad": "Medellín"},
    "palmas": {"nombre": "Las Palmas", "ciudad": "Medellín"},
    "el tesoro": {"nombre": "El Tesoro", "ciudad": "Medellín"},
    "loma del indio": {"nombre": "Loma del Indio", "ciudad": "Medellín"},
    "la calera": {"nombre": "La Calera", "ciudad": "Medellín"},
    "santa fe": {"nombre": "Santa Fe", "ciudad": "Medellín"},
    "provenza": {"nombre": "Provenza", "ciudad": "Medellín"},
    "astorga": {"nombre": "Astorga", "ciudad": "Medellín"},
    "la visitacion": {"nombre": "La Visitación", "ciudad": "Medellín"},
    "los gonzalez": {"nombre": "Los González", "ciudad": "Medellín"},
    "el diamante": {"nombre": "El Diamante", "ciudad": "Medellín"},
    "diamante": {"nombre": "El Diamante", "ciudad": "Medellín"},
    "benedictinos": {"nombre": "Benedictinos", "ciudad": "Medellín"},
    "el castillo": {"nombre": "El Castillo", "ciudad": "Medellín"},
    "castillo": {"nombre": "El Castillo", "ciudad": "Medellín"},
    "alejandria": {"nombre": "Alejandría", "ciudad": "Medellín"},
    "alejandría": {"nombre": "Alejandría", "ciudad": "Medellín"},
    "loma de alejandria": {"nombre": "Alejandría", "ciudad": "Medellín"},
    "loma de alejandría": {"nombre": "Alejandría", "ciudad": "Medellín"},
    "la florida": {"nombre": "La Florida", "ciudad": "Medellín"},
    
    "oviedo": {"nombre": "Oviedo", "ciudad": "Medellín"},
    "sector oviedo": {"nombre": "Oviedo", "ciudad": "Medellín"},
    "zona oviedo": {"nombre": "Oviedo", "ciudad": "Medellín"},

    "aguacatala": {"nombre": "La Aguacatala", "ciudad": "Medellín"},
    "la aguacatala": {"nombre": "La Aguacatala", "ciudad": "Medellín"},
    "santa maria de los angeles": {"nombre": "Santa María de Los Ángeles", "ciudad": "Medellín"},
    "santa maría de los ángeles": {"nombre": "Santa María de Los Ángeles", "ciudad": "Medellín"},

    # Zonas planas (opuesto a loma)
    "zona plana medellin": {"nombre": "Zona Plana Medellín", "ciudad": "Medellín"},
    "zona plana medellín": {"nombre": "Zona Plana Medellín", "ciudad": "Medellín"},
    "zona plana poblado": {"nombre": "Zona Plana Poblado", "ciudad": "Medellín"},
    "zona plana sabaneta": {"nombre": "Zona Plana Sabaneta", "ciudad": "Sabaneta"},
    "zona plana la estrella": {"nombre": "Zona Plana La Estrella", "ciudad": "La Estrella"},
    "zona plana itagüí": {"nombre": "Zona Plana Itagüí", "ciudad": "Itagüí"},
    "zona plana itagui": {"nombre": "Zona Plana Itagüí", "ciudad": "Itagüí"},
    "los balsos": {"nombre": "Los Balsos", "ciudad": "Medellín"},
    "balsos": {"nombre": "Los Balsos", "ciudad": "Medellín"},
    "altos del poblado": {"nombre": "Altos del Poblado", "ciudad": "Medellín"},
    "lalinde": {"nombre": "Lalinde", "ciudad": "Medellín"},
    "villa carlota": {"nombre": "Villa Carlota", "ciudad": "Medellín"},
    "las lomas": {"nombre": "Las Lomas", "ciudad": "Medellín"},
    "loma de los parra": {"nombre": "Loma de Los Parra", "ciudad": "Medellín"},
    "los parra": {"nombre": "Loma de Los Parra", "ciudad": "Medellín"},
    "loma de los gonzalez": {"nombre": "Loma de Los González", "ciudad": "Medellín"},
    "loma de los gonzález": {"nombre": "Loma de Los González", "ciudad": "Medellín"},
    "el campestre": {"nombre": "El Campestre", "ciudad": "Medellín"},
    "campestre": {"nombre": "El Campestre", "ciudad": "Medellín"},
    "san michel": {"nombre": "San Michel", "ciudad": "Medellín"},
    "los naranjos": {"nombre": "Los Naranjos", "ciudad": "Medellín"},
    "la tomatera": {"nombre": "La Tomatera", "ciudad": "Medellín"},
    "las lomas no 1": {"nombre": "Las Lomas No. 1", "ciudad": "Medellín"},
    "las lomas no 2": {"nombre": "Las Lomas No. 2", "ciudad": "Medellín"},
    "la cola del zorro": {"nombre": "la cola del zorro", "ciudad": "Medellín"},
    "cola del zorro": {"nombre": "la cola del zorro", "ciudad": "Medellín"},


    # =========================================
    # SECTOR: BELÉN
    # =========================================

    "belen": {"nombre": "Belén", "ciudad": "Medellín"},
    "belén": {"nombre": "Belén", "ciudad": "Medellín"},

    "belen rosales": {"nombre": "Belén Rosales", "ciudad": "Medellín"},
    "belén rosales": {"nombre": "Belén Rosales", "ciudad": "Medellín"},
    "rosales": {"nombre": "Belén Rosales", "ciudad": "Medellín"},
    "fatima": {"nombre": "Fátima", "ciudad": "Medellín"},
    "fátima": {"nombre": "Fátima", "ciudad": "Medellín"},
    "belen malibu": {"nombre": "Belén Malibu", "ciudad": "Medellín"},
    "belén malibu": {"nombre": "Belén Malibu", "ciudad": "Medellín"},
    "nogal": {"nombre": "Nogal", "ciudad": "Medellín"},
    "granada": {"nombre": "Granada", "ciudad": "Medellín"},
    "aliadas": {"nombre": "Las Playas", "ciudad": "Medellín"},
    "las playas": {"nombre": "Las Playas", "ciudad": "Medellín"},
    "playas": {"nombre": "Las Playas", "ciudad": "Medellín"},
    "san bernardo": {"nombre": "San Bernardo", "ciudad": "Medellín"},
    "la mota": {"nombre": "La Mota", "ciudad": "Medellín"},
    "mota": {"nombre": "La Mota", "ciudad": "Medellín"},
    "loma de los bernal": {"nombre": "Loma de Los Bernal", "ciudad": "Medellín"},
    "los bernal": {"nombre": "Loma de Los Bernal", "ciudad": "Medellín"},
    "rodeo alto": {"nombre": "Rodeo Alto", "ciudad": "Medellín"},
    "rodeo": {"nombre": "Rodeo Alto", "ciudad": "Medellín"},
    "altavista": {"nombre": "Altavista", "ciudad": "Medellín"},
    "miravalle": {"nombre": "Miravalle", "ciudad": "Medellín"},
    "zafra": {"nombre": "Zafra", "ciudad": "Medellín"},
    "las violetas": {"nombre": "Las Violetas", "ciudad": "Medellín"},
    "alpes": {"nombre": "Los Alpes", "ciudad": "Medellín"},
    "los alpes": {"nombre": "Los Alpes", "ciudad": "Medellín"},
    "las mercedes": {"nombre": "Las Mercedes", "ciudad": "Medellín"},
    "la palma": {"nombre": "La Palma", "ciudad": "Medellín"},
    "diego echavarria": {"nombre": "Diego Echavarría", "ciudad": "Medellín"},
    "diego echavarría": {"nombre": "Diego Echavarría", "ciudad": "Medellín"},
    "rincon": {"nombre": "Rincón", "ciudad": "Medellín"},
    "rincón": {"nombre": "Rincón", "ciudad": "Medellín"},


    # =========================================
    # SECTOR: GUAYABAL
    # =========================================

    "guayabal": {"nombre": "Guayabal", "ciudad": "Medellín"},
    "trinidad": {"nombre": "Trinidad", "ciudad": "Medellín"},
    "barrio antioquia": {"nombre": "Barrio Antioquia", "ciudad": "Medellín"},
    "antioquia": {"nombre": "Barrio Antioquia", "ciudad": "Medellín"},
    "campo amor": {"nombre": "Campo Amor", "ciudad": "Medellín"},
    "campoamor": {"nombre": "Campo Amor", "ciudad": "Medellín"},
    "cristo rey": {"nombre": "Cristo Rey", "ciudad": "Medellín"},
    "la colina": {"nombre": "La Colina", "ciudad": "Medellín"},
    "colina": {"nombre": "La Colina", "ciudad": "Medellín"},
    "tenche": {"nombre": "Tenche", "ciudad": "Medellín"},
    "el rodeo": {"nombre": "El Rodeo", "ciudad": "Medellín"},
    "club el rodeo": {"nombre": "Club El Rodeo", "ciudad": "Medellín"},


    # =========================================
    # SECTOR: CENTRO SUR / TRANSICIÓN
    # =========================================

    "san diego": {"nombre": "San Diego", "ciudad": "Medellín"},
    "ciudad del rio": {"nombre": "Ciudad del Río", "ciudad": "Medellín"},
    "boston": {"nombre": "Boston", "ciudad": "Medellín"},
    "la candelaria": {"nombre": "La Candelaria", "ciudad": "Medellín"},


    # =========================================
    # SECTOR: OCCIDENTE CERCANO (frecuente en captación)
    # =========================================

    "laureles": {"nombre": "Laureles", "ciudad": "Medellín"},
    "la castellana": {"nombre": "La Castellana", "ciudad": "Medellín"},
    "castellana": {"nombre": "La Castellana", "ciudad": "Medellín"},
    "san joaquin": {"nombre": "San Joaquín", "ciudad": "Medellín"},
    "san joaquín": {"nombre": "San Joaquín", "ciudad": "Medellín"},
    "bolivariana": {"nombre": "Bolivariana", "ciudad": "Medellín"},
    "carlos e restrepo": {"nombre": "Carlos E. Restrepo", "ciudad": "Medellín"},
    "carlos e. restrepo": {"nombre": "Carlos E. Restrepo", "ciudad": "Medellín"},
    "aeroparque juan pablo ii": {"nombre": "Aeroparque Juan Pablo II", "ciudad": "Medellín"},
    "nueva villa de aburra": {"nombre": "Nueva Villa de Aburrá", "ciudad": "Medellín"},
    "barrio colombia": {"nombre": "Barrio Colombia", "ciudad": "Medellín"},
    "la america": {"nombre": "La América", "ciudad": "Medellín"},
    "calasanz": {"nombre": "Calasanz", "ciudad": "Medellín"},
    "estadio": {"nombre": "Estadio", "ciudad": "Medellín"},
    "suramericana": {"nombre": "Suramericana", "ciudad": "Medellín"},
    "conquistadores": {"nombre": "Conquistadores", "ciudad": "Medellín"},
    "florida nueva": {"nombre": "Florida Nueva", "ciudad": "Medellín"},
    "los colores": {"nombre": "Los Colores", "ciudad": "Medellín"},
    "simon bolivar": {"nombre": "Simón Bolívar", "ciudad": "Medellín"},
    "robledo": {"nombre": "Robledo", "ciudad": "Medellín"},

    # === SABANETA ===
    "aves maria": {"nombre": "Aves María", "ciudad": "Sabaneta"},
    "aves maría": {"nombre": "Aves María", "ciudad": "Sabaneta"},
    "calle larga": {"nombre": "Calle Larga", "ciudad": "Sabaneta"},
    "las lomitas": {"nombre": "Las Lomitas", "ciudad": "Sabaneta"},
    "mayorca": {"nombre": "Mayorca", "ciudad": "Sabaneta"},
    "pan de azucar": {"nombre": "Pan de Azúcar", "ciudad": "Sabaneta"},
    "san jose": {"nombre": "San José", "ciudad": "Sabaneta"},
    "la barquereña": {"nombre": "La Barquereña", "ciudad": "Sabaneta"},
    "barquereña": {"nombre": "La Barquereña", "ciudad": "Sabaneta"},
    "entreamigos": {"nombre": "Entreamigos", "ciudad": "Sabaneta"},
    "holanda": {"nombre": "Holanda", "ciudad": "Sabaneta"},
    "san joaquin": {"nombre": "San Joaquín", "ciudad": "Sabaneta"},
    "san joaquín": {"nombre": "San Joaquín", "ciudad": "Sabaneta"},
    "maria auxiliadora": {"nombre": "María Auxiliadora", "ciudad": "Sabaneta"},
    "maría auxiliadora": {"nombre": "María Auxiliadora", "ciudad": "Sabaneta"},
    "las casitas": {"nombre": "Las Casitas", "ciudad": "Sabaneta"},
    "ardillas": {"nombre": "Ardillas", "ciudad": "Sabaneta"},
    "asdesillas": {"nombre": "Asdesillas", "ciudad": "Sabaneta"},

    # === BELLO ===
    "niquia": {"nombre": "Niquía", "ciudad": "Bello"},
    "niquía": {"nombre": "Niquía", "ciudad": "Bello"},
    "cabañas": {"nombre": "Cabañas", "ciudad": "Bello"},
    "cabanas": {"nombre": "Cabañas", "ciudad": "Bello"},
    "la cumbre": {"nombre": "La Cumbre", "ciudad": "Bello"},
    "centro bello": {"nombre": "Centro", "ciudad": "Bello"},

    # === ITAGÜÍ ===
    "ditaires": {"nombre": "Ditaires", "ciudad": "Itagüí"},
    "santa maria itagui": {"nombre": "Santa María", "ciudad": "Itagüí"},
    "suramerica": {"nombre": "Suramérica", "ciudad": "Itagüí"},
    "pilsen": {"nombre": "Pilsen", "ciudad": "Itagüí"},

    # === LA ESTRELLA ===
    "pueblo viejo": {"nombre": "Pueblo Viejo", "ciudad": "La Estrella"},
    "la tablaza": {"nombre": "La Tablaza", "ciudad": "La Estrella"},
    "la ferreria": {"nombre": "La Ferrería", "ciudad": "La Estrella"},

    # === CALDAS ===
    "la valeria": {"nombre": "La Valeria", "ciudad": "Caldas"},
    "la quiebra": {"nombre": "La Quiebra", "ciudad": "Caldas"},

    # === COPACABANA ===
    "machado": {"nombre": "Machado", "ciudad": "Copacabana"},
    "el cabuyal": {"nombre": "El Cabuyal", "ciudad": "Copacabana"},
}


# =========================================
# PUNTOS DE INTERÉS (POIs)
# Centros comerciales y lugares de referencia mapeados a barrios
# =========================================
PUNTOS_INTERES: dict[str, dict[str, any]] = {
    "viva envigado": {
        "nombre": "Viva Envigado",
        "ciudad": "Envigado",
        "keywords": ["viva envigado", "cc viva", "viva"],
        "barrios_cercanos": ["Alcalá", "Zona Centro", "Envigado Bajo", "San Marcos", "El Dorado"]
    },
    "exito envigado": {
        "nombre": "Éxito Envigado",
        "ciudad": "Envigado",
        "keywords": ["exito envigado", "exito de envigado", "exito"],
        "barrios_cercanos": ["Alcalá", "Zona Centro", "Envigado Bajo", "San Marcos", "El Dorado"]
    },
    "city plaza": {
        "nombre": "City Plaza",
        "ciudad": "Envigado",
        "keywords": ["city plaza", "cityplaza", "cc city plaza"],
        "barrios_cercanos": ["El Esmeraldal", "Loma del Chocho", "Guayacanes"]
    },
    "parque envigado": {
        "nombre": "Parque de Envigado",
        "ciudad": "Envigado",
        "keywords": ["parque de envigado", "parque envigado", "cerca al parque"],
        "barrios_cercanos": ["Centro", "San Marcos", "La Magnolia", "Jardines", "El Dorado"]
    },
    "el tesoro": {
        "nombre": "El Tesoro",
        "ciudad": "Medellín",
        "keywords": ["el tesoro", "cc el tesoro", "tesoro"],
        "barrios_cercanos": ["El Tesoro", "Poblado Alto", "Altos del Poblado", "Los González"]
    },
    "santafe": {
        "nombre": "Santafé",
        "ciudad": "Medellín",
        "keywords": ["santafe", "santa fe", "cc santafe", "cc santa fe"],
        "barrios_cercanos": ["El Poblado", "Poblado Bajo", "La Aguacatala", "Alejandría", "Oviedo"]
    },
    "oviedo": {
        "nombre": "Oviedo",
        "ciudad": "Medellín",
        "keywords": ["oviedo", "cc oviedo", "sector oviedo", "zona oviedo"],
        "barrios_cercanos": ["El Poblado", "Poblado Bajo", "La Aguacatala", "Alejandría", "Santafé"]
    },
    "unicentro": {
        "nombre": "Unicentro",
        "ciudad": "Medellín",
        "keywords": ["unicentro", "cc unicentro"],
        "barrios_cercanos": ["Laureles", "Conquistadores", "Fátima"]
    },
    "parque fabricato": {
        "nombre": "Parque Fabricato",
        "ciudad": "Bello",
        "keywords": ["fabricato", "parque fabricato", "cc fabricato"],
        "barrios_cercanos": ["Cabañas", "Niquía", "Centro"]
    },
    "puerta del norte": {
        "nombre": "Puerta del Norte",
        "ciudad": "Bello",
        "keywords": ["puerta del norte", "puertadelnorte", "cc puerta del norte"],
        "barrios_cercanos": ["Niquía"]
    },
    "parque sabaneta": {
        "nombre": "Parque de Sabaneta",
        "ciudad": "Sabaneta",
        "keywords": ["parque de sabaneta", "parque sabaneta", "cerca al parque"],
        "barrios_cercanos": ["Calle Larga", "La Barquereña", "Entreamigos", "Holanda", "San Joaquín", "María Auxiliadora", "Las Casitas"]
    },
    "parque el poblado": {
        "nombre": "Parque El Poblado",
        "ciudad": "Medellín",
        "keywords": ["parque el poblado", "parque lleras", "lleras", "cerca al parque"],
        "barrios_cercanos": ["Manila", "Astorga", "Lalinde", "Patio Bonito"]
    }
}