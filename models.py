class Estudiante:
    """MODELO: un estudiante con sus materias (set) y sus notas (dict de listas)."""

    CAMPOS = ("nombre", "apellido", "email", "carnet")
    OBLIGATORIOS = ("nombre", "apellido", "email", "carnet")
    NOTA_MINIMA = 0
    NOTA_MAXIMA = 20
    total_creados = 0

    def __init__(self, id_estudiante, nombre, apellido, email, carnet,
                 notas=None, materias=None):
        self.__id = id_estudiante
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.carnet = carnet
        self.__notas = dict(notas) if notas else {}           # DICCIONARIO de LISTAS
        self.__materias = set(materias) if materias else set()   # CONJUNTO
        Estudiante.total_creados += 1

    # ===== ESTÁTICOS =====
    @staticmethod
    def limpiar(texto):
        return str(texto).strip()

    @staticmethod
    def es_nota_valida(nota):
        return isinstance(nota, (int, float)) and \
            Estudiante.NOTA_MINIMA <= nota <= Estudiante.NOTA_MAXIMA

    # ===== PROPIEDADES =====
    @property
    def id(self):
        return self.__id

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = Estudiante.limpiar(valor)
        if not valor:
            raise ValueError("El nombre es obligatorio")
        self.__nombre = valor.title()

    @property
    def apellido(self):
        return self.__apellido

    @apellido.setter
    def apellido(self, valor):
        valor = Estudiante.limpiar(valor)
        if not valor:
            raise ValueError("El apellido es obligatorio")
        self.__apellido = valor.title()

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        valor = Estudiante.limpiar(valor)
        if "@" not in valor:
            raise ValueError(f"Email inválido: '{valor}'")
        self.__email = valor.lower()

    @property
    def carnet(self):
        return self.__carnet

    @carnet.setter
    def carnet(self, valor):
        valor = Estudiante.limpiar(valor).upper()
        if len(valor) < 4:
            raise ValueError("El carnet debe tener al menos 4 caracteres")
        self.__carnet = valor

    @property
    def materias(self):
        return set(self.__materias)

    @property
    def nombre_completo(self):
        return f"{self.__nombre} {self.__apellido}"

    @property
    def promedio(self):
        todas = []
        for lista_notas in self.__notas.values():
            todas.extend(lista_notas)
        return round(sum(todas) / len(todas), 2) if todas else 0

    @property
    def estado(self):
        """Propiedad calculada exigida en la tarea: Aprobado si promedio >= 14"""
        return "Aprobado" if self.promedio >= 14 else "Reprobado"

    # ===== MÉTODOS DE INSTANCIA =====
    def inscribir_materia(self, materia):
        materia = Estudiante.limpiar(materia).title()
        if not materia:
            raise ValueError("La materia no puede estar vacía")
        self.__materias.add(materia)
        return materia

    def agregar_nota(self, materia, nota):
        if not Estudiante.es_nota_valida(nota):
            raise ValueError(
                f"La nota debe estar entre {Estudiante.NOTA_MINIMA} y {Estudiante.NOTA_MAXIMA}"
            )
        materia = self.inscribir_materia(materia)
        self.__notas.setdefault(materia, []).append(nota)

    def notas_de(self, materia):
        return list(self.__notas.get(Estudiante.limpiar(materia).title(), []))

    def materias_en_comun(self, otro):
        return self.__materias & otro.materias

    def a_diccionario(self):
        return {
            "id": self.__id,
            "nombre": self.__nombre,
            "apellido": self.__apellido,
            "email": self.__email,
            "carnet": self.__carnet,
            "notas": self.__notas,
            "materias": sorted(self.__materias),
        }

    def __str__(self):
        return f"[{self.__carnet}] {self.nombre_completo} - Promedio: {self.promedio} ({self.estado})"

    # ===== MÉTODO DE CLASE =====
    @classmethod
    def desde_diccionario(cls, datos):
        return cls(
            datos["id"], datos["nombre"], datos["apellido"], datos["email"],
            datos["carnet"],
            notas=datos.get("notas", {}),
            materias=set(datos.get("materias", [])),
        )

