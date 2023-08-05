========================
 List Output Formatters
========================

cliff-tablib delivers a new output formatter for list commands.

html
====

The ``html`` formatter uses tablib_ to produce HTML output as a table.

::

  (.venv)$ cliffdemo files -f html
  <table>
  <thead>
  <tr><th>Name</th>
  <th>Size</th></tr>
  </thead>
  <tr><td>build</td>
  <td>136</td></tr>
  <tr><td>cliffdemo.log</td>
  <td>3252</td></tr>
  <tr><td>Makefile</td>
  <td>5569</td></tr>
  <tr><td>requirements.txt</td>
  <td>33</td></tr>
  <tr><td>source</td>
  <td>782</td></tr>
  </table>
.. _tablib: https://github.com/kennethreitz/tablib
