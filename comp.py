import os
from collections import Counter
import heapq

class Nodo:
    def __init__(self, caracter=None, frecuencia=0):
        self.caracter = caracter
        self.frecuencia = frecuencia
        self.izquierda = None
        self.derecha = None

    def __lt__(self, otro):
        # Priorizar nodos con caracteres sobre subárboles cuando las frecuencias son iguales
        if self.frecuencia == otro.frecuencia:
            if self.caracter is not None and otro.caracter is not None:
                return self.caracter < otro.caracter  # Ordenar caracteres por valor ASCII
            return self.caracter is not None  # Los caracteres tienen prioridad sobre subárboles
        return self.frecuencia < otro.frecuencia

def construir_arbol(frecuencias):
    """Construye el árbol de Huffman a partir de las frecuencias."""
    heap = [Nodo(caracter, freq) for caracter, freq in frecuencias.items()]
    heapq.heapify(heap)
    print(f"Nodos iniciales en el heap: {len(heap)}")  # Depuración

    while len(heap) > 1:
        nodo1 = heapq.heappop(heap)
        nodo2 = heapq.heappop(heap)
        nuevo_nodo = Nodo(frecuencia=nodo1.frecuencia + nodo2.frecuencia)
        nuevo_nodo.izquierda = nodo1
        nuevo_nodo.derecha = nodo2
        heapq.heappush(heap, nuevo_nodo)
        print(f"Combinando nodos: ({nodo1.frecuencia}, {nodo2.frecuencia}) -> {nuevo_nodo.frecuencia}")  # Depuración

    print(f"Nodos finales en el heap (debería ser 1): {len(heap)}")  # Depuración
    print(f"Número total de nodos frecuencia creados: {len(frecuencias) - 1}")  # Depuración
    return heap[0]  #
def generar_codigos(raiz):
    """Genera los códigos de Huffman para cada carácter."""
    codigos = {}

    def recorrer(nodo, codigo_actual):
        if nodo is None:
            return
        if nodo.caracter is not None:  # Nodo terminal
            codigos[nodo.caracter] = codigo_actual
        recorrer(nodo.izquierda, codigo_actual + '0')
        recorrer(nodo.derecha, codigo_actual + '1')

    recorrer(raiz, '')
    return codigos

def calcular_bits_sobrantes(bits_totales):
    """Calcula los bits sobrantes."""
    return (8 - (bits_totales % 8)) % 8

