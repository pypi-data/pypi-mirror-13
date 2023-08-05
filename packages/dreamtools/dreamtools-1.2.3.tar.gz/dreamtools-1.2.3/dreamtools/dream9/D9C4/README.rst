
Overview
===========


:Title: 
:Nickname: D9C4
:Summary:  SV, SNV
:SubChallenges: 
:Synapse page: https://www.synapse.org/#!Synapse:synXXXXXXX

Resources:
https://github.com/Sage-Bionetworks/ICGC-TCGA-DREAM-Mutation-Calling-challenge-tools

.. contents::


Scoring
---------

::

    from dreamtools import D9C4
    s = D9C4()
    filename = s.download_template() 
    s.score(filename) 


