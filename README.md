# Analizador_sintactico

Un analizador léxico y sintáctico completo para un subconjunto del lenguaje Python, implementado desde cero sin usar herramientas externas como PLY o ANTLR.

## 📋 Descripción

Este proyecto implementa un compilador básico que realiza análisis léxico y sintáctico de código Python. Verifica tanto la estructura léxica (tokens) como la sintaxis del código, detectando errores y reportándolos con la línea y columna exactas donde ocurren.

## 🏗️ Arquitectura

El proyecto está dividido en varios módulos especializados:

### **1. Analizador Léxico (`lexer_core.py`)**
Convierte el código fuente en una secuencia de tokens. Reconoce:
- **Palabras clave**: `if`, `while`, `for`, `def`, `return`, etc.
- **Identificadores**: nombres de variables y funciones
- **Literales**: números enteros y cadenas de texto
- **Operadores**: aritméticos, lógicos, de comparación y de asignación
- **Delimitadores**: paréntesis, corchetes, llaves, comas, dos puntos
- **Comentarios**: líneas que comienzan con `#`

### **2. Definiciones de Tokens (`tokens_def.py`)**
Contiene las definiciones de:
- Palabras clave del lenguaje
- Operadores simples y compuestos
- Funciones auxiliares para clasificar caracteres

### **3. Verificador de Indentación (`indent_check.py`)**
Valida las reglas de indentación de Python:
- Solo espacios O solo tabulaciones (no mezcla)
- Múltiplos de 4 espacios
- Tabulaciones cuentan como 4 espacios
- Detecta saltos de indentación inválidos

### **4. Puente Léxico-Sintáctico (`bridge.py`)**
Transforma los tokens del lexer en una estructura más rica que incluye:
- Tokens `NEWLINE`: marca fin de línea lógica
- Tokens `INDENT`: indica aumento de indentación
- Tokens `DEDENT`: indica reducción de indentación
- Maneja correctamente paréntesis abiertos (no genera NEWLINE dentro de `()`, `[]`, `{}`)

### **5. Analizador Sintáctico (`sintactico.py`)**
Parser LL(1) recursivo descendente que verifica la estructura sintáctica del código según la gramática de Python. Reconoce:
- **Declaraciones compuestas**: `if`, `elif`, `else`, `while`, `for`, `def`
- **Declaraciones simples**: asignaciones, `return`, `pass`, `break`, `continue`
- **Expresiones**: aritméticas, lógicas, comparaciones, llamadas a funciones
- **Estructuras de datos**: listas, diccionarios, conjuntos, tuplas
- **Anotaciones de tipo**: `x: int = 5`
- **Parámetros con valores por defecto**: `def f(x=10):`

### **6. Sistema de Reporte (`reporte.py`)**
Coordina el análisis completo:
1. Verifica indentación
2. Ejecuta análisis léxico
3. Ejecuta análisis sintáctico
4. Genera mensaje de éxito o error

### **7. Programa Principal (`main.py`)**
Interfaz de línea de comandos que:
- Lee el archivo Python a analizar
- Ejecuta el análisis completo
- Imprime el resultado en consola
- Guarda el resultado en un archivo `.txt`

## 🚀 Uso

### Ejecución básica:
```bash
python main.py
```

El programa pedirá la ruta del archivo a analizar:
```
Dame el archivo para analizar: ejemplo_ok.py
```

### Salida exitosa:
```
El analisis sintactico ha finalizado exitosamente.
```

### Salida con error:
```
<2,1> Error sintactico: se encontro: "
"; se esperaba: ":".
```

## 📂 Ejemplos Incluidos

### **ejemplo_ok.py** ✅
Código sintácticamente correcto:
```python
def suma(a, b):
    return a + b

x = 3
y = 5
print(suma(x, y))
```

### **ejemplo_error.py** ❌
Código con error (falta dos puntos):
```python
def suma(a, b)
    return a + b
```

## 🔍 Características Destacadas

### ✨ Manejo de Errores Detallado
- Reporta la **línea y columna exacta** del error
- Indica qué se encontró y qué se esperaba
- Mensajes claros y descriptivos

### 📝 Soporte de Sintaxis Python
- Estructuras de control: `if/elif/else`, `while`, `for`
- Funciones con parámetros tipados y valores por defecto
- Anotaciones de retorno: `def f() -> int:`
- Expresiones complejas con precedencia de operadores
- Listas, diccionarios y conjuntos literales
- Indexación, acceso a atributos y llamadas a funciones

### 🎯 Validación Estricta
- No permite comas finales en listas literales: `[1, 2,]` ❌
- Verifica consistencia en el uso de espacios/tabs
- Valida incrementos de indentación de exactamente 4 espacios
- Maneja correctamente expresiones multi-línea con paréntesis


## 📊 Flujo de Análisis

```
Archivo .py
    ↓
[Verificación de Indentación]
    ↓
[Análisis Léxico - Tokens]
    ↓
[Inserción INDENT/DEDENT]
    ↓
[Análisis Sintáctico - Parser]
    ↓
Resultado (éxito/error) → Archivo .txt
```


