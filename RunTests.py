import QPSA
from qiskit.visualization import plot_histogram


class ThreeQubitCases:
    def __init__(self, back, simulator, state=None):
        if state is None:
            state = [0, 1, 0]
        self.n = 3
        self.back = back
        self.state = state
        self.simulator = simulator

    def print_result(self, result):
        (P_theoretical, P_actual, selectivity, depth, histogram) = result
        print("P_theoretical: ", P_theoretical)
        print("P_actual: ", P_actual)
        print("selectivity: ", selectivity)
        print("depth: ", depth)
        print("R_IBM: ", P_actual / P_theoretical)
        print("expected depth: ", depth / P_actual)
        # print("histogram: ", histogram)
        # plot_histogram(histogram)

    def D2M3(self):
        print("Test D2M3: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(self.n, 2, [1], self.state)
        result = QPSA.classic_grover_stats(result_circuit, self.state, self.n, self.simulator)
        self.print_result(result)

    def D3M3(self):
        print("Test D3M3: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(self.n, 2, [0, 1], self.state)
        result = QPSA.classic_grover_stats(result_circuit, self.state, self.n, self.simulator)
        self.print_result(result)

    def D3D3M3(self):
        print("Test D3D3M3: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(self.n, 2, [0, 2], self.state)
        result = QPSA.classic_grover_stats(result_circuit, self.state, self.n, self.simulator)
        self.print_result(result)

    def D2M1_D2M2(self):
        print("Test D2M1_D2M2: __________________")
        #   two stage algorithm
        result = QPSA.design_and_test_two_stage(self.n, 2, [1], 2, [1], self.state, self.simulator)
        self.print_result(result)
    def G1D2M2(self):
        print("Test G1D2M2: __________________")
        result = QPSA.hybrid_design_and_test(self.n, 1, 2, [1, 0], self.state, self.simulator)
        self.print_result(result)
