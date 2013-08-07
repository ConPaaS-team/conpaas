
import math
"""
    This prediction models need a minimum range of input values of 15-20 to be able to make future predictions. 
"""
class Prediction_Models:
    
    def __init__(self, logger):
        self.logger = logger    
        
    def average(self, x):
        assert len(x) > 0
        return float(sum(x)) / len(x)

    def correlation(self, x, y):
        assert len(x) == len(y)
        n = len(x)
        assert n > 0
        avg_x = self.average(x)
        avg_y = self.average(y)
        diffprod = 0
        xdiff2 = 0
        ydiff2 = 0
        for idx in range(n):
            xdiff = x[idx] - avg_x
            ydiff = y[idx] - avg_y
            diffprod += xdiff * ydiff
            xdiff2 += xdiff * xdiff
            ydiff2 += ydiff * ydiff

        return diffprod / math.sqrt(xdiff2 * ydiff2)    
    
    def linear_regression(self, php_resp_time, num_predictions):
        forecast = []
        
        return forecast
    
    def vector_auto_regression(self, php_resp_time, cpu_load, num_predictions):
        #year = 1921     # year to be mapped with the values
        forecast = []   # predict array
               
        return forecast 


    
    def linear_regression_ols(self, php_resp_time, num_predictions):
        forecast = []
              
        return forecast
    
    def multiple_regression(self, php_resp_time, req_rate, cpu_usage, num_predictions):
        forecast = []
             
        return forecast
    
    def auto_regression(self, php_resp_time, num_predictions):
        forecast = []
            
        return forecast

    
    def arma (self,php_resp_time, num_predictions):
        forecast = []
                
        return forecast
    
    def holtwinters(self, y, alpha, beta, gamma, c, debug=False):
        """
        y - time series data.
        alpha , beta, gamma - exponential smoothing coefficients 
                                      for level, trend, seasonal components.
        c -  extrapolated future data points.
              4 quarterly
              7 weekly.
              12 monthly
 
 
        The length of y must be a an integer multiple  (> 2) of c.
        """
        #Compute initial b and intercept using the first two complete c periods.
        
        forecast = []
        
 
        return forecast
    
    def exponential_smoothing (self, php_resp_time, num_predictions ):
        forecast = []
              
        return forecast
    

