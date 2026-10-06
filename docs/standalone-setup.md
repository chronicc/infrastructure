Standalone Setup
================

When there is no static IP address or the connection to the internet is limited or impossible, the standalone setup
will ensure the services can still be used.

Self-signed Certificates
------------------------

1. Create the directory to contain the certificates and the configuration: `mkdir .tls && cd $_`.
2. Create the self signed certificate:
    ```
    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
    -keyout local.key -out local.crt \
    -subj "/CN=*.<DOMAIN>"
    ```
3. Create the traefik configuration file `tls.yml`:
    ```
    tls:
    stores:
      default:
        defaultCertificate:
          certFile: /ssl/local.crt
          keyFile: /ssl/local.key
    certificates:
      - certFile: /ssl/local.crt
        keyFile:  /ssl/local.key
    ```
4. Uncomment the letsencrypt certresolver parts from the traefik compose file.
5. Deploy the traefik stack: `docker stack deploy -c swarm_services/traefik.compose.yml traefik`.
6. Copy the contents of the .ssl directory to the traefik ssl volume: `cp .ssl/* /var/lib/docker/volumes/`.
7. Redeploy the traefik stack: `docker stack deploy -c swarm_services/traefik.compose.yml traefik`.
