#!/bin/bash

mkdir -p diff

for i in {1..6}; do
    echo "=== Running test $i ==="

    # Run the simulator
    python3 Vsim.py "tests_dakshina/sample$i.txt"

    # Compare disassembly outputs
    diff -w -B disassembly.txt "tests_dakshina/disassembly$i.txt" > "diff/disassembly_diff_$i.txt"

    # Compare simulation outputs
    diff -w -B simulation.txt "tests_dakshina/simulation$i.txt" > "diff/simulation_diff_$i.txt"

    echo "Diffs saved for test $i in diff/disassembly_diff_$i.txt and diff/simulation_diff_$i.txt"
    echo
done

echo "✅ All comparisons completed. Check the 'diff/' folder for results."
