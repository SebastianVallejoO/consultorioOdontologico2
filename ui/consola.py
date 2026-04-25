from models.cliente import Cliente
from utils.helpers import pedir_opcion, pedir_entero, pedir_texto, pedir_numero, pedir_fecha
from services.cita_service import (
    calcular_total, ordenar_clientes, ingresos_totales,
    contar_extracciones, contar_urgentes, construir_cola_urgentes
)
from structures.cola import Cola

clientes = []
agenda_dia = Cola()        # Cola de atención del día (FIFO)
cola_urgentes = Cola()     # Cola persistente de urgentes con extracción
cola_urgentes_generada = False  # Indica si ya se generó la cola de urgentes


# ─────────────────────────────────────────────
# Registro de cliente
# ─────────────────────────────────────────────

def pedir_cliente():
    cedula = pedir_numero("Cédula: ")
    nombre = pedir_texto("Nombre: ")
    telefono = pedir_numero("Teléfono: ")

    tipo_cliente = pedir_opcion(
        "Tipo cliente (particular/eps/prepagada): ",
        ["particular", "eps", "prepagada"]
    )

    tipo_atencion = pedir_opcion(
        "Tipo atención (limpieza/calzas/extraccion/diagnostico): ",
        ["limpieza", "calzas", "extraccion", "diagnostico"]
    )

    if tipo_atencion in ["limpieza", "diagnostico"]:
        print("Para este tipo de atención la cantidad es 1 automáticamente.")
        cantidad = 1
    else:
        cantidad = pedir_entero("Cantidad: ")

    prioridad = pedir_opcion(
        "Prioridad (normal/urgente): ",
        ["normal", "urgente"]
    )

    fecha = pedir_fecha("Fecha (dd/mm/aaaa): ")

    return Cliente(
        cedula, nombre, telefono,
        tipo_cliente, tipo_atencion,
        cantidad, prioridad, fecha
    )


def registrar_cliente():
    global cola_urgentes_generada
    cliente = pedir_cliente()
    calcular_total(cliente)
    clientes.append(cliente)
    cola_urgentes_generada = False  # Resetear para que se reconstruya con el nuevo cliente
    print("Cliente registrado correctamente.\n")


# ─────────────────────────────────────────────
# Estadísticas
# ─────────────────────────────────────────────

def mostrar_estadisticas():
    if not clientes:
        print("\nNo hay clientes registrados aún.\n")
        return

    print("\n--- RESULTADOS ---")
    print("Total clientes:", len(clientes))
    print("Ingresos:", f"${ingresos_totales(clientes):,}")
    print("Extracciones:", contar_extracciones(clientes))
    print("Clientes urgentes:", contar_urgentes(clientes))

    ordenados = ordenar_clientes(clientes)

    print("\n--- CLIENTES ORDENADOS POR VALOR (mayor a menor) ---")
    for c in ordenados:
        print(f"{c.nombre} | {c.tipo_atencion} | ${c.total:,}")
    print()


# ─────────────────────────────────────────────
# Búsqueda
# ─────────────────────────────────────────────

def buscar_cliente():
    cedula = input("\nBuscar cédula: ")

    for c in clientes:
        if c.cedula == cedula:
            print(f"""
--- Cliente encontrado ---
Cédula:       {c.cedula}
Nombre:       {c.nombre}
Teléfono:     {c.telefono}
Tipo cliente: {c.tipo_cliente}
Tipo atención:{c.tipo_atencion}
Cantidad:     {c.cantidad}
Prioridad:    {c.prioridad}
Fecha:        {c.fecha}
Total:        ${c.total:,}
""")
            return

    print("Cliente no encontrado\n")


# ─────────────────────────────────────────────
# Gestión de agenda con Cola (atención del día)
# ─────────────────────────────────────────────

def menu_agenda():
    while True:
        print("""
    --- AGENDA DEL DÍA (Cola de atención FIFO) ---
    1. Agregar cliente a la cola
    2. Ver cola completa
    3. Atender siguiente cliente
    4. Ver próximo cliente (sin atender)
    5. Volver al menú principal
        """)
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            agregar_a_cola()
        elif opcion == "2":
            ver_cola()
        elif opcion == "3":
            atender_siguiente()
        elif opcion == "4":
            ver_proximo()
        elif opcion == "5":
            break
        else:
            print("Opción inválida\n")


def agregar_a_cola():
    if not clientes:
        print("No hay clientes registrados aún.")
        return

    cedula = input("Ingrese la cédula del cliente a agregar a la agenda: ")
    for c in clientes:
        if c.cedula == cedula:
            agenda_dia.enqueue(c)
            print(f"Cliente '{c.nombre}' agregado a la cola. Posición: {agenda_dia.size()}\n")
            return

    print("Cliente no encontrado. Regístrelo primero desde el menú principal.\n")


def ver_cola():
    if agenda_dia.is_empty():
        print("\nLa agenda de hoy está vacía.\n")
        return

    print(f"\n--- COLA DE ATENCIÓN ({agenda_dia.size()} cliente(s)) ---")
    for i, c in enumerate(agenda_dia.to_list(), start=1):
        print(f"{i}. {c.nombre} | Cédula: {c.cedula} | "
              f"Atención: {c.tipo_atencion} | "
              f"Prioridad: {c.prioridad} | Total: ${c.total:,}")
    print()


