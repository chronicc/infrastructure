"""Distribute ACME certificates and keys to remote hosts."""

import argparse
import os
import paramiko
import sys
import json


class AcmeDistributor:
    def __init__(self, acme_file_path, host, user):
        self.acme_file_path = acme_file_path
        self.host = host
        self.user = user

        self.cert = None
        self.key = None

    def distribute(self):
        for host in self.hosts:
            print(f"Distributing certificates to {host}...")
            try:
                self._distribute_to_host(host)
            except Exception as e:
                print(f"Failed to distribute to {host}: {e}")

    def _distribute_to_host(self, host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=self.user, key_filename=self.key_file)

        sftp = ssh.open_sftp()
        for filename in os.listdir(self.cert_dir):
            local_path = os.path.join(self.cert_dir, filename)
            remote_path = f"/etc/ssl/certs/{filename}"
            sftp.put(local_path, remote_path)
            print(f"Uploaded {filename} to {host}:{remote_path}")

        sftp.close()
        ssh.close()

    def read_acme_files(self):
        with open(self.acme_file_path, "r") as fp:
            content = json.load(fp)
            self.cert = content.search(
                "Certificates[?domain.main==`{{ item }}`].certificate"
            )
            self.key = content.search("Certificates[?domain.main==`{{ item }}`].key")
