Installation
============

1. Connect all nodes via nebula vpn.
2. Create a docker swarm cluster on the vpn subnet.
3. Add the proxy label to the lighthouse node. This will host the proxy container.
    ```bash
    docker node update --label-add proxy=true $NODE
    ```
4. Add the environment label to all nodes.
    ```bash
    docker node update --label-add environment=production $NODE
    docker node update --label-add environment=testing $NODE
    docker node update --label-add environment=development $NODE
    ```
5. Deploy the swarm services to the cluster.
    ```bash
    docker stack deploy -c swarm_services/$SERVICE.compose.yml $SERVICE
    ```
6. Deploy one or more swarm apps to the cluster.
    ```bash
    docker stack deploy -c swarm_apps/$APP.compose.yml $APP
    ```