def comprimir(archivo):
    try:
        with open(archivo, 'rb') as f:  # Leer en modo binario
            contenido = f.read()

        # Debugging: Verify the exact content of the file after reading
        print(f"Contenido del archivo leído: {contenido}")

        # Calcular frecuencias
        frecuencias = Counter(contenido)
        print(f"Frecuencias calculadas: {frecuencias}")  # Depuración

        # Filtrar caracteres con frecuencia cero
        frecuencias = {caracter: freq for caracter, freq in frecuencias.items() if freq > 0}
        print(f"Frecuencias filtradas: {frecuencias}")  # Depuración

        # Construir el árbol de Huffman
        raiz = construir_arbol(frecuencias)
        print("Árbol de Huffman construido correctamente.")  # Depuración

        # Generar códigos de Huffman
        codigos = generar_codigos(raiz)
        print(f"Códigos de Huffman generados: {codigos}")  # Depuración

        # Debugging: Verify the mapping of each byte in the content to its Huffman code
        for byte in contenido:
            if byte not in codigos:
                print(f"Advertencia: Byte {byte} no tiene un código asignado en el diccionario.")
            else:
                print(f"Byte {byte}: Código {codigos[byte]}")

        # Generar el ZIP
        zip_bits = ''.join(codigos[byte] for byte in contenido)
        print(f"Bits del ZIP generados: {zip_bits[:64]}... (truncado)")  # Depuración

        # Calcular bits sobrantes
        bits_totales = len(zip_bits)
        bits_sobrantes = calcular_bits_sobrantes(bits_totales)
        print(f"Bits totales: {bits_totales}, Bits sobrantes: {bits_sobrantes}")  # Depuración

        # Verificar integridad de zip_bits antes de la conversión
        if len(zip_bits) % 8 != 0:
            print(f"Advertencia: zip_bits no está alineado a bytes. Longitud: {len(zip_bits)}")
        print(f"zip_bits antes de la conversión: {zip_bits}")

        # Asegurar que los bits sobrantes se añadan al final del último byte
        zip_bits += '0' * bits_sobrantes
        print(f"zip_bits ajustados con bits sobrantes: {zip_bits}")

        # Convertir ZIP a bytes
        zip_bytes = int(zip_bits, 2).to_bytes((bits_totales + 7) // 8, byteorder='big')
        print(f"zip_bytes después de la conversión: {zip_bytes}")

        # Serializar el árbol en preorden
        def serializar_arbol(nodo):
            if nodo.caracter is not None:  # Nodo terminal
                val = nodo.caracter if isinstance(nodo.caracter, int) else ord(nodo.caracter)
                if not (0 <= val <= 255):
                    print(f"Error: Nodo terminal con valor fuera de rango: {val}")
                    raise ValueError(f"Nodo terminal con valor fuera de rango: {val}")
                return [1, val]
            else:  # Nodo frecuencia
                return [0, 0] + serializar_arbol(nodo.izquierda) + serializar_arbol(nodo.derecha)

        tree_bits = serializar_arbol(raiz)

        # Calcular NF basado en nodos frecuencia en lugar de caracteres únicos
        nf = len(frecuencias) - 1  # Número de nodos frecuencia creados
        print(f"Número de frecuencias (NF): {nf}")  # Depuración

        if nf > 255:
            print(f"Error: NF ({nf}) excede el rango permitido de un byte (0-255)")
            raise ValueError(f"NF ({nf}) excede el rango permitido de un byte (0-255)")

        # Crear el archivo comprimido
        archivo_salida = archivo + '.pkz'
        with open(archivo_salida, 'wb') as f:
            # Escribir NF
            print(f"Escribiendo NF: {nf}")  # Depuración
            f.write(bytes([nf]))

            # Escribir TREE
            # Asegurar que los datos del árbol se escriban correctamente
            for i in range(0, len(tree_bits), 2):
                b1, b2 = tree_bits[i], tree_bits[i+1]
                if not (0 <= b1 <= 255 and 0 <= b2 <= 255):
                    print(f"Error: intentó escribir bytes fuera de rango en el árbol: {b1}, {b2}")
                    raise ValueError(f"Intentó escribir bytes fuera de rango en el árbol: {b1}, {b2}")
                f.write(bytes([b1, b2]))

            # Calcular bits significativos
            bits_significativos = bits_totales % 8
            if bits_significativos == 0:
                bits_significativos = 8  # Si es 0, significa que todos los bits del último byte son significativos
            print(f"Bits significativos (BS): {bits_significativos}")  # Depuración

            # Escribir BS
            f.write(bytes([bits_significativos]))

            # Escribir ZIP
            print(f"Escribiendo ZIP de tamaño: {len(zip_bytes)} bytes")  # Depuración
            f.write(zip_bytes)

        # Mostrar los datos escritos para depuración
        print(f"[NF]: {nf}")
        print(f"[TREE]: {tree_bits}")
        print(f"[BS]: {bits_significativos}")

        # Convertir ZIP a formato binario para depuración y mostrar completo
        zip_bits_debug = ''.join(format(byte, '08b') for byte in zip_bytes)
        print(f"[ZIP]: {zip_bits_debug}")

        print(f"Archivo comprimido guardado como {archivo_salida}")
    except Exception as e:
        print(f"Error durante la compresión: {e}")
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python comp.py <ruta_del_archivo_a_comprimir>")
    else:
        try:
            comprimir(sys.argv[1])
            print("Compresión exitosa.")
        except Exception as e:
            print(f"Error durante la compresión: {e}")