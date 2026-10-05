from models import Estudiante
from shared.json_manager import GestorJSON


class ClienteController:
    """CONTROLADOR BASE: las cinco operaciones estándar."""

    MODELO = Estudiante
    ARCHIVO = "data/estudiantes.json"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")
    _gestor = GestorJSON(ARCHIVO)

    @classmethod
    def _registros(cls):
        return cls._gestor.leer()

    @classmethod
    def emails_registrados(cls, excepto_id=None):
        return {
            registro["email"].lower()
            for registro in cls._registros()
            if registro["id"] != excepto_id
        }

    @classmethod
    def siguiente_id(cls):
        ids = [registro["id"] for registro in cls._registros()]
        return max(ids) + 1 if ids else 1

    @staticmethod
    def _coincide(registro, termino, campos):
        for campo in campos:
            if termino in str(registro.get(campo, "")).lower():
                return True
        return False

    @classmethod
    def crear(cls, datos):
        try:
            faltantes = [
                campo for campo in cls.MODELO.OBLIGATORIOS
                if not str(datos.get(campo, "")).strip()
            ]
            if faltantes:
                return False, f"Faltan campos obligatorios: {', '.join(faltantes)}"

            email = str(datos.get("email", "")).strip().lower()
            if email in cls.emails_registrados():
                return False, "Ese email ya está registrado"

            # Validación específica de carnet duplicado para estudiantes
            if hasattr(cls, "carnets_registrados"):
                carnet = str(datos.get("carnet", "")).strip().upper()
                if carnet in cls.carnets_registrados():
                    return False, "Ese carnet ya está registrado"

            valores = {campo: datos.get(campo, "") for campo in cls.MODELO.CAMPOS}
            objeto = cls.MODELO(cls.siguiente_id(), **valores)

            registros = cls._registros()
            registros.append(objeto.a_diccionario())
            if not cls._gestor.guardar(registros):
                return False, "No se pudo escribir el archivo"

            return True, f"{objeto.nombre_completo} creado con id {objeto.id}"

        except ValueError as error:
            return False, str(error)

    @classmethod
    def listar(cls):
        return [cls.MODELO.desde_diccionario(r) for r in cls._registros()]

    @classmethod
    def obtener(cls, id_registro):
        for objeto in cls.listar():
            if objeto.id == id_registro:
                return objeto
        return None

    @classmethod
    def buscar(cls, termino):
        termino = str(termino).strip().lower()
        if not termino:
            return []
        return [
            cls.MODELO.desde_diccionario(registro)
            for registro in cls._registros()
            if cls._coincide(registro, termino, cls.CAMPOS_BUSCABLES)
        ]

    @classmethod
    def actualizar(cls, id_registro, cambios):
        try:
            desconocidos = set(cambios) - set(cls.MODELO.CAMPOS)
            if desconocidos:
                return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"
            if not cambios:
                return False, "No se indicó ningún cambio"

            objeto = cls.obtener(id_registro)
            if objeto is None:
                return False, f"No existe un registro con id {id_registro}"

            if "email" in cambios:
                nuevo = str(cambios["email"]).strip().lower()
                if nuevo in cls.emails_registrados(excepto_id=id_registro):
                    return False, "Ese email ya lo usa otro registro"

            if "carnet" in cambios and hasattr(cls, "carnets_registrados"):
                nuevo_carnet = str(cambios["carnet"]).strip().upper()
                if nuevo_carnet in cls.carnets_registrados(excepto_id=id_registro):
                    return False, "Ese carnet ya lo usa otro estudiante"

            for campo, valor in cambios.items():
                setattr(objeto, campo, valor)

            registros = cls._registros()
            for indice, registro in enumerate(registros):
                if registro["id"] == id_registro:
                    registros[indice] = objeto.a_diccionario()
                    break

            cls._gestor.guardar(registros)
            return True, f"Registro {id_registro} actualizado ({len(cambios)} campo/s)"

        except ValueError as error:
            return False, str(error)

    @classmethod
    def eliminar(cls, id_registro):
        registros = cls._registros()
        quedan = [r for r in registros if r["id"] != id_registro]

        if len(quedan) == len(registros):
            return False, f"No existe un registro con id {id_registro}"

        cls._gestor.guardar(quedan)
        return True, f"Registro {id_registro} eliminado"

    @classmethod
    def estadisticas(cls):
        registros = cls._registros()
        dominios = {r["email"].split("@")[1] for r in registros if "@" in r["email"]}
        aprobados = sum(1 for r in registros if cls.MODELO.desde_diccionario(r).estado == "Aprobado")
        return {
            "total": len(registros),
            "aprobados": aprobados,
            "reprobados": len(registros) - aprobados,
            "dominios": sorted(dominios),
        }


class EstudianteController(ClienteController):
    """CONTROLADOR DE ESTUDIANTES: hereda el CRUD y añade lógica de notas y carnets."""

    MODELO = Estudiante
    ARCHIVO = "data/estudiantes.json"
    CAMPOS_BUSCABLES = ("nombre", "apellido", "email", "carnet")
    _gestor = GestorJSON(ARCHIVO)

    @classmethod
    def carnets_registrados(cls, excepto_id=None):
        """CONJUNTO de carnets ya usados para evitar duplicados."""
        return {
            registro["carnet"].upper()
            for registro in cls._registros()
            if registro["id"] != excepto_id
        }

    @classmethod
    def agregar_nota(cls, id_estudiante, materia, nota):
        """Busca al estudiante, le añade la nota validada y guarda el archivo."""
        try:
            objeto = cls.obtener(id_estudiante)
            if objeto is None:
                return False, f"No existe un estudiante con id {id_estudiante}"

            # El método del modelo valida si la nota está entre 0 y 20
            objeto.agregar_nota(materia, float(nota))

            registros = cls._registros()
            for indice, registro in enumerate(registros):
                if registro["id"] == id_estudiante:
                    registros[indice] = objeto.a_diccionario()
                    break

            cls._gestor.guardar(registros)
            return True, f"Nota de {nota} agregada en {materia} para {objeto.nombre_completo}"

        except ValueError as error:
            return False, str(error)

    @classmethod
    def materias_ofertadas(cls):
        """Devuelve un conjunto (set) con todas las materias registradas en la escuela sin repetir."""
        todas = set()
        for objeto in cls.listar():
            todas.update(objeto.materias)
        return todas

    @classmethod
    def materias_en_comun_estudiantes(cls, id_a, id_b):
        """Usa la intersección de conjuntos del modelo entre dos estudiantes."""
        est_a = cls.obtener(id_a)
        est_b = cls.obtener(id_b)
        if not est_a or not est_b:
            return None
        return est_a.materias_en_comun(est_b)