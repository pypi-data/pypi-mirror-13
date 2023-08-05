
Overview
===========

:Title: Acute Myeloid Leukemia Outcome Prediction
:Nickname: D9C2
:Summary: 
:SubChallenges: sc1, sc2, sc3
:Synapse page: https://www.synapse.org/#!Synapse:syn2455683


.. contents::


Scoring
---------

::

    from dreamtools import D9C2
    s = D9C2()
    filename = s.download_template() 
    s.score(filename) 


