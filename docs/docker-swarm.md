Docker Swarm
============

Create a new Swarm
------------------

1. Initialize the swarm on the first node: `docker swarm init --advertise-addr <MANAGER-IP>`.
2. Check if the swarm is active: `docker info` and `docker node ls`.

Join a Node to the Swarm
------------------------

1. Get the join command from an initialized swarm node: `docker swarm join-token worker`.
2. Run the join command on the node that should join the swarm.
3. Check if the node has joined the swarm: `docker node ls`.

Add a Label to a Node
---------------------

1. Add the label to the node: `docker node update --label-add <KEY>=<VALUE> <NODE>`
