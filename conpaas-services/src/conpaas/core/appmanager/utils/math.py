#!/usr/bin/env python


class MathUtils:

    @staticmethod
    def pareto_frontier(Xs, Ys, maxX = False, maxY = False):
        myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
        p_front = [myList[0]]    
        for pair in myList[1:]:
            if maxY: 
                if pair[1] >= p_front[-1][1]:
                    p_front.append(pair)
            else:
                if pair[1] <= p_front[-1][1]:
                    p_front.append(pair)
        p_frontX = [pair[0] for pair in p_front]
        p_frontY = [pair[1] for pair in p_front]
        return p_frontX, p_frontY
        


    @staticmethod
    def pareto_frontier_data(data):
        myList = sorted(data, key=lambda element: (element[1], element[2]))
        p_front = [myList[0]]    
        for pair in myList[1:]:
	    t_pair = [pair[1], pair[2]]
	    f_pair = [p_front[-1][1], p_front[-1][2]]
            if t_pair[1] <= f_pair[1]:
		p_front.append(pair)
        return p_front
    
