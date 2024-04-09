{ pkgs ? import <nixpkgs> {} }:

let
  esptool = pkgs.stdenv.mkDerivation {
    name = "esptool";
    src = pkgs.fetchFromGitHub {
      owner = "espressif";
      repo = "esptool";
      # Specify the commit or tag you want to use:
      rev = "v4.7"; # This should be replaced with the commit hash or tag you want to use
      sha256 = "1y4cngvryxaqai3zz83lhlb059dqkv58vymjlbcwiyqy1l531cfa"; # This should be replaced with the correct SHA256 hash for the revision
    };
    buildInputs = [ pkgs.python3 pkgs.python3Packages.setuptools ];
    propagatedBuildInputs = [
        pkgs.python3Packages.setuptools
        pkgs.python3Packages.pyserial
        pkgs.python3Packages.cryptography
        pkgs.python311Packages.intelhex
        pkgs.python311Packages.pyyaml
        pkgs.python311Packages.reedsolo
        pkgs.python311Packages.ecdsa
        pkgs.python311Packages.bitstring
    ];
    postUnpack = ''
      find $sourceRoot -type f -exec touch {} \;
    '';
    installPhase = ''
      python setup.py install --prefix=$out
    '';
  };
in
pkgs.mkShell {
  buildInputs = [
    esptool
    pkgs.python3
    pkgs.rshell
  ];

  shellHook = ''
    echo "Environment ready. Python and esptool are available."
  '';
}
