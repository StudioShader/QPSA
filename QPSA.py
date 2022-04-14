from qiskit import BasicAer, QuantumCircuit, ClassicalRegister, QuantumRegister, IBMQ, Aer, assemble, transpile, execute
from qiskit.algorithms import NumPyMinimumEigensolver, VQE
from qiskit.algorithms.optimizers import SPSA
from qiskit.circuit.library import TwoLocal
from qiskit.providers.aer import AerSimulator
from qiskit.quantum_info import Pauli, Statevector
from qiskit.quantum_info import Statevector
from qiskit.transpiler.passes import Unroller
from qiskit.utils import QuantumInstance, algorithm_globals
from qiskit.visualization import plot_histogram


# provider = IBMQ.load_account()


def initialize_s(qc, qubits):
    """Apply a H-gate to 'qubits' in qc"""
    for q in qubits:
        qc.h(q)
    return qc


def diffuser(nqubits):
    qc = QuantumCircuit(nqubits)
    # Apply transformation |s> -> |00..0> (H-gates)
    for qubit in range(nqubits):
        qc.h(qubit)
    # Apply transformation |00..0> -> |11..1> (X-gates)
    for qubit in range(nqubits):
        qc.x(qubit)
    # Do multi-controlled-Z gate
    qc.h(nqubits - 1)
    qc.mct(list(range(nqubits - 1)), nqubits - 1)  # multi-controlled-toffoli
    qc.h(nqubits - 1)
    # Apply transformation |11..1> -> |00..0>
    for qubit in range(nqubits):
        qc.x(qubit)
    # Apply transformation |00..0> -> |s>
    for qubit in range(nqubits):
        qc.h(qubit)
    # We will return the diffuser as a gate
    U_s = qc.to_gate()
    U_s.name = "U$_s$"
    return U_s


def partial_diffuser(nqubits, m):
    qc = QuantumCircuit(nqubits)
    # Apply transformation |s> -> |00..0> (H-gates)
    for qubit in range((nqubits - m), nqubits):
        qc.h(qubit)
    # Apply transformation |00..0> -> |11..1> (X-gates)
    for qubit in range((nqubits - m), nqubits):
        qc.x(qubit)
    # Do multi-controlled-Z gate
    qc.h(nqubits - 1)
    qc.mct(list(range((nqubits - m), nqubits - 1)), nqubits - 1)  # multi-controlled-toffoli
    qc.h(nqubits - 1)
    # Apply transformation |11..1> -> |00..0>
    for qubit in range((nqubits - m), nqubits):
        qc.x(qubit)
    # Apply transformation |00..0> -> |s>
    for qubit in range((nqubits - m), nqubits):
        qc.h(qubit)
    # We will return the diffuser as a gate
    U_s = qc.to_gate()
    U_s.name = "U$_s$"
    return U_s


# As all experiments depend on the length of circuit it is very important to see the length of the Oracles,
# as it depends heavily on the task that we are trying to solve. In our case we are mocking the task
# but still the length is exp from n as we use Toffoli(n).
# Also we are using another additional qubit for amplitude amplification realization for convenience.
# When it comes to run on a real devices we should use something smarter then Toffoli(n).
# While we make simple translation of our circuit, Toffoli gate probably translates in something huge (n^3 or bigger).
# Which we theoretically can compensate with auxiliary qubits.

# initialize the Oracle in single state |s> (the state is pure and given in form of [010011...] of len = n)
# additional qubit should be realized as (qc.initialize([1, -1]/np.sqrt(2), output_qubit))
def oracle(state, n: int):
    var_qubits = QuantumRegister(n, name='v')
    output_qubit = QuantumRegister(1, name='out')  # additional qubit
    qc = QuantumCircuit(var_qubits, output_qubit)

    for i in range(n):
        if state[i] == 0:
            qc.x(i)

    # Flip 'output' bit if all clauses are satisfied
    qc.mct(var_qubits, output_qubit)

    for i in range(n):
        if state[i] == 0:
            qc.x(i)

    Oracle = qc.to_gate()
    Oracle.name = "O"
    return Oracle


def grover_operator(n, state):
    grover = QuantumCircuit(n + 1)
    grover.append(oracle(state, n), range(n + 1))
    grover.append(diffuser(n), range(n))
    Grover = grover.to_gate()
    Grover.name = "G_" + str(n)
    return Grover


def local_grover_operator(n, m, state):
    grover = QuantumCircuit(n + 1)
    grover.append(oracle(state, n), range(n + 1))
    grover.append(partial_diffuser(n, m), range(n))
    Grover = grover.to_gate()
    Grover.name = "G_" + str(n) + "_" + str(m)
    return Grover


def design_grover_circuit(n, operator_count, state):
    grover_circuit = QuantumCircuit(n + 1, n)
    grover_circuit = initialize_s(grover_circuit, range(n))
    grover_circuit.x(n)
    grover_circuit.h(n)
    for i in range(operator_count):
        grover_circuit.append(grover_operator(n, state), range(n + 1))
    return grover_circuit


def design_partial_grover_circuit(n, m, vector_j, state):
    #     j =[j1, j2, j3 ...] powers for grover operators global and partial going in turn
    #     last number j_q - always for the local grover operator. Will stand first in the circuit.
    grover_circuit = QuantumCircuit(n + 1, n)
    grover_circuit = initialize_s(grover_circuit, range(n))
    grover_circuit.x(n)
    grover_circuit.h(n)
    partial = True
    for j_i in vector_j:
        for power in range(j_i):
            if partial:
                grover_circuit.append(local_grover_operator(n, m, state), range(n + 1))
            else:
                grover_circuit.append(grover_operator(n, state), range(n + 1))
        partial = (not partial)
    return grover_circuit


