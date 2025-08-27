import os

class Nodo:
    def __init__(self, caracter=None):
        self.caracter = caracter
        self.izquierda = None
        self.derecha = None

def reconstruir_arbol(datos_arbol):
    """Reconstruye el árbol binario a partir de los datos en pares de bytes."""
    def helper(iterador):
        try:
            byte1 = next(iterador)
            byte2 = next(iterador)

            if byte1 == '00000000' and byte2 == '00000000':  # Nodo frecuencia
                nodo = Nodo()
                nodo.izquierda = helper(iterador)
                nodo.derecha = helper(iterador)
                return nodo
            elif byte1 == '00000001':  # Nodo terminal
                return Nodo(caracter=chr(int(byte2, 2)))
            else:
                return None
        except StopIteration:
            # Si los datos del árbol están incompletos, devolvemos None
            return None
    
    iterador = iter(datos_arbol)
    return helper(iterador)

def imprimir_arbol(nodo, nivel=0):
    """Imprime la estructura del árbol para depuración."""
    if nodo is not None:
        print("  " * nivel + (f"Nodo terminal: {nodo.caracter}" if nodo.caracter else "Nodo frecuencia"))
        imprimir_arbol(nodo.izquierda, nivel + 1)
        imprimir_arbol(nodo.derecha, nivel + 1)

def decodificar_zip(arbol, zip_bits):
    """Decodifica el zip usando el árbol binario."""
    resultado = []
    nodo_actual = arbol
    for i, bit in enumerate(zip_bits):
        if nodo_actual is None:
            raise ValueError("El árbol no está correctamente construido.")
        
        if bit == '0':
            nodo_actual = nodo_actual.izquierda
        elif bit == '1':
            nodo_actual = nodo_actual.derecha
        
        if nodo_actual and nodo_actual.caracter is not None:  # Nodo terminal
            resultado.append(nodo_actual.caracter)
            nodo_actual = arbol  # Reinicia desde la raíz
    return ''.join(resultado)

def descomprimir(archivo):
    # Validar que el archivo tenga la extensión .pkz
    if not archivo.endswith('.pkz'):
        raise ValueError("El archivo no tiene la extensión .pkz esperada.")

    with open(archivo, 'rb') as f:
        # Leer el primer byte (NF)
        nf = int.from_bytes(f.read(1), 'big')
        
        # Calcular el tamaño del árbol
        tamanio_arbol = (nf + nf + 1) * 2
        
        # Leer los bytes del árbol
        datos_arbol = []
        for _ in range(tamanio_arbol // 2):  # Leer en pares de bytes
            byte1 = f.read(1)
            byte2 = f.read(1)
            if not byte1 or not byte2:
                raise ValueError("Datos del árbol incompletos.")
            bits1 = format(int.from_bytes(byte1, 'big'), '08b')
            bits2 = format(int.from_bytes(byte2, 'big'), '08b')
            datos_arbol.append(bits1)
            datos_arbol.append(bits2)
        
        # Reconstruir el árbol
        arbol = reconstruir_arbol(datos_arbol)
        if arbol is None:
            raise ValueError("El árbol no pudo ser reconstruido.")
        
        # Leer bits significativos
        bits_significativos = int.from_bytes(f.read(1), 'big')
        
        # Leer el zip
        zip_bytes = f.read()
        zip_bits = ''.join(format(byte, '08b') for byte in zip_bytes)
        if bits_significativos > 0:
            zip_bits = zip_bits[:-(8 - bits_significativos)]  # Ignorar bits no significativos
        
        # Mostrar los datos leídos para depuración
        print(f"[NF]: {nf}")
        print(f"[TREE]: {datos_arbol}")
        print(f"[BS]: {bits_significativos}")
        print(f"[ZIP]: {zip_bytes[:64]}... (truncado si es largo)")
        
        # Decodificar el zip
        resultado = decodificar_zip(arbol, zip_bits)
        
        # Determinar el nombre del archivo de salida
        nombre_salida = os.path.splitext(archivo)[0]  # Remover la extensión .pkz
        with open(nombre_salida, 'wb') as out:
            out.write(resultado.encode('latin1'))  # Restaurar la escritura original usando latin1
        print(f"Archivo descomprimido guardado como {nombre_salida}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python desc.py <ruta_del_archivo_a_descomprimir>")
    else:
        try:
            descomprimir(sys.argv[1])
            print("Descompresión exitosa.")
        except Exception as e:
            print(f"Error durante la descompresión: {e}")