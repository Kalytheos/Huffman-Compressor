# Huffman Compressor in Python

A file compressor and decompressor based on **Huffman's algorithm**, which allows reducing the size of any type of file through variable-length encoding without information loss.

## 📋 Description

This project implements the Huffman compression algorithm, developed by David A. Huffman in 1952. The algorithm uses variable-length codes to represent bytes, assigning shorter codes to more frequent bytes and longer codes to less frequent ones, achieving efficient compression.

### How does the Huffman algorithm work?

1. **Frequency Analysis**: Calculate the frequency of occurrence of each byte in the original file.
2. **Binary Tree Construction**: Build a Huffman tree using a priority queue (heap):
   - Each byte is a leaf of the tree
   - Internal nodes represent the sum of frequencies of their children
   - Nodes with lower frequency are combined first
3. **Code Generation**: Traverse the tree to assign binary codes:
   - Left = `0`
   - Right = `1`
4. **Compression**: Replace original bytes with their Huffman codes.

## 🚀 Features

- ✅ Compression of any file type (text, binary, multimedia)
- ✅ Decompression with exact restoration of the original file
- ✅ Custom `.pkz` format (Package Zip)
- ✅ Huffman tree serialization for reconstruction
- ✅ Efficient handling of padding bits
- ✅ Detailed debugging messages

## 📦 Compressed File Structure (.pkz)

The `.pkz` format has the following structure:

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│     NF      │    TREE     │     BS      │     ZIP     │
│   (1 byte)  │  (variable) │   (1 byte)  │  (variable) │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Components:

- **NF (Number of Frequencies)**: 1 byte indicating the number of frequency nodes in the tree (N-1, where N is the number of unique bytes).
- **TREE**: Preorder serialization of the Huffman tree:
  - Frequency node: `[0x00, 0x00]` followed by its left and right children
  - Terminal node: `[0x01, byte]` where byte is the ASCII/binary value
- **BS (Significant Bits)**: 1 byte indicating how many bits of the last ZIP byte are valid (1-8).
- **ZIP**: The compressed data in binary format.

## 🛠️ Requirements

- Python 3.6 or higher
- Standard libraries: `os`, `collections`, `heapq`

No external dependencies required.

## 📖 Usage

### Compress a file

```bash
python comp.py <file_path>
```

**Example:**
```bash
python comp.py document.txt
```

This will generate `document.txt.pkz` in the same directory.

### Decompress a file

```bash
python desc.py <file_path.pkz>
```

**Example:**
```bash
python desc.py document.txt.pkz
```

This will restore the original file `document.txt`.

## 💡 Usage Examples

### Example 1: Compress a text file

```bash
python comp.py letter.txt
```

**Output:**
```
Contenido del archivo leído: b'Hello world...'
Frecuencias calculadas: Counter({72: 1, 111: 2, 108: 1, ...})
Árbol de Huffman construido correctamente.
Códigos de Huffman generados: {72: '000', 111: '01', ...}
Archivo comprimido guardado como letter.txt.pkz
Compresión exitosa.
```

### Example 2: Decompress a file

```bash
python desc.py letter.txt.pkz
```

**Output:**
```
[NF]: 15
[TREE]: ['00000000', '00000000', ...]
[BS]: 5
Archivo descomprimido guardado como letter.txt
Descompresión exitosa.
```

## 📊 Performance

The Huffman algorithm is especially effective with files that have:
- Non-uniform byte distribution
- Repetitive patterns
- Text with frequent characters

**Note:** Small files or files with uniform distribution may result in similar or slightly larger sizes due to Huffman tree overhead.

## 🔍 Implementation Details

### Node Structure

```python
class Nodo:
    def __init__(self, caracter=None, frecuencia=0):
        self.caracter = caracter        # Represented byte (None for internal nodes)
        self.frecuencia = frecuencia    # Frequency of occurrence
        self.izquierda = None           # Left child
        self.derecha = None             # Right child
```

### Tree Construction

A **min-heap** is used to build the tree efficiently:
1. Insert all bytes with their frequencies
2. Extract the two nodes with the lowest frequency
3. Create a new node with the sum of both frequencies
4. Repeat until there is only one node (the root)

### Padding Bits Handling

Since files are stored in bytes (8 bits), but Huffman codes may not be multiples of 8, **padding bits** are calculated:

```python
bits_sobrantes = (8 - (bits_totales % 8)) % 8
```

These bits are filled with zeros and recorded in the `BS` field to discard them during decompression.

## 🧪 Testing

You can test the compressor with different file types:

```bash
# Text
python comp.py example.txt
python desc.py example.txt.pkz

# Binary
python comp.py image.png
python desc.py image.png.pkz

# Video
python comp.py video.mp4
python desc.py video.mp4.pkz
```

## ⚠️ Limitations

- **Maximum NF**: 255 frequency nodes (up to 256 unique bytes)
- **With Very small files**: The file may increase in size due to tree overhead
- **Already compressed files**: Formats like `.zip`, `.jpg`, `.mp3` do not benefit significantly

## 🐛 Debugging

Both scripts include detailed debugging messages showing:
- Calculated frequencies
- Step-by-step tree construction
- Generated Huffman codes
- `.pkz` file structure
- ZIP bits

To get less output, you can comment out the `print()` lines in the code.

## 📚 References

- [Huffman Coding - Wikipedia](https://en.wikipedia.org/wiki/Huffman_coding)
- Huffman, D. A. (1952). "A Method for the Construction of Minimum-Redundancy Codes"

## 📄 License

This project is open source and available for educational purposes.

