"""
The Predictor module estimates future values using the monitoring data.

@author: fernandez
"""

import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.ar_model import AR
from pandas import Series, DataFrame
from statsmodels.tools import Dataset
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
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
        try: 
            time =[t for t in range(len(php_resp_time))]        
            slope, intercept, r_value, p_value, std_err = stats.linregress(time,php_resp_time)
        
            
            for pred in range(num_predictions):
                forecast.append( intercept + slope * (pred+time[len(php_resp_time)-1]) )
        
            self.logger.info("LR: Forecast values obtained for php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast))
        
        except Exception as e:
            forecast.append( 0 )
            self.logger.error("ERROR calculating the LR for the php_resp_time values with php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast)+ " "+str(e))
        
        return forecast
    
    def vector_auto_regression(self, php_resp_time, cpu_load, num_predictions):
        year = 1921     # year to be mapped with the values
        forecast = []   # predict array
        
        try: 

            dates = sm.tsa.datetools.dates_from_range(str(year), length=len(php_resp_time)) #
            mdata = self.load_data(php_resp_time,cpu_load).data
            mdata = mdata[['value','value2']]
            data = np.array(mdata) #ndarray
            model = sm.tsa.VAR(data)
            #maxlag: Maximum number of lags to check for order selection, defaults to
            #12 * (nobs/100.)**(1./4), see select_order function
            results = model.fit(maxlags=5) #3
        
            lag_order = results.k_ar
            pred = results.forecast(data[-lag_order:], num_predictions)

            start_time = year + len(php_resp_time) #start time year of the prediction
            dates_pred = sm.tsa.datetools.dates_from_range(str(start_time), length=num_predictions)

            for i in pred:
                forecast.append(i[0]) #fisrt column
            self.logger.info("Vector_auto_regression: Forecast values obtained for php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast))
        
        except Exception as e:
            forecast = []
            forecast.append( 0 )
            self.logger.error("ERROR calculating the VAR for the php_resp_time values with php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast)+ " "+str(e))
        
        return forecast 

    def load_data(self, php_resp_time, cpu_load):
        if (len(php_resp_time) != len(cpu_load)):
            self.logger.info("load_data: data arrays must have the same number of elements.")

        data = []
        year = 1921
        for i in range(len(php_resp_time)):
            data.append({'year':year+i, 'value':php_resp_time[i], 'value2':cpu_load[i]})

        names = ('year', 'value', 'value2')

        dataset = Dataset(data=data, names=names)
        dataset.data = DataFrame(dataset.data)

        return dataset
    
    def linear_regression_ols(self, php_resp_time, num_predictions):
        forecast = []
        try: 
            time =[t for t in range(len(php_resp_time))]        
            res = sm.OLS(php_resp_time,time)
            model = res.fit(disp=False)
        
            for i in range(num_predictions):
                forecast.append( model.predict() )
        
            self.logger.info("OLS Regression: Forecast values obtained for php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast))
        except Exception as e:
            forecast.append( 0 )
            self.logger.error("ERROR calculating the LR_OLS for the php_resp_time values with php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast)+ " "+str(e))
        
        return forecast
    
    def multiple_regression(self, php_resp_time, req_rate, cpu_usage, num_predictions):
        forecast = []
        try: 
            x = np.column_stack(( php_resp_time, req_rate, cpu_usage)) 
            x = sm.add_constant(x, prepend=True) #stack explanatory variables into an array
            #y = sm.add_constant(y, prepend=True) #add a constant

            res = sm.OLS(php_resp_time,x)
            model = res.fit(disp=False)
            #res = sm.OLS(y,x).fit() #create a model and fit it

            for i in range(num_predictions):
                forecast.append( model.predict() )
        
            self.logger.info("Multiple Regression: Forecast values obtained for php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast))
        except Exception as e:
            forecast.append( 0 )
            self.logger.error("ERROR calculating the Multiple Regression for the php_resp_time values with php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast)+ " "+str(e))
        
        return forecast
    
    def auto_regression(self, php_resp_time, num_predictions):
        forecast = []
        try: 
            dates = sm.tsa.datetools.dates_from_range('1921', length=len(php_resp_time))
            endog = Series(php_resp_time, index=dates)
            ar_model = sm.tsa.AR(endog).fit(maxlag=9, method='mle',disp=False)
   
            start_time = 1920 + len(php_resp_time)
            end_time = start_time + num_predictions
            pred = ar_model.predict(start=str(start_time), end=str(end_time))
            # print pred

            for i in pred.index:
                if str(pred.ix).find('nan') > 0 :
                    forecast.append(0)
                else:
                    forecast.append(pred.ix[i])
            
            if math.isnan(forecast[0]):
                raise Exception("The forecast values contain 'nan' values")
                
            self.logger.info("AR: Forecast values obtained for php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast))
        
        except Exception as e:
            forecast = []
            forecast.append( 0 )
            self.logger.error("ERROR calculating the AR for the php_resp_time values with php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast)+ " "+str(e))
        
        return forecast

    
    def arma (self,php_resp_time, num_predictions):
        forecast = []
        try: 
            #data = sm.datasets.sunspots.load()
            dates = sm.tsa.datetools.dates_from_range('1921', length=len(php_resp_time))

            endog = Series(php_resp_time, index=dates)
            #arma_model = sm.tsa.ARMA(endog,(15,0)).fit() 
        
            p = sm.tsa.AR(endog).fit(disp=False).params

            arma_model = sm.tsa.ARMA(endog, (len(p)-1,0)).fit(start_params=p.values,disp=False)
        
            start_time = 1920 + len(php_resp_time)
            end_time = start_time + num_predictions
            pred = arma_model.predict(start=str(start_time), end=str(end_time), dynamic=True)
                
            for i in pred.index:
                if str(pred.ix).find('nan') > 0:
                    forecast.append(0)
                else:
                    forecast.append(pred.ix[i])
            
            if math.isnan(forecast[0]):
                raise Exception("The forecast values contain 'nan' values")
            
            self.logger.info("ARMA: Forecast values obtained for php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast))
        
        except Exception as e:
            forecast = []
            forecast.append( 0 )
            self.logger.error("ERROR calculating the ARMA for the php_resp_time values with php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast)+ " "+str(e))
            
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
        ylen =len(y)
        # I cannot pass 12 as a parameter of C
        #if ylen % c !=0:
        #   return None
   
        fc =float(c)
        ybar2 =sum([y[i] for i in range(c, 2 * c)])/ fc
        ybar1 =sum([y[i] for i in range(c)]) / fc
        b0 =(ybar2 - ybar1) / fc
        if debug: print "b0 = ", b0
 
        #Compute for the level estimate a0 using b0 above.
        tbar  =sum(i for i in range(1, c+1)) / fc
        # print tbar
        a0 =ybar1  - b0 * tbar
        if debug: "a0 = ", a0
 
        #Compute for initial indices
        I =[y[i] / (a0 + (i+1) * b0) for i in range(0, ylen)]
        if debug: print "Initial indices = ", I
 
        S=[0] * (ylen+ c)
        for i in range(c):
            S[i] =(I[i] + I[i+c]) / 2.0
 
        #Normalize so S[i] for i in [0, c)  will add to c.
        tS =c / sum([S[i] for i in range(c)])
        for i in range(c):
            S[i] *=tS
            if debug: print "S[",i,"]=", S[i]
 
        # Holt - winters proper ...
        if debug: print "Use Holt Winters formulae"
        F =[0] * (ylen+ c)   
 
        At =a0
        Bt =b0
        for i in range(ylen):
            Atm1 =At
            Btm1 =Bt
            At =alpha * y[i] / S[i] + (1.0-alpha) * (Atm1 + Btm1)
            Bt =beta * (At - Atm1) + (1- beta) * Btm1
            S[i+c] =gamma * y[i] / At + (1.0 - gamma) * S[i]
            F[i]=(a0 + b0 * (i+1)) * S[i]        
         #   print "i=", i+1, "y=", y[i], "S=", S[i], "Atm1=", Atm1, "Btm1=",Btm1, "At=", At, "Bt=", Bt, "S[i+c]=", S[i+c], "F=", F[i]
         #   print i,y[i],  F[i]
        #Forecast for next c periods:
        forecast = []
        for m in range(c):
            forecast.append( (At + Bt* (m+1))* S[ylen + m] )
 
        return forecast
    
    def exponential_smoothing (self, php_resp_time, num_predictions ):
        forecast = []
        try: 
            forecast = self.holtwinters(php_resp_time, 0.2, 0.1, 0.05, num_predictions)
        
            self.logger.info("Exponential Smoothing: Forecast values obtained for php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast))
        
        except Exception as e:
            forecast.append( 0 )
            self.logger.error("ERROR calculating the EXP. SMOOTHING for the php_resp_time values with php_resp_time[0]: "+str(php_resp_time[0])+" --> "+ str(forecast)+ " "+str(e))
            
        return forecast
    