def classic_grover_stats(qcircuit, state, n, back):
    qubit_count = n + 1
    m = len(state)
    #     first we evolve exact state
    base_state = Statevector.from_int(0, 2 ** qubit_count)
    evolved_state = base_state.evolve(qcircuit)
    dict_ = evolved_state.probabilities_dict()
    #     now we find P_theoretical
    #     strState = ''.join(str(e) for e in state)
    strState = ''
    for i in range(m):
        strState += str(state[m - i - 1])
    P_theoretical = 0
    # print(dict_)
    for strin in dict_:
        if strin[(qubit_count - m):] == strState:
            P_theoretical += dict_[strin]
    # print("P_theoretical: ", P_theoretical)
    #     now for simulation. We will mimimc noise model from real backend device ibmq_quito
    # back = provider.get_backend("ibmq_quito")
    #     now we add measures to our circuit
    qcircuit.measure(range(n), range(n - 1, -1, -1))
    optimized_3 = transpile(qcircuit, backend=back, seed_transpiler=11, optimization_level=3)
    print('gates = ', optimized_3.count_ops())
    # print('depth = ', optimized_3.depth())
    depth = optimized_3.depth()
    backend = AerSimulator.from_backend(back)
    result = backend.run(optimized_3).result()
    #     find P_actual
    strState = ''.join(str(e) for e in state)
    m = len(state)
    counts = result.get_counts(0)
    summ = 0
    res = 0
    max_ = 0
    for strin in counts:
        summ += counts[strin]
        if strin == strState:
            res += counts[strin]
        else:
            if max_ < counts[strin]:
                max_ = counts[strin]
    P_actual = res / summ
    S = res / max_
    # print("S: ", S)
    # print(summ, res)
    # print("P_actual: ", res * 100 / summ, "%")
    # return plot_histogram(counts, title='counts on quito')
#     return (Pt, Pactual, selectivity, depth, plot_histogram)
    return (P_theoretical, P_actual, S, depth, plot_histogram(counts, title='counts on quito'))


def QPSA_stats(qcircuit, partial_state, n, back, measure_first=True):
    #     when measure_first value id false we will measure the last m qubits instead of first.
    #     Thus the length of partial_state should be m

    P_theoretical = 0
    qubit_count = n + 1
    m = len(partial_state)

    #     final measurements added only to partial state from 0 to (n-m)
    #     first we evolve exact state
    base_state = Statevector.from_int(0, 2 ** qubit_count)
    evolved_state = base_state.evolve(qcircuit)
    dict_ = evolved_state.probabilities_dict()
    if measure_first:
        #     now we find P_theoretical
        #     strState = ''.join(str(e) for e in state)
        strState = ''
        for i in range(m):
            strState += str(partial_state[m - i - 1])
        for strin in dict_:
            if strin[(qubit_count - m):] == strState:
                P_theoretical += dict_[strin]
        print("P_theoretical: ", P_theoretical)
    else:
        strState = ''
        for i in range(m):
            strState += str(partial_state[m - i - 1])
        for strin in dict_:
            if strin[(qubit_count - n):(qubit_count - n) + m] == strState:
                P_theoretical += dict_[strin]
        print("P_theoretical: ", P_theoretical)
    # now for simulation. We will mimimc noise model from real backend device ibmq_quito
    # back = provider.get_backend("ibmq_quito")
    if measure_first:
        #     now we add measures to our circuit
        qcircuit.measure(range(m), range(m - 1, -1, -1))
    else:
        qcircuit.measure(range((n - m), n), range(m - 1, -1, -1))

    optimized_3 = transpile(qcircuit, backend=back, seed_transpiler=11, optimization_level=3)
    print('gates = ', optimized_3.count_ops())
    depth = optimized_3.depth()
    print('depth = ', depth)
    backend = AerSimulator.from_backend(back)
    result = backend.run(optimized_3).result()

    #     find P_actual
    strState = ''.join(str(e) for e in partial_state)
    counts = result.get_counts(0)
    summ = 0
    res = 0
    max_ = 0
    for strin in counts:
        summ += counts[strin]
        if strin[n - m:] == strState:
            res += counts[strin]
        else:
            if max_ < counts[strin]:
                max_ = counts[strin]

    P_actual = res / summ
    S = res / max_
    print("S: ", S)
    print(summ, res)
    print("P_actual: ", res * 100 / summ, "%")
    #     return (Pt, Pactual, selectivity, depth, plot_histogram)
    return (P_theoretical, P_actual, S, depth, plot_histogram(counts, title='counts on quito'))


def design_and_test_two_stage(n, m1, vector_j1, m2, vector_j2, state, back):
    first_stage_circuit = design_partial_grover_circuit(n, m1, vector_j1, state)
    partial_state = state[:(n - m1)]
    (P_theoretical_first, P_actual_first, S_first, depth_first, _) = QPSA_stats(first_stage_circuit,
                                                                                partial_state, n, back)
    second_stage_circuit = design_partial_grover_circuit(n, m2, vector_j2, state)
    partial_state = state[(n - m1):]
    (P_theoretical_second, P_actual_second, S_second, depth_second, _) = QPSA_stats(second_stage_circuit,
                                                                                    partial_state,
                                                                                    n, back, False)
    #     return (selectivity, R_IBM, depth, "expected deapth") expected deapth defined as goes
    return (min([S_first, S_second]),
            P_actual_first * P_actual_second / (P_theoretical_first * P_theoretical_second),
            depth_first + depth_second,
            (depth_first + depth_second) / (P_actual_first * P_actual_second))