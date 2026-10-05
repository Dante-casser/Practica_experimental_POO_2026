from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import EstudianteController


class MenuEstudiantes:
    """VISTA: muestra, pide y presenta. No decide reglas del negocio."""

    TITULO = "SISTEMA DE GESTIÓN DE ESTUDIANTES"
    ANCHO = 90

    def __init__(self, controlador=EstudianteController):
        self.__controlador = controlador
        self.__activo = True
        self.__opciones = {
            "1": ("Crear estudiante", self.crear),
            "2": ("Ver todos", self.listar),
            "3": ("Buscar", self.buscar),
            "4": ("Ver por id", self.ver_por_id),
            "5": ("Actualizar", self.actualizar),
            "6": ("Eliminar", self.eliminar),
            "7": ("Agregar nota", self.agregar_nota),
            "8": ("Materias ofertadas", self.materias_ofertadas),
            "9": ("Materias en común", self.materias_en_comun),
            "10": ("Estadísticas", self.estadisticas),
            "0": ("Salir", self.salir),
        }

    @staticmethod
    def pausa():
        input("\nPresione Enter para continuar...")

    @staticmethod
    def pedir_entero(etiqueta):
        try:
            return int(input(etiqueta))
        except ValueError:
            return None

    @staticmethod
    def mostrar_resultado(exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    def mostrar_tabla(self, estudiantes):
        print(f"{'ID':<5}{'CARNET':<15}{'NOMBRE':<25}{'EMAIL':<28}{'PROMEDIO':<10}{'ESTADO':<10}")
        print("-" * self.ANCHO)
        for est in estudiantes:
            print(f"{est.id:<5}{est.carnet:<15}{est.nombre_completo:<25}"
                  f"{est.email:<28}{est.promedio:<10}{est.estado:<10}")
        print("-" * self.ANCHO)
        imprimir_info(f"Total: {len(estudiantes)} estudiante(s)")

    def crear(self):
        imprimir_titulo("CREAR NUEVO ESTUDIANTE")
        datos = {}
        for campo in self.__controlador.MODELO.CAMPOS:
            datos[campo] = input(f"{campo.capitalize()}: ")

        exito, mensaje = self.__controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def listar(self):
        imprimir_titulo("LISTA DE ESTUDIANTES")
        estudiantes = self.__controlador.listar()
        if not estudiantes:
            imprimir_info("Todavía no hay estudiantes. Use la opción 1 para crear el primero.")
        else:
            self.mostrar_tabla(estudiantes)
        self.pausa()

    def buscar(self):
        imprimir_titulo("BUSCAR ESTUDIANTE")
        termino = input("Nombre, apellido, email o carnet: ")
        encontrados = self.__controlador.buscar(termino)
        if not encontrados:
            imprimir_info(f"Ningún estudiante coincide con '{termino}'.")
        else:
            self.mostrar_tabla(encontrados)
        self.pausa()

    def ver_por_id(self):
        imprimir_titulo("VER ESTUDIANTE POR ID")
        id_est = self.pedir_entero("Id del estudiante: ")
        if id_est is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        est = self.__controlador.obtener(id_est)
        if est is None:
            imprimir_error(f"No existe un estudiante con id {id_est}")
        else:
            for clave, valor in est.a_diccionario().items():
                print(f"  {clave.capitalize():<12}: {valor}")
            print(f"  Promedio     : {est.promedio}")
            print(f"  Estado       : {est.estado}")
            print(f"  Materias     : {', '.join(est.materias) if est.materias else 'Ninguna'}")
        self.pausa()

    def actualizar(self):
        imprimir_titulo("ACTUALIZAR ESTUDIANTE")
        id_est = self.pedir_entero("Id del estudiante: ")
        if id_est is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        est = self.__controlador.obtener(id_est)
        if est is None:
            imprimir_error(f"No existe un estudiante con id {id_est}")
            return self.pausa()

        imprimir_info(f"Editando a {est.nombre_completo}")
        print("Deje en blanco el campo que no quiera cambiar.\n")

        cambios = {}
        for campo in self.__controlador.MODELO.CAMPOS:
            actual = getattr(est, campo)
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo:
            
                cambios[campo] = nuevo

        self.mostrar_resultado(*self.__controlador.actualizar(id_est, cambios))
        self.pausa()

    def eliminar(self):
        imprimir_titulo("ELIMINAR ESTUDIANTE")
        id_est = self.pedir_entero("Id del estudiante: ")
        if id_est is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        est = self.__controlador.obtener(id_est)
        if est is None:
            imprimir_error(f"No existe un estudiante con id {id_est}")
            return self.pausa()

        imprimir_info(f"Se eliminará: {est}")
        if confirmar("¿Confirma la eliminación?"):
            self.mostrar_resultado(*self.__controlador.eliminar(id_est))
        else:
            imprimir_info("Operación cancelada")
        self.pausa()

    def agregar_nota(self):
        imprimir_titulo("AGREGAR NOTA A ESTUDIANTE")
        id_est = self.pedir_entero("Id del estudiante: ")
        if id_est is None:
            imprimir_error("El id debe ser un número entero")
            return self.pausa()

        materia = input("Nombre de la materia: ")
        try:
            nota = float(input("Nota (0 a 20): "))
        except ValueError:
            imprimir_error("La nota debe ser un valor numérico")
            return self.pausa()

        exito, mensaje = self.__controlador.agregar_nota(id_est, materia, nota)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def materias_ofertadas(self):
        imprimir_titulo("MATERIAS OFERTADAS EN LA ESCUELA")
        materias = self.__controlador.materias_ofertadas()
        if not materias:
            imprimir_info("Todavía no hay materias registradas.")
        else:
            for m in sorted(materias):
                print(f"  • {m}")
        self.pausa()

    def materias_en_comun(self):
        imprimir_titulo("MATERIAS EN COMÚN ENTRE DOS ESTUDIANTES")
        id_a = self.pedir_entero("Id del primer estudiante: ")
        id_b = self.pedir_entero("Id del segundo estudiante: ")
        if id_a is None or id_b is None:
            imprimir_error("Los ids deben ser números enteros")
            return self.pausa()

        comun = self.__controlador.materias_en_comun_estudiantes(id_a, id_b)
        if comun is None:
            imprimir_error("Uno o ambos estudiantes no existen")
        elif not comun:
            imprimir_info("No comparten ninguna materia.")
        else:
            imprimir_exito(f"Materias en común: {', '.join(sorted(comun))}")
        self.pausa()

    def estadisticas(self):
        imprimir_titulo("ESTADÍSTICAS")
        datos = self.__controlador.estadisticas()
        print(f"  Total de estudiantes : {datos['total']}")
        print(f"  Aprobados (>= 14)    : {datos['aprobados']}")
        print(f"  Reprobados (< 14)    : {datos['reprobados']}")
        print(f"  Dominios de email    : {', '.join(datos['dominios'])}")
        self.pausa()

    def salir(self):
        self.__activo = False
        imprimir_info("¡Hasta luego!")

    def mostrar_menu(self):
        imprimir_titulo(self.TITULO)
        for tecla, (texto, _metodo) in self.__opciones.items():
            print(f"  {tecla:>2}. {texto}")
        print()

    def ejecutar(self):
        while self.__activo:
            self.mostrar_menu()
            tecla = input("Seleccione una opción: ").strip()

            if tecla not in self.__opciones:
                imprimir_error("Opción no válida")
                self.pausa()
                continue

            _texto, metodo = self.__opciones[tecla]
            metodo()


if __name__ == "__main__":
    try:
        MenuEstudiantes().ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")