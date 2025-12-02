# Music Entropy Toolkit

Herramienta en Python 3.10+ para medir entropia, redundancia y complejidad en musica simbolica (MIDI o secuencias JSON/CSV).

## Instalacion

```bash
python -m pip install -r requirements.txt
# opcional para desarrollo
python -m pip install -e .[dev]
```

## Uso del CLI

Comandos principales:

- Analizar un archivo:
  ```bash
  python -m music_entropy analyze --input path/to/file.mid --input-type midi       --markov-order 2 --window-size 16 --window-step 8 --local --plot-dir outputs/plots
  ```
- Analizar una carpeta:
  ```bash
  python -m music_entropy analyze-batch --input carpeta/ --input-type midi --pattern "*.mid" --plot-dir outputs/plots
  ```
- Analizar una carpeta con gráfica comparativa:
  ```bash
  python -m music_entropy analyze-batch --input carpeta/ --input-type midi --pattern "*.mid" --plot-dir outputs/plots --batch-plot
  ```

Parametros clave:
- `--markov-order`: orden k del modelo de Markov para Hk.
- `--time-unit`: resolucion en beats para la cuadricula ritmica en MIDI (ej. 0.25 = semicorchea).
- `--window-size` / `--window-step`: ventana y desplazamiento para entropias locales (`--local` las activa).
- `--output-csv`, `--local-csv`, `--output-json`: exportar metricas numericas.
- `--plot-dir`: guarda automaticamente graficas PNG (globales y, si existen, locales) en la carpeta indicada.
- `--batch-plot`: genera una grafica comparativa de todos los archivos (solo para `analyze-batch`).

Tambien puedes usar el entrypoint instalado: `music-entropy analyze ...`.

## Graficas automaticas

El modulo `music_entropy.visualization` genera los siguientes tipos de graficos:

### Por archivo individual:
- **Perfil global**: barras con H0, Hk, Hmax, Redundancy, IP, LZC y LZC normalizada.
- **Entropias locales**: line plot con H0 y Hk por ventana (requiere `--local`).

### Para analisis de carpetas completas (con `--batch-plot`):
- **Promedios globales**: grafica de barras mostrando valores promedio de todas las metricas (H0, Hk, Hmax, Redundancia, Predictibilidad, LZC normalizada) calculados a partir de todos los archivos. Se guarda como `batch_comparison.png`.
- **Promedios de entropías locales**: grafica de lineas mostrando la evolucion temporal promedio de H0 y Hk por ventana (requiere `--local`). Se guarda como `batch_local_averages.png`.

Ejemplo rapido:
```bash
python -m music_entropy analyze --input examples/sample_sequence.json --input-type json --local --plot-dir reports/plots
```
Esto crea `reports/plots/sample_sequence_global.png` y, como se pidieron metricas locales, `reports/plots/sample_sequence_local.png`.

Ejemplo con carpeta completa:
```bash
python -m music_entropy analyze-batch --input examples/ --input-type midi --pattern "*.mid" --plot-dir reports/plots --batch-plot --local
```
Esto genera graficas individuales para cada archivo, una grafica de promedios globales `batch_comparison.png`, y una grafica de promedios de entropias locales `batch_local_averages.png`.

## Formatos de entrada

- **MIDI**: se elige la pista con mas `note_on` (o configurable). Melodia = pitch MIDI por onset; ritmo binario en una rejilla. La resolucion se controla con `--time-unit`.
- **JSON**: diccionario `{"melody": [...], "rhythm": [...]}`. Ejemplos en `examples/`.
- **CSV** (flexible): columnas `melody` y `rhythm` con secuencias separadas por espacio/coma, o bien columnas `type,sequence` con filas `melody` y `rhythm`.

## Metricas implementadas

- Entropia de Shannon H0.
- Entropia condicional Markov Hk (orden k).
- Entropia maxima Hmax = log2(q), q = tamano del alfabeto.
- Redundancia R = Hmax - Hk.
- Complejidad de Lempel-Ziv (binaria) y version normalizada.
- Indice de predictibilidad IP = 1 - (Hk / Hmax).
- Entropias locales por ventana deslizante.

## Ejemplos reproducibles

- **JSON ficticio** (`examples/sample_sequence.json`):
  ```bash
  python -m music_entropy analyze --input examples/sample_sequence.json --input-type json --markov-order 2 --local --window-size 4 --window-step 2 --plot-dir outputs/plots
  ```
  Salida esperada (valores aproximados):
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
  python -m music_entropy analyze --input examples/demo_melody.mid --input-type midi --markov-order 1 --time-unit 0.25 --plot-dir outputs/plots
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
    visualization.py
tests/
    conftest.py
    test_encoding.py
    test_entropy.py
    test_loaders.py
    test_lzc.py
examples/
    sample_sequence.json
    sample_sequence_2.json
    demo_melody.mid
requirements.txt
pyproject.toml
README.md
```

## Pruebas

```bash
pytest -q
```
