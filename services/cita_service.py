from data.tarifas import TARIFAS
from structures.cola import Cola


def calcular_total(cliente):
    valor_cita = TARIFAS[cliente.tipo_cliente]["cita"]
    valor_atencion = TARIFAS[cliente.tipo_cliente]["atencion"][cliente.tipo_atencion]

    if cliente.tipo_atencion in ["Limpieza", "Diagnostico"]:
        cliente.cantidad = 1

    cliente.total = valor_cita + (valor_atencion * cliente.cantidad)


def contar_extracciones(clientes):
    return sum(1 for c in clientes if c.tipo_atencion.lower() == "extraccion")


def ingresos_totales(clientes):
    return sum(c.total for c in clientes)


def ordenar_clientes(clientes):
    return sorted(clientes, key=lambda c: c.total, reverse=True)


def contar_urgentes(clientes):
    return sum(1 for c in clientes if c.prioridad == "urgente")


def construir_cola_urgentes(clientes):
    """
    Genera una Cola con los clientes que cumplen:
      - Tipo de atención: extracción
      - Prioridad: urgente
    Ordenados por fecha de cita de la más cercana a la más lejana.
    """
    def parsear_fecha(fecha_str):
        try:
            dia, mes, anio = fecha_str.split("/")
            return (int(anio), int(mes), int(dia))
        except Exception:
            return (9999, 12, 31)

    filtrados = [
        c for c in clientes
        if c.tipo_atencion.lower() == "extraccion"
        and c.prioridad.lower() == "urgente"
    ]

    ordenados = sorted(filtrados, key=lambda c: parsear_fecha(c.fecha))

    cola_urgentes = Cola()
    for c in ordenados:
        cola_urgentes.enqueue(c)

    return cola_urgentes
