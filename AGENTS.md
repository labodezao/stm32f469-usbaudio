# Consignes pour les agents

GitHub Actions est coupé (12/11/2026). Ne jamais le réactiver ni relancer un workflow.

Contrôles : `J:\claude\venv\Scripts\python.exe controles_locaux.py`, en local, avant toute fusion.
La chaîne ARM (`arm-none-eabi-gcc`) est requise. Indiquer son dossier bin par `--chaine <dossier>`
ou la variable `ARM_GCC_BIN` ; sinon le PATH. Sans chaîne, la compilation est « NON LANCÉE » (code 3, pas un vert).

Dans la PR : coller le résumé Markdown du script. Puis `gh pr merge`.
