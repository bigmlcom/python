#!/usr/bin/env python
# -*- coding: utf-8 -*-
def predict_final(prefix=None,
                  assignment=None,
                  tutorial=None,
                  midterm=None,
                  takehome=None,
                  final=None):
    """ Predictor for Final from model/59db76eb9b356c2c97004802

        Predictive model by BigML - Machine Learning Made Easy
    """
    if (midterm is None):
        return {"prediction":-2.31071}
    if (midterm > 77.19):
        if (assignment is None):
            return {"prediction":17.90525}
        if (assignment > 85.635):
            if (takehome is None):
                return {"prediction":18.7373}
            if (takehome > 106.945):
                return {"prediction":2.71513}
            if (takehome <= 106.945):
                if (tutorial is None):
                    return {"prediction":19.56899}
                if (tutorial > 103.365):
                    return {"prediction":12.02522}
                if (tutorial <= 103.365):
                    if (tutorial > 78.795):
                        return {"prediction":23.71468}
                    if (tutorial <= 78.795):
                        return {"prediction":9.17351}
        if (assignment <= 85.635):
            return {"prediction":1.88013}
    if (midterm <= 77.19):
        if (midterm > 55.31):
            if (tutorial is None):
                return {"prediction":-5.75208}
            if (tutorial > 84.92):
                if (tutorial > 87.115):
                    if (takehome is None):
                        return {"prediction":-5.90899}
                    if (takehome > 98.33):
                        if (tutorial > 100.58):
                            return {"prediction":-0.08649}
                        if (tutorial <= 100.58):
                            return {"prediction":-2.49316}
                    if (takehome <= 98.33):
                        if (prefix is None):
                            return {"prediction":-7.67532}
                        if (prefix > 7):
                            if (tutorial > 94.715):
                                return {"prediction":-12.86316}
                            if (tutorial <= 94.715):
                                return {"prediction":-3.53487}
                        if (prefix <= 7):
                            if (midterm > 65.31):
                                return {"prediction":-6.10379}
                            if (midterm <= 65.31):
                                return {"prediction":3.55013}
                if (tutorial <= 87.115):
                    return {"prediction":14.56621}
            if (tutorial <= 84.92):
                if (assignment is None):
                    return {"prediction":-12.04119}
                if (assignment > 40.75):
                    if (tutorial > 73.515):
                        return {"prediction":-8.34478}
                    if (tutorial <= 73.515):
                        return {"prediction":-16.89263}
                if (assignment <= 40.75):
                    return {"prediction":-0.08649}
        if (midterm <= 55.31):
            if (takehome is None):
                return {"prediction":-18.31226}
            if (takehome > 101.67):
                return {"prediction":6.05013}
            if (takehome <= 101.67):
                if (tutorial is None):
                    return {"prediction":-20.33976}
                if (tutorial > 100.315):
                    return {"prediction":-27.48979}
                if (tutorial <= 100.315):
                    if (tutorial > 97.21):
                        return {"prediction":-3.94987}
                    if (tutorial <= 97.21):
                        return {"prediction":-15.97477}


def predict(prefix=None,
            assignment=None,
            tutorial=None,
            midterm=None,
            takehome=None,
            final=None):
    prediction = predict_final(prefix=prefix, assignment=assignment, tutorial=tutorial, midterm=midterm, takehome=takehome, final=final)
    prediction.update({"weight": 0.09984})
    return prediction