import argparse, re
import quasimodo
from qiskit import qasm3
from qiskit import QuantumCircuit

def run_qasm3(args):
    qc = qasm3.loads(args.filename)

    transpilation_started = False

    qreg_highest_offset = 0
    qreg_offset = dict()

    def convert_qubit(qreg, qubit, qreg_offset):
        return str(qreg_offset[qreg] + qubit)
    
    n = 10
    qc = quasimodo.QuantumCircuit("CFLOBDD", n, args.seed)

    for line in qc.splitlines():
        line = line.rstrip()

        if re.match(r"h \w+\[\d+\];", line):
            match = re.match(r"h (\w+)\[(\d+)\];", line)
            qreg = match.group(1)
            qubit = int(match.group(2))
            qubit = convert_qubit(qreg, qubit, qreg_offset) 
            qc.h(qubit)

        elif re.match(r"s \w+\[\d+\];", line):
            match = re.match(r"h (\w+)\[(\d+)\];", line)
            qreg = match.group(1)
            qubit = int(match.group(2))
            qubit = convert_qubit(qreg, qubit, qreg_offset) 
            qc.s(qubit)

        elif re.match(r"cx \w+\[\d+\], \w+\[\d+\];", line):
            match = re.match(r"cx (\w+)\[(\d+)\], (\w+)\[(\d+)\];", line)
            qreg1 = match.group(1)
            qubit1 = int(match.group(2))
            qreg2 = match.group(3)
            qubit2 = int(match.group(4))
            ctqc_transpiled += "CNOT " + convert_qubit(qreg1, qubit1, qreg_offset) + " " + convert_qubit(qreg2, qubit2, qreg_offset) + "\n"

        elif re.match(r"rz(.*) \w+\[\d+\];", line):
            match = re.match(r"rz\((.*)\) (\w+)\[(\d+)\];", line)
            angle = match.group(1)
            qreg = match.group(2)
            qubit = int(match.group(3))
            ctqc_transpiled += "Rz(" + angle + ") " + convert_qubit(qreg, qubit, qreg_offset) + "\n"

        elif re.match(r".*measure \w+\[\d+\];", line):
            match = re.match(r".*measure (\w+)\[(\d+)\];", line)
            qreg = match.group(1)
            qubit = int(match.group(2))
            ctqc_transpiled += "M " + convert_qubit(qreg, qubit, qreg_offset) + "\n"
        
        elif re.match(r"^qubit\[\d+\] \w+;", line):
            match = re.match(r"^qubit\[(\d+)\] (\w+);", line)
            n_qubits = int(match.group(1))
            qreg = match.group(2)

            qreg_offset[qreg] = qreg_highest_offset
            qreg_highest_offset += n_qubits

        # Ignore barriers
        elif re.match(r"barrier.*", line):
            continue
    
        # Ignore classical registers
        elif re.match(r"bit.*", line):
            continue

        else: 
            if transpilation_started: 
                raise RuntimeError(f"Cannot convert \"{line}\".")
            else:
                continue
        
        transpilation_started = True





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate CFLOBDD python binding code.')
    parser.add_argument('-f', '--filename')
    parser.add_argument('-s', '--seed', default=1)
    parser.add_argument('-m', '--measurement', choices=['firstzero', 'allzero'])
    args = parser.parse_args()
    run_qasm3(args)
