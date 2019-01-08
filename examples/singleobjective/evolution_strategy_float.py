from jmetal.algorithm.singleobjective.evolution_strategy import EvolutionStrategy
from jmetal.operator import Polynomial
from jmetal.problem import Sphere
from jmetal.util.termination_criterion import StoppingByEvaluations

if __name__ == '__main__':
    problem = Sphere(number_of_variables=10)

    algorithm = EvolutionStrategy(
        problem=problem,
        mu=10,
        lambda_=10,
        elitist=True,
        mutation=Polynomial(probability=1.0 / problem.number_of_variables),
        termination_criterion=StoppingByEvaluations(max=25000)
    )

    algorithm.run()
    result = algorithm.get_result()

    print('Algorithm: {}'.format(algorithm.get_name()))
    print('Problem: {}'.format(problem.get_name()))
    print('Solution: {}'.format(result.variables))
    print('Fitness: {}'.format(result.objectives[0]))
    print('Computing time: {}'.format(algorithm.total_computing_time))
