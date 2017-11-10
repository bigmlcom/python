#!/usr/bin/env python
# -*- coding: utf-8 -*-
def predict_final(prefix=None,
                  assignment=None,
                  tutorial=None,
                  midterm=None,
                  takehome=None,
                  final=None):
    """ Predictor for Final from model/59db76eb9b356c2c97004804

        Predictive model by BigML - Machine Learning Made Easy
    """
    if (midterm is None):
        return {"prediction":0.38343}
    if (midterm > 77.08667):
        if (takehome is None):
            return {"prediction":20.38342}
        if (takehome > 106.945):
            return {"prediction":3.43945}
        if (takehome <= 106.945):
            if (tutorial is None):
                return {"prediction":22.41332}
            if (tutorial > 78.665):
                return {"prediction":23.88547}
            if (tutorial <= 78.665):
                return {"prediction":8.56289}
    if (midterm <= 77.08667):
        if (midterm > 48.75):
            if (takehome is None):
                return {"prediction":-4.5295}
            if (takehome > 53.795):
                if (midterm > 73.44):
                    if (takehome > 73.795):
                        return {"prediction":-13.82749}
                    if (takehome <= 73.795):
                        return {"prediction":-3.41771}
                if (midterm <= 73.44):
                    if (assignment is None):
                        return {"prediction":-0.71945}
                    if (assignment > 82.74):
                        if (tutorial is None):
                            return {"prediction":-3.97172}
                        if (tutorial > 103.945):
                            if (tutorial > 104.835):
                                return {"prediction":-0.08074}
                            if (tutorial <= 104.835):
                                return {"prediction":1.25414}
                        if (tutorial <= 103.945):
                            if (midterm > 62.5):
                                if (midterm > 65.31):
                                    return {"prediction":-4.37529}
                                if (midterm <= 65.31):
                                    return {"prediction":4.4972}
                            if (midterm <= 62.5):
                                if (tutorial > 95.71):
                                    return {"prediction":-14.0932}
                                if (tutorial <= 95.71):
                                    return {"prediction":-1.74541}
                    if (assignment <= 82.74):
                        if (tutorial is None):
                            return {"prediction":7.50115}
                        if (tutorial > 96.79):
                            return {"prediction":-0.71028}
                        if (tutorial <= 96.79):
                            return {"prediction":10.35668}
            if (takehome <= 53.795):
                return {"prediction":-13.76724}
        if (midterm <= 48.75):
            if (takehome is None):
                return {"prediction":-15.51536}
            if (takehome > 58.89):
                return {"prediction":-18.93268}
            if (takehome <= 58.89):
                if (tutorial is None):
                    return {"prediction":-5.65621}
                if (tutorial > 77.095):
                    return {"prediction":-7.01337}
                if (tutorial <= 77.095):
                    return {"prediction":-0.79237}


def predict(prefix=None,
            assignment=None,
            tutorial=None,
            midterm=None,
            takehome=None,
            final=None):
    prediction = predict_final(prefix=prefix, assignment=assignment, tutorial=tutorial, midterm=midterm, takehome=takehome, final=final)
    prediction.update({"weight": 0.09621})
    return prediction