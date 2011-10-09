ConPaasSql - Conpaas SQL Server
-------------------------------

Configuration
-------------
./src/conpaas/mysql/server/agent/configuration.cnf

Running agent-server
--------------------
How to run the agent-server:
sudo PYTHONPATH=<path to checked out svnroot/contrail/conpaas/trunk/sql/conpaassql> python server.py

Running unit tests
------------------

Try 

$ PYTHONPATH=./src:./contrib python -m unittest conpaas.mysql.test.unit.agent.TestServerAgent

for running unit tests for agent.

Use 

$ PYTHONPATH=./src:./contrib python -m unittest conpaas.mysql.test.unit.manager.TestServerManager

for running manager unit tests.

Generating documentation
========================
../doc$ sphinx-build -a -b html source/ build/
