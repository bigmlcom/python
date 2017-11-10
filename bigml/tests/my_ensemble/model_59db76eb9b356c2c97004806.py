#!/usr/bin/env python
# -*- coding: utf-8 -*-
def predict_final(prefix=None,
                  assignment=None,
                  tutorial=None,
                  midterm=None,
                  takehome=None,
                  final=None):
    """ Predictor for Final from model/59db76eb9b356c2c97004806

        Predictive model by BigML - Machine Learning Made Easy
    """
    if (midterm is None):
        return {"prediction":-1.4035}
    if (midterm > 77.19):
        if (midterm > 98.75):
            return {"prediction":27.63444}
        if (midterm <= 98.75):
            if (assignment is None):
                return {"prediction":12.52275}
            if (assignment > 85.635):
                if (takehome is None):
                    return {"prediction":13.32619}
                if (takehome > 106.945):
                    return {"prediction":2.41413}
                if (takehome <= 106.945):
                    if (assignment > 97.08):
                        return {"prediction":4.62108}
                    if (assignment <= 97.08):
                        return {"prediction":15.26138}
            if (assignment <= 85.635):
                return {"prediction":0.63728}
    if (midterm <= 77.19):
        if (tutorial is None):
            return {"prediction":-9.38705}
        if (tutorial > 86.76):
            if (takehome is None):
                return {"prediction":-12.08301}
            if (takehome > 92.5):
                if (tutorial > 104.6):
                    return {"prediction":-0.05667}
                if (tutorial <= 104.6):
                    return {"prediction":-2.93235}
            if (takehome <= 92.5):
                if (midterm > 46.875):
                    if (assignment is None):
                        return {"prediction":-15.59471}
                    if (assignment > 66.73):
                        if (tutorial > 88.32):
                            return {"prediction":-16.57693}
                        if (tutorial <= 88.32):
                            return {"prediction":-4.54968}
                    if (assignment <= 66.73):
                        return {"prediction":-2.69614}
                if (midterm <= 46.875):
                    if (takehome > 75.925):
                        return {"prediction":3.58837}
                    if (takehome <= 75.925):
                        return {"prediction":-10.89428}
        if (tutorial <= 86.76):
            if (takehome is None):
                return {"prediction":-3.91393}
            if (takehome > 88.795):
                return {"prediction":-12.42279}
            if (takehome <= 88.795):
                if (tutorial > 84.92):
                    return {"prediction":9.023}
                if (tutorial <= 84.92):
                    if (tutorial > 81.225):
                        return {"prediction":-6.43719}
                    if (tutorial <= 81.225):
                        if (tutorial > 72.855):
                            return {"prediction":5.60188}
                        if (tutorial <= 72.855):
                            if (tutorial > 61.81):
                                return {"prediction":-1.00567}
                            if (tutorial <= 61.81):
                                return {"prediction":0.80228}


def predict(prefix=None,
            assignment=None,
            tutorial=None,
            midterm=None,
            takehome=None,
            final=None):
    prediction = predict_final(prefix=prefix, assignment=assignment, tutorial=tutorial, midterm=midterm, takehome=takehome, final=final)
    prediction.update({"weight": 0.09984})
    return prediction