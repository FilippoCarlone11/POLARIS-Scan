#!/bin/bash

# Ciclo sui benchmark da b01 a b22
for i in $(seq -w 1 22); do
  folder="b${i}"
  
  if [ -d "$folder" ]; then
    echo "=== Entro in $folder ==="
    cd "$folder" || exit
    
    # Esecuzione per le tecnologie scelte
    mkdir -p log
    for tech in 15nm 45nm 130nm; do
      polaris "b${i}_${tech}.tcl" \
        > "log/b${i}_${tech}_stdout.log" \
        2> "log/b${i}_${tech}_stderr.log" 
    done
    
    cd ..
  else
    echo "Attenzione: cartella $folder non trovata, salto..."
  fi
done