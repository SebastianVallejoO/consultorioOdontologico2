def pedir_opcion(mensaje, opciones):
    while True:
        valor = input(mensaje).lower()
        if valor in opciones:
            return valor
        else:
            print(f"Opción inválida. Opciones válidas: {', '.join(opciones)}")


def pedir_entero(mensaje):
    while True:
        try:
            valor = int(input(mensaje))
            if valor > 0:
                return valor
            else:
                print("Debe ser mayor que 0")
        except:
            print("Ingrese un número válido")

def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        else:
            print("Este campo no puede estar vacío")

def pedir_numero(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit():
            return valor
        else:
            print("Solo se permiten números")


def pedir_fecha(mensaje):
    while True:
        valor = input(mensaje).strip()

        partes = valor.split("/")

        if len(partes) != 3:
            print("Formato inválido. Use dd/mm/aaaa")
            continue

        dia, mes, anio = partes

        if not (dia.isdigit() and mes.isdigit() and anio.isdigit()):
            print("La fecha solo debe contener números")
            continue

        dia = int(dia)
        mes = int(mes)
        anio = int(anio)

        if 1 <= dia <= 31 and 1 <= mes <= 12 and anio > 1900:
            return valor
        else:
            print("Fecha inválida")