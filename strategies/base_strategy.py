from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """Abstract class that serves as a mold for implementing betting strategies

    :param perimeter: A list of strings corresponding to the leagues on which you want to bet.
    :type perimeter: list, optional
    :param context: A dictionary that contains all the info available at the time of the bet.

    """

    perimeter = None
    context = {}

    @abstractmethod
    def accept(self, row) -> bool:
        """This function must be implemented in order to determine if the event corresponding to the given row
         is acceptable to the strategy or not."""
        pass

    @abstractmethod
    def aggregate(self, events):
        """"""
        pass

    @abstractmethod
    def select_out(self, row) -> str:
        """This function needs to be implemented in order to select which outcome is to be used for the bet.
        The chosen outcome should be one of the columns in the processed dataset."""
        pass

    @abstractmethod
    def get_bet_amount(self):
        """This function determines the amount to be used for the current bet."""
        pass

    def get_bet(self, row):
        return self.select_out(row)

    def in_perimeter(self, row):
        if self.perimeter is not None:
            if row.Div in self.perimeter:
                return True
            else:
                return False
        else:
            return True
