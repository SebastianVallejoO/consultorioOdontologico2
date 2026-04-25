class Cola:
    """
    Estructura de datos Cola (FIFO - First In, First Out).
    Los clientes son atendidos en el orden en que llegan.
    """

    def __init__(self):
        self._elementos = []

    def enqueue(self, elemento):
        """Agrega un elemento al final de la cola."""
        self._elementos.append(elemento)

    def dequeue(self):
        """
        Elimina y retorna el primer elemento de la cola.
        Lanza un error si la cola está vacía.
        """
        if self.is_empty():
            raise IndexError("La cola está vacía. No hay clientes en la agenda.")
        return self._elementos.pop(0)

    def peek(self):
        """Retorna el primer elemento sin eliminarlo."""
        if self.is_empty():
            raise IndexError("La cola está vacía.")
        return self._elementos[0]

    def is_empty(self):
        """Retorna True si la cola no tiene elementos."""
        return len(self._elementos) == 0

    def size(self):
        """Retorna la cantidad de elementos en la cola."""
        return len(self._elementos)

    def to_list(self):
        """Retorna todos los elementos como lista (para mostrar la agenda)."""
        return list(self._elementos)

    def __str__(self):
        if self.is_empty():
            return "Cola vacía"
        return " -> ".join(
            f"{c.nombre} ({c.tipo_atencion})" for c in self._elementos
        )