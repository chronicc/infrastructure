let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-25.05";
  pkgs = import nixpkgs {
    config = { };
    overlays = [ ];
  };
in
pkgs.mkShellNoCC {
  packages = with pkgs; [
    curl
    docker_28
    docker-compose
    git
    lychee
    nixfmt-rfc-style
    pre-commit
  ];

  shellHook = ''
    alias infrastructure-vm-build="nix-build '<nixpkgs/nixos>' -A vm -I nixpkgs=channel:nixos-24.05 -I nixos-config=./configuration.nix"
    alias infrastructure-vm-start="QEMU_KERNEL_PARAMS=console=ttyS0 ./result/bin/run-nixos-vm -nographic; reset"
    alias reset="rm -f nixos.qcow2"
  '';
}
