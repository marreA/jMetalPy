from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from jmetal.core.solution import Solution

S = TypeVar('S')


class Comparator(Generic[S], ABC):

    @abstractmethod
    def compare(self, solution1: S, solution2: S) -> int:
        pass

    def get_name(self) -> str:
        return self.__class__.__name__


class EqualSolutionsComparator(Comparator):

    def compare(self, solution1: Solution, solution2: Solution) -> int:
        if solution1 is None:
            return 1
        elif solution2 is None:
            return -1

        dominate1 = 0
        dominate2 = 0

        for i in range(len(solution1.objectives)):
            value1 = solution1.objectives[i]
            value2 = solution2.objectives[i]

            if value1 < value2:
                flag = -1
            elif value1 > value2:
                flag = 1
            else:
                flag = 0

            if flag == -1:
                dominate1 = 1
            if flag == 1:
                dominate2 = 1

        if dominate1 == 0 and dominate2 == 0:
            return 0
        elif dominate1 == 1:
            return -1
        elif dominate2 == 1:
            return 1


class SolutionAttributeComparator(Comparator):

    def __init__(self, key: str, lowest_is_best: bool = True):
        self.key = key
        self.lowest_is_best = lowest_is_best

    def compare(self, solution1: Solution, solution2: Solution) -> int:
        value1 = solution1.attributes.get(self.key)
        value2 = solution2.attributes.get(self.key)

        result = 0
        if value1 is not None and value2 is not None:
            if self.lowest_is_best:
                if value1 < value2:
                    result = -1
                elif value1 > value2:
                    result = 1
                else:
                    result = 0
            else:
                if value1 > value2:
                    result = -1
                elif value1 < value2:
                    result = 1
                else:
                    result = 0

        return result


class RankingAndCrowdingDistanceComparator(Comparator):

    def compare(self, solution1: Solution, solution2: Solution) -> int:
        result = \
            SolutionAttributeComparator("dominance_ranking").compare(solution1, solution2)

        if result is 0:
            result = \
                SolutionAttributeComparator("crowding_distance", lowest_is_best=False).compare(solution1, solution2)

        return result


class DominanceComparator(Comparator):

    def __init__(self,
                 constraint_comparator: SolutionAttributeComparator=SolutionAttributeComparator("overall_constraint_violation", False)):
        self.constraint_comparator = constraint_comparator

    def compare(self, solution1: Solution, solution2: Solution) -> int:
        if solution1 is None:
            raise Exception("The solution1 is None")
        elif solution2 is None:
            raise Exception("The solution2 is None")
        # elif len(solution1.objectives) != len(solution2.objectives):
        #    raise Exception("The solutions have different number of objectives")

        result = 0
        #if solution1.number_of_constraints > 0:
        if solution1.attributes.get(self.constraint_comparator.key) is not None:
            result = self.constraint_comparator.compare(solution1, solution2)
        if result == 0:
            result = self.__dominance_test(solution1, solution2)

        return result

    def __dominance_test(self, solution1: Solution, solution2: Solution) -> float:
        best_is_one = 0
        best_is_two = 0

        for i in range(solution1.number_of_objectives):
            value1 = solution1.objectives[i]
            value2 = solution2.objectives[i]
            if value1 != value2:
                if value1 < value2:
                    best_is_one = 1
                if value1 > value2:
                    best_is_two = 1

        if best_is_one > best_is_two:
            result = -1
        elif best_is_two > best_is_one:
            result = 1
        else:
            result = 0

        return result


class GDominanceComparator(DominanceComparator):

    def __init__(self,
                 reference_point: (),
                 constraint_comparator=SolutionAttributeComparator('overall_constraint_violation', False)):
        super(GDominanceComparator, self).__init__(constraint_comparator)
        self.reference_point = reference_point

    def compare(self, solution1: Solution, solution2: Solution):
        if self.__flag(solution1) > self.__flag(solution2):
            result = -1
        elif self.__flag(solution1) < self.__flag(solution2):
            result = 1
        else:
            result = super(GDominanceComparator, self).compare(solution1, solution2)

        return result

    def __flag(self, solution: Solution):
        result = 1
        for i in range(solution.number_of_objectives):
            if solution.objectives[i] > self.reference_point[i]:
                result = 0

        if result == 0:
            result = 1
            for i in range(solution.number_of_objectives):
                if solution.objectives[i] < self.reference_point[i]:
                    result = 0

        return result
