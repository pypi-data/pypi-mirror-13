.. vim: set fileencoding=utf-8 :
.. Manuel Günther <siebenkopf@googlemail.com>
.. Wed Apr 17 15:48:58 CEST 2013

The face recognition algorithms
===============================
In this evaluation, we execute several well-known and state-of-the-art face recognition algorithms of different kinds.
Here, we only give a short overview of the algorithms used.
For a more detailed description including the original papers and a reason for the selection of the algorithms, please read section 3.1 of `the book chapter`_.

- Cohort LDA [#]_ [``LDA-IR``]: Performs PCA and LDA on two color channels of the images and compares model and probe features in Fisher space using a the correlation function. [Lui12]_
- Grid graphs of Gabor jets [``Graphs``]: Extracts Gabor jets including Gabor phases from grid locations and compares model and probe graphs with a Gabor-phase based similarity function. [Zhang09]_
- Local Gabor binary pattern histogram sequence [``LGBPHS``]: Extracts local binary patterns (LBP) from Gabor wavelet filtered images, splits them into image blocks, extracts and concatenates histograms of LBP's and compares model and probe histograms with a histogram similarity measure. [Guenther12]_
- Inter-session variability modeling [``ISV``]: Extracts DCT features from image blocks, models them with a Gaussian mixture model, enrolls client models using ISV and computed probabilities, how probable probe features have been created by the client. [Wallace11]_
- Commercial of-the-sheft algorithgm [``COTS``]: Uses a commercial algorithm (the vendor has requested to be anonymus) for feature extraction, client model enrollment and scoring.

.. [#] The name of the algorithm was changed from ``LDA-IR`` to ``CohortLDA`` by the authors of the CSU toolkit.
       Since we do not use the cohort in our experiments, we stick to the old name ``LDA-IR`` to avoid confusion.

.. [Lui12] **Y. M. Lui, D. S. Bolme, P. J. Phillips, J. R. Beveridge, and B. A. Draper.** *Preliminary studies on the Good, the Bad, and the Ugly face recognition challenge problem.* In CVPR Workshops, pages 9–16. IEEE Computer Society, 2012.
.. [Guenther12] **M. Günther, D. Haufe, and R. P. Würtz.** *Face recognition with disparity corrected Gabor phase differences.* In ICANN, volume 7552 of LNCS, pages 411–418. Springer, 2012.
.. [Zhang09] **W. Zhang, S. Shan, L. Qing, X. Chen, and W. Gao.** *Are Gabor phases really useless for face recognition?* Pattern Analysis & Applications, 12:301–307, 2009.
.. [Wallace11] **R. Wallace, M. McLaren, C. McCool, and S. Marcel.** *Inter-session variability modelling and joint factor analysis for face authentication.* In IJCB, pages 1–8. IEEE, 2011.

.. include:: links.rst
