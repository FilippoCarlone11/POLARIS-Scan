#!/bin/bash

# Ciclo sui benchmark da b01 a b22
for i in $(seq -w 1 22); do
  folder="b${i}"
  
  if [ -d "$folder" ]; then
    echo "=== Entro in $folder ==="
    cd "$folder" || exit
    
    # Esecuzione per le tecnologie scelte
    for tech in 45nm; do
      polaris "b${i}_${tech}.tcl" \
        > "b${i}_${tech}_stdout.log" \
        2> "b${i}_${tech}_stderr.log" 
    done
    
    cd ..
  else
    echo "Attenzione: cartella $folder non trovata, salto..."
  fi
done