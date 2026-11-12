#!/usr/bin/env python3
r"""Contrôles locaux (remplacent .github/workflows/cross-compile-arm.yml, Actions coupé le 12/11/2026).

Usage : J:aude\venv\Scripts\python.exe controles_locaux.py [--chaine <dossier bin ARM>]
Chaîne cherchée : --chaine, puis ARM_GCC_BIN, puis PATH, puis emplacements usuels.
Sortie 0 = tout vert ; 1 = échec ; 3 = compilation non lancée (chaîne ARM absente).
"""
import argparse, glob, os, shutil, subprocess, sys, time

RACINE = os.path.dirname(os.path.abspath(__file__))
EXE = ".exe" if os.name == "nt" else ""
GCC = "arm-none-eabi-gcc" + EXE
USUELS = [
    r"C:\ST\STM32CubeIDE*\STM32CubeIDE\plugins\com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32*\tools\bin",
    r"C:\Program Files\Arm\GNU Toolchain*\bin",
    r"C:\Program Files (x86)\Arm\GNU Toolchain*\bin",
    r"C:\Program Files (x86)\GNU Arm Embedded Toolchain\*\bin",
    r"C:\Program Files\GNU Arm Embedded Toolchain\*\bin",
    r"C:\Program Files\STMicroelectronics\STM32Cube\STM32CubeIDE*\plugins\*gnu-tools-for-stm32*\tools\bin",
    r"C:\ProgramData\chocolatey\lib\gcc-arm-embedded\tools\*\bin",
]


def trouver_chaine(option):
    """Retourne (dossier bin ou None pour PATH, source) ou (None, None)."""
    for src, d in (("--chaine", option), ("ARM_GCC_BIN", os.environ.get("ARM_GCC_BIN"))):
        if d:
            if os.path.isfile(os.path.join(d, GCC)):
                return d, src
            print(f"Avertissement : {GCC} absent de {d} ({src})")
    if shutil.which("arm-none-eabi-gcc"):
        return None, "PATH"
    for motif in USUELS:
        for d in sorted(glob.glob(motif), reverse=True):
            if os.path.isfile(os.path.join(d, GCC)):
                return d, "emplacement usuel"
    return None, None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--chaine", help="dossier bin de la chaîne arm-none-eabi")
    a = p.parse_args()
    resultats = []  # (étape, statut, durée)

    def etape(nom, fonction):
        t = time.time()
        try:
            ok, detail = fonction()
        except Exception as e:  # noqa
            ok, detail = False, str(e)
        statut = "OK" if ok is True else ("NON LANCÉE (%s)" % detail if ok is None else "ÉCHEC (%s)" % detail)
        resultats.append((nom, statut, time.time() - t))
        print(f"[{nom}] {statut}")

    def fichiers():
        manquants = [f for f in ("Makefile", "STM32F469NIHx_FLASH.ld", "startup_stm32f469xx.s", "Src", "Inc")
                     if not os.path.exists(os.path.join(RACINE, f))]
        return (not manquants, "manquants : " + ", ".join(manquants))

    etape("Fichiers du projet", fichiers)

    d, src = trouver_chaine(a.chaine)
    make = shutil.which("make")
    env = dict(os.environ)
    if d:
        env["PATH"] = d + os.pathsep + env["PATH"]
        print(f"Chaîne ARM : {d} ({src})")

    def build():
        if not make:
            return False, "make introuvable"
        r = subprocess.run([make], cwd=RACINE, env=env)
        if r.returncode:
            return False, f"make code {r.returncode}"
        manq = [e for e in ("elf", "hex", "bin")
                if not os.path.isfile(os.path.join(RACINE, "build", f"f469-usbaudio-ex2.{e}"))]
        return (not manq, "sortie absente : " + ", ".join(manq))

    if d is None and src is None:
        etape("Compilation croisée ARM (make)", lambda: (None, "chaîne ARM absente sur ce PC"))
    else:
        etape("Compilation croisée ARM (make)", build)

    print("\n## Résumé des contrôles\n\n| Étape | Statut | Durée |\n|---|---|---|")
    for n, s, t in resultats:
        print(f"| {n} | {s} | {t:.1f} s |")
    if any(s.startswith("ÉCHEC") for _, s, _ in resultats):
        return 1
    if any(s.startswith("NON LANCÉE") for _, s, _ in resultats):
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
