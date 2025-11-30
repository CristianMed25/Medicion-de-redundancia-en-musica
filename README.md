# Music Entropy Toolkit

Herramienta en Python 3.10+ para medir entropía, redundancia y complejidad en música simbólica (MIDI o secuencias JSON/CSV).

## Instalación

```bash
python -m pip install -r requirements.txt
# opcional para desarrollo
python -m pip install -e .[dev]
```

## Uso del CLI

Comandos principales:

- Analizar un archivo:
  ```bash
  python -m music_entropy analyze --input path/to/file.mid --input-type midi \
      --markov-order 2 --window-size 16 --window-step 8 --local
  ```
- Analizar una carpeta:
  ```bash
  python -m music_entropy analyze-batch --input carpeta/ --input-type midi --pattern "*.mid"
  ```

Parámetros clave:
- `--markov-order`: orden k del modelo de Markov para Hk.
- `--time-unit`: resolución en beats para la cuadrícula rítmica en MIDI (ej. 0.25 = semicorchea).
- `--window-size` / `--window-step`: ventana y desplazamiento para entropías locales (`--local` las activa).
- `--output-csv`, `--local-csv`, `--output-json`: exportar métricas.

También puedes usar el entrypoint instalado: `music-entropy analyze ...`.

## Formatos de entrada

- **MIDI**: se elige la pista con más `note_on` (o configurable). Melodía = pitch MIDI por onset; ritmo binario en una rejilla.
- **JSON**: diccionario `{"melody": [...], "rhythm": [...]}`. Ejemplo en `examples/sample_sequence.json`.
- **CSV** (flexible): columnas `melody` y `rhythm` con secuencias separadas por espacio/coma, o bien columnas `type,sequence` con filas `melody` y `rhythm`.

## Métricas implementadas

- Entropía de Shannon H0.
- Entropía condicional Markov Hk (orden k).
- Entropía máxima Hmax = log2(q), q = tamaño del alfabeto.
- Redundancia R = Hmax - Hk.
- Complejidad de Lempel–Ziv (binaria) y versión normalizada.
- Índice de predictibilidad IP = 1 - (Hk / Hmax).
- Entropías locales por ventana deslizante.

## Ejemplos reproducibles

- **JSON ficticio** (`examples/sample_sequence.json`):
  ```bash
  python -m music_entropy analyze --input examples/sample_sequence.json --input-type json --markov-order 2 --local --window-size 4 --window-step 2
  ```
  Salida esperada:
  ```
  File: examples\sample_sequence.json
    H0: 2.2359
    Hk (order): 0.0000
    Hmax: 2.3219
    Redundancy: 2.3219
    LZC: 2
    LZC normalized: 0.8021
    Predictability (IP): 1.0000
    Local windows: 4
  ```

- **MIDI simple** (`examples/demo_melody.mid` generado con mido):
  ```bash
  python -m music_entropy analyze --input examples/demo_melody.mid --input-type midi --markov-order 1 --time-unit 0.25
  ```
  Salida esperada:
  ```
  File: examples\demo_melody.mid
    H0: 2.5850
    Hk (order): 0.0000
    Hmax: 2.5850
    Redundancy: 2.5850
    LZC: 2
    LZC normalized: 0.5693
    Predictability (IP): 1.0000
  ```

## Estructura del proyecto

```
music_entropy/
    __init__.py
    __main__.py
    analysis.py
    cli.py
    encoding.py
    entropy.py
    loader_midi.py
    loader_text.py
    lzc.py
tests/
    conftest.py
    test_encoding.py
    test_entropy.py
    test_loaders.py
    test_lzc.py
examples/
    sample_sequence.json
    demo_melody.mid
requirements.txt
pyproject.toml
README.md
```

## Pruebas

```bash
pytest -q
```