def atender_siguiente():
    try:
        cliente = agenda_dia.dequeue()
        print(f"""
--- ATENDIENDO CLIENTE ---
Nombre:    {cliente.nombre}
Cédula:    {cliente.cedula}
Teléfono:  {cliente.telefono}
Atención:  {cliente.tipo_atencion}
Cantidad:  {cliente.cantidad}
Prioridad: {cliente.prioridad}
Total:     ${cliente.total:,}
Quedan {agenda_dia.size()} cliente(s) en cola.
""")
    except IndexError as e:
        print(f"\n{e}\n")


def ver_proximo():
    try:
        c = agenda_dia.peek()
        print(f"\nPróximo: {c.nombre} | {c.tipo_atencion} | "
              f"Prioridad: {c.prioridad} | ${c.total:,}\n")
    except IndexError as e:
        print(f"\n{e}\n")


# ─────────────────────────────────────────────
# Cola de urgentes (persistente en la sesión)
# ─────────────────────────────────────────────

def menu_cola_urgentes():
    """
    Menú para gestionar la cola de urgentes:
    - Solo clientes con extracción dental y prioridad urgente
    - Ordenados por fecha más cercana → más lejana
    - Se puede llamar/atender cliente por cliente (dequeue)
    - Se puede regenerar la cola desde los datos actuales
    """
    global cola_urgentes, cola_urgentes_generada

    # Generar la cola si aún no existe o fue reseteada
    if not cola_urgentes_generada:
        cola_urgentes = construir_cola_urgentes(clientes)
        cola_urgentes_generada = True

    while True:
        print(f"""
    === COLA DE URGENTES (Extracciones) ===
    Clientes pendientes en cola: {cola_urgentes.size()}
    ----------------------------------------
    1. Ver informe completo de la cola
    2. Llamar / atender siguiente urgente
    3. Ver próximo urgente (sin atender)
    4. Regenerar cola (actualizar desde registros)
    5. Volver al menú principal
        """)
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            mostrar_informe_cola_urgentes()
        elif opcion == "2":
            llamar_siguiente_urgente()
        elif opcion == "3":
            ver_proximo_urgente()
        elif opcion == "4":
            cola_urgentes = construir_cola_urgentes(clientes)
            print(f"\nCola regenerada. Total clientes: {cola_urgentes.size()}\n")
        elif opcion == "5":
            break
        else:
            print("Opción inválida\n")


def mostrar_informe_cola_urgentes():
    """Muestra el informe completo de la cola de urgentes sin modificarla."""
    print("\n" + "=" * 60)
    print("   INFORME - COLA DE URGENTES (Extracciones Dentales)")
    print("=" * 60)

    if cola_urgentes.is_empty():
        print("No hay clientes en la cola de urgentes.")
        print("Criterios de filtro:")
        print("  - Tipo de atención: Extracción")
        print("  - Prioridad: Urgente")
        print("=" * 60 + "\n")
        return

    print(f"Total en cola: {cola_urgentes.size()} cliente(s)")
    print(f"{'#':<4} {'Nombre':<22} {'Cédula':<12} {'Fecha':<12} {'Teléfono':<13} {'Total'}")
    print("-" * 72)

    for i, c in enumerate(cola_urgentes.to_list(), start=1):
        print(f"{i:<4} {c.nombre:<22} {c.cedula:<12} {c.fecha:<12} {c.telefono:<13} ${c.total:,}")

    print("=" * 60)
    print("Orden: fecha más cercana → más lejana (FIFO)")
    print("=" * 60 + "\n")


def llamar_siguiente_urgente():
    """Llama y atiende al siguiente cliente urgente (dequeue)."""
    try:
        cliente = cola_urgentes.dequeue()
        print(f"""
--- LLAMANDO CLIENTE URGENTE ---
Nombre:    {cliente.nombre}
Cédula:    {cliente.cedula}
Teléfono:  {cliente.telefono}
Fecha:     {cliente.fecha}
Atención:  {cliente.tipo_atencion}
Cantidad:  {cliente.cantidad}
Prioridad: {cliente.prioridad}
Total:     ${cliente.total:,}
Quedan {cola_urgentes.size()} cliente(s) urgentes en cola.
""")
    except IndexError:
        print("\nNo hay clientes urgentes en la cola.\n")


def ver_proximo_urgente():
    """Muestra el próximo urgente sin retirarlo de la cola."""
    try:
        c = cola_urgentes.peek()
        print(f"\nPróximo urgente: {c.nombre} | Cédula: {c.cedula} | "
              f"Fecha: {c.fecha} | ${c.total:,}\n")
    except IndexError:
        print("\nNo hay clientes urgentes en la cola.\n")


# ─────────────────────────────────────────────
# Menú principal
# ─────────────────────────────────────────────

def mostrar_menu():
    print("""
    ╔══════════════════════════════════════╗
    ║    CONSULTORIO ODONTOLÓGICO          ║
    ║    Sistema de Gestión con Colas      ║
    ╠══════════════════════════════════════╣
    ║  1. Registrar cliente                ║
    ║  2. Ver estadísticas                 ║
    ║  3. Buscar cliente                   ║
    ║  4. Gestionar agenda del día (Cola)  ║
    ║  5. Cola de urgentes (Extracciones)  ║
    ║  6. Salir                            ║
    ╚══════════════════════════════════════╝
    """)


def ejecutar_app():
    print("\nBienvenido al Sistema del Consultorio Odontológico")
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_cliente()
        elif opcion == "2":
            mostrar_estadisticas()
        elif opcion == "3":
            buscar_cliente()
        elif opcion == "4":
            menu_agenda()
        elif opcion == "5":
            menu_cola_urgentes()
        elif opcion == "6":
            print("Saliendo del sistema. ¡Hasta pronto!")
            break
        else:
            print("Opción inválida\n")
