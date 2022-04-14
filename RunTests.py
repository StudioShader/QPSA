import QPSA
from qiskit.visualization import plot_histogram


class ThreeQubitCases:
    def __init__(self, back):
        self.n = 3
        self.back = back

    def print_result(self, result):
        (P_theoretical, P_actual, selectivity, depth, histogram) = result
        print("P_theoretical: ", P_theoretical)
        print("P_actual: ", P_actual)
        print("selectivity: ", selectivity)
        print("depth: ", depth)
        print("R_IBM: ", P_actual/P_theoretical)
        print("expected depth: ", depth/P_actual)
        # print("histogram: ", histogram)
        # plot_histogram(histogram)

    def D2M3(self):
        m = 2
        j = [1]  # one partial operator applied
        state = [0, 1, 0]
        result_circuit = QPSA.design_partial_grover_circuit(self.n, m, j, state)
        result = QPSA.classic_grover_stats(result_circuit, state, self.n, self.back)
        self.print_result(result)
