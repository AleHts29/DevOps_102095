"""
Simulador de Git — plantilla para el ejercicio del Módulo 2.

Completá las cinco reglas donde dice TODO.
No uses librerías de Git: esto es un simulador con un contador.

ENTRADA (por stdin):
    primera línea: N, cantidad de comandos
    siguientes N líneas: un comando por línea

SALIDA:
    una línea con: rama_actual cantidad_de_commits
"""
import sys


def main():
    datos = sys.stdin.read().split("\n")
    n = int(datos[0].strip())

    ramas = {}      # nombre de rama -> cantidad de commits
    actual = None   # nombre de la rama en la que estamos parados

    for i in range(1, n + 1):
        partes = datos[i].strip().split()
        if not partes:
            continue
        cmd = partes[0]
        arg = partes[1] if len(partes) > 1 else None

        if cmd == "clone":
            # TODO: estado inicial → rama "main" con 0 commits
            pass

        elif cmd == "commit":
            # TODO: sumar 1 a la rama actual
            pass

        elif cmd == "branch":
            # TODO: crear la rama con el MISMO conteo que la actual.
            #       Ojo: NO cambia la rama actual.
            pass

        elif cmd == "checkout":
            # TODO: cambiar de rama. Si la rama no existe, ignorar.
            pass

        elif cmd == "merge":
            # TODO: sumar el conteo de la otra rama al de la actual.
            pass

    print(f"{actual} {ramas[actual]}")


main()
