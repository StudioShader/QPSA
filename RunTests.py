import QPSA
from qiskit.visualization import plot_histogram
from qiskit.test.mock import FakeMelbourne as Mback


def print_result(result):
    (P_theoretical, P_actual, selectivity, depth, histogram) = result

    # uncomment these if you want to see precise data about tests
    print("P_theoretical: ", P_theoretical)
    print("P_actual: ", P_actual)
    print("selectivity: ", selectivity)
    print("depth: ", depth)
    print("R_IBM: ", P_actual / P_theoretical)
    print("expected depth: ", depth / P_actual)

    gathered = [P_theoretical, P_actual, selectivity, depth, P_actual / P_theoretical, depth / P_actual]
    return gathered
    # print("histogram: ", histogram)
    # plot_histogram(histogram)


class ThreeQubitCases:
    def __init__(self, simulator, execution_parameters=None, state=None):
        if state is None:
            state = [0, 1, 0]
        self.n = 3
        self.state = state
        self.simulator = simulator
        self.execution_parameters = execution_parameters

    def SpecialCase(self):
        print("Test D3M3: __________________")
        result_circuit = QPSA.design_grover_circuit(self.n, 1, self.state)
        result = QPSA.classic_grover_stats(result_circuit, self.state, self.n, self.simulator,
                                           execution_parameters=self.execution_parameters)
        return print_result(result)

    def D2M3(self):
        print("Test D2M3: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(self.n, 2, [1], self.state)
        result = QPSA.classic_grover_stats(result_circuit, self.state, self.n, self.simulator,
                                           execution_parameters=self.execution_parameters)
        self.print_result(result)

    def D3M3(self, execution_parameters):
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


class OtherCases:
    def __init__(self, simulator, execution_parameters=None):
        self.simulator = simulator
        self.execution_parameters = execution_parameters
        self.state6 = [0, 1, 0, 0, 1, 1]
        self.state8 = [0, 1, 1, 0, 0, 1, 0, 1]
        self.state10 = [0, 1, 0, 0, 1, 1, 1, 0, 1, 0]

    def D6_iM6(self, i):
        print("Test D6_" + str(i) + "M6: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(n=6, m=None, vector_j=[0, i], state=self.state6)
        result = QPSA.classic_grover_stats(result_circuit, self.state6, 6, self.simulator,
                                           execution_parameters=self.execution_parameters)
        return print_result(result)

    def D4_iM6(self, i):
        print("Test D6_" + str(i) + "M6: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(n=6, m=4, vector_j=[i, 0], state=self.state6)
        result = QPSA.classic_grover_stats(result_circuit, self.state6, 6, self.simulator,
                                           execution_parameters=self.execution_parameters)
        return print_result(result)

    def D4_i1M2_D4_i2M4(self, i1, i2):
        print("Test D4_" + str(i1) + "M2_D4_" + str(i2) + "M4: __________________")
        #   two stage algorithm
        result = QPSA.design_and_test_two_stage(n=6, m1=4, vector_j1=[i1], m2=4, vector_j2=[i2], state=self.state6,
                                                simulator=self.simulator,
                                                execution_parameters=self.execution_parameters)
        return print_result(result)

    def D8_iM8(self, i):
        print("Test D8_" + str(i) + "M8: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(n=8, m=None, vector_j=[0, i], state=self.state8)
        result = QPSA.classic_grover_stats(result_circuit, self.state8, 8, self.simulator,
                                           execution_parameters=self.execution_parameters)
        return print_result(result)

    def D6_iM8(self, i):
        print("Test D6_" + str(i) + "M8: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(n=8, m=6, vector_j=[i, 0], state=self.state8)
        result = QPSA.classic_grover_stats(result_circuit, self.state8, 8, self.simulator,
                                           execution_parameters=self.execution_parameters)
        return print_result(result)

    def G1D6_iM8(self, i):
        print("Test G1D6_iM8: __________________")
        result = QPSA.hybrid_design_and_test(n=8, l=1, m=6, vector_j=[0, i], state=self.state8,
                                             simulator=self.simulator)
        return print_result(result)

    def G1D7_iM8(self, i):
        print("Test G1D6_iM8: __________________")
        result = QPSA.hybrid_design_and_test(n=8, l=1, m=7, vector_j=[0, i], state=self.state8,
                                             simulator=self.simulator)
        return print_result(result)

    def G2D6_iM8(self, i):
        print("Test G2D6_iM8: __________________")
        result = QPSA.hybrid_design_and_test(n=8, l=2, m=6, vector_j=[0, i], state=self.state8,
                                             simulator=self.simulator)
        return print_result(result)

    def D10_iM10(self, i):
        print("Test D10_" + str(i) + "M10: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(n=10, m=None, vector_j=[0, i], state=self.state10)
        result = QPSA.classic_grover_stats(result_circuit, self.state10, 10, self.simulator,
                                           execution_parameters=self.execution_parameters)
        return print_result(result)

    def D8_iM10(self, i):
        print("Test D8_" + str(i) + "M10: __________________")
        result_circuit = QPSA.design_partial_grover_circuit(n=10, m=8, vector_j=[i, 0], state=self.state10)
        result = QPSA.classic_grover_stats(result_circuit, self.state10, 10, self.simulator,
                                           execution_parameters=self.execution_parameters)
        return print_result(result)

    def change_exec_params(self, execution_parameters):
        self.execution_parameters = execution_parameters


def _D6_iM6(test_class, i):
    return test_class.D6_iM6(i)


def _D4_iM6(test_class, i):
    return test_class.D4_iM6(i)


def _D4_i1M2_D4_i2M4(test_class, i1, i2):
    return test_class.D4_i1M2_D4_i2M4(i1, i2)


def _D8_iM8(test_class, i):
    return test_class.D8_iM8(i)


def _D6_iM8(test_class, i):
    return test_class.D6_iM8(i)


def _G1D6_iM8(test_class, i):
    return test_class.G1D6_iM8(i)


def _G1D7_iM8(test_class, i):
    return test_class.G1D7_iM8(i)


def _G2D6_iM8(test_class, i):
    return test_class.G2D6_iM8(i)


def _D10_iM10(test_class, i):
    return test_class.D10_iM10(i)


def _D8_iM10(test_class, i):
    return test_class.D8_iM10(i)
