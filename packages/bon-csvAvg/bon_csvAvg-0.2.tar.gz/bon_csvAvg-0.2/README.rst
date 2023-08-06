============
bon_csvAvg
============

A little script that calculates the average of a number of eqal `bonnie++ <http://www.coker.com.au/bonnie++/>`_ tests.
It is probably far from complete and I've just tested it with some of my recent results.

Installation
============

.. code-block:: sh

    pip install bon-csvAvg


Usage
=====

.. code-block:: sh

    bonnie++ ... | bon_csvAvg.py | bon_csv2html > your_bonnie_result.html
    # or
    bon_csvAvg.py your_bonnie_result.csv | bon_csv2html > your_bonnie_result.html


The script will try to average all results with the same name (:code:`bonnie++ -m "foobar" ...`) and will only output lines that have been calculated (e.g lines with names occurring only one won't be printed).
Columns that could not be calculated will be printed as ":code:`yyyyy`" (borrowing from bonnies ":code:`+++++`" columns).
