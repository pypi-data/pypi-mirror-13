=====================
SCluster
=====================
--------------------------------------------------------
an implementation of spectral clustering for documents
--------------------------------------------------------

 :Homepage: http://github.com/whym/scluster
 :Contact:  http://whym.org

Overview
==============================
Spectral clustering a modern clustering technique considered to be effective for image clustering among others. [#]_ [#]_

This software find clusters among documents based on the bag-of-words representation [#]_ and TF-IDF weighting [#]_.

.. [#] Ulrike von Luxburg, A Tutorial on Spectral Clustering, 2006. http://arxiv.org/abs/0711.0189
.. [#] Chris H. Q. Ding, Spectral Clustering, 2004. http://ranger.uta.edu/~chqding/Spectral/
.. [#] http://en.wikipedia.org/wiki/Bag_of_words_model
.. [#] http://en.wikipedia.org/wiki/Tf%E2%80%93idf

Requirements
==============================
Following softwares are required.

- Python 2 or 3
- Numpy
- Scipy

How to use
==============================
1. Prepare documents as raw-text files


Notes
==============================
- When you use the Reuters set, notice No 17980 might contain non-Unicode character at Line 10. It should probably read: "world economic growth-side measures ..."

.. [#] http://www.daviddlewis.com/resources/testcollections/reuters21578/
