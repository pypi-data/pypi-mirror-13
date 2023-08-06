import numpy as np


class Forecast:
    def __init__(self, orders: list):
        self.__orders = orders
        self.__moving_average_forecast = []

    @property
    def moving_average_forecast(self, forecast: list):
        self.__moving_average_forecast = forecast

    @moving_average_forecast.getter
    def moving_average_forecast(self) -> list:
        return self.__moving_average_forecast

    # specify a start position and the forecast will build from this position
    def calculate_moving_average_forecast(self, average_period: int = 3, forecast_length: int = 2,
                                          base_forecast: bool = False, start_position: int = 0) -> list:
        try:
            if base_forecast:
                start_period = start_position + average_period
                end_period = len(self.__orders)
                total_orders = 0

                moving_average = []
                for i in self.__orders[0:start_position]:
                    moving_average.append(self.__orders[i])
                # in the base_forecast the length of the forecast is the same as the length of the initial run of demand
                # retrieved from the demand list to the moving_average list


                count = 0
                average_orders = 0.0
                while count < forecast_length:
                    for items in moving_average[0:end_period]:
                        total_orders += items
                    count += 1
                    average_orders = total_orders / float(average_period)
                    moving_average.append(average_orders)
                    average_orders = 0.0
                    total_orders = 0.0
                    if count < 1:
                        start_period += len(moving_average) - average_period
                    else:
                        start_period += 1

                    end_period = len(moving_average)
                    self.__moving_average_forecast = moving_average

            else:
                start_period = len(self.__orders) - average_period
                end_period = len(self.__orders)
                total_orders = 0
                moving_average = self.__orders
                count = 0
                average_orders = 0.0
                while count < forecast_length:
                    for items in moving_average[start_period:end_period]:
                        total_orders += items
                    count += 1
                    average_orders = total_orders / float(average_period)
                    moving_average.append(average_orders)
                    average_orders = 0.0
                    total_orders = 0.0
                    if count < 1:
                        start_period += len(moving_average) - average_period
                    else:
                        start_period += 1

                    end_period = len(moving_average)
                    self.__moving_average_forecast = moving_average
                return moving_average
        except Exception as e:
            print(e)

    # make sure the number of weights matches the average period if not error
    def calculate_weighted_moving_average_forecast(self, weights: list, average_period: int = 3,
                                                   forecast_length: int = 3) -> list:
        try:
            if sum(weights) != 1 or len(weights) != average_period:
                raise Exception(
                    'The weights should equal 1 and be as long as the average period (default 3).'
                    ' The supplied weights total {} and is {} members long. Please check the supplied weights.'.format(
                        sum(weights), len(weights)))
            else:
                start_period = len(self.__orders) - average_period
            end_period = len(self.__orders)
            total_orders = 0
            moving_average = self.__orders
            count = 0
            average_orders = 0.0
            weight_count = 0
            while count < forecast_length:
                weight_count = 0
                for items in moving_average[start_period:end_period]:
                    total_orders += items
                average_orders = (total_orders / float(average_period)) * weights[weight_count]
                count += 1
                moving_average.append(average_orders)
                average_orders = 0.0
                total_orders = 0.0
                if count < 1:
                    start_period += len(moving_average) - average_period
                else:
                    start_period += 1

                end_period = len(moving_average)
            return moving_average
        except Exception as e:
            print(e)

    def calculate_simple_exponential_smoothed_forecast(self, forecasts: list) -> list:
        pass

    # also use to calculate the MAD for all forecasting methods given a spcific length of order

    def calculate_mean_absolute_deviation(self, forecasts: list, orders: list, base_forecast: bool = False) -> np.array:
        if base_forecast:
            forecast_array = np.array(forecasts)
            orders_array = np.array(self.__orders[0: len(forecasts)])
            print(orders_array)
            print(forecast_array)
            std_array = orders_array - forecast_array
            std_array = sum(abs(std_array)) / len(std_array)
        else:
            forecast_array = np.array(forecasts)
            orders_array = np.array(self.__orders)
            print(orders_array)
            print(forecast_array)
            std_array = orders_array - forecast_array
            std_array = sum(abs(std_array)) / len(std_array)
        return std_array

    def calculate_mean_forecast_error(self):
        pass

    def calculate_mean_aboslute_percentage_error(self, **forecasts) -> list:
        pass

    def optimise_select_optimal_forecast_technique(self):
        pass

    def model_linear_regression_forecast(self):
        pass

    def model_autoregressive_forecast(self):
        pass

    # select which algorithm to use list available algorithms in the documentations
    def model_genetic_algorithm(self):
        pass
