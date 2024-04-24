{ pkgs ? import <nixpkgs> {} }:

let
  esptool = pkgs.stdenv.mkDerivation {
    name = "esptool";
    src = pkgs.fetchFromGitHub {
      owner = "espressif";
      repo = "esptool";
      rev = "v4.7";
      sha256 = "1y4cngvryxaqai3zz83lhlb059dqkv58vymjlbcwiyqy1l531cfa";
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
    pkgs.rshell
    pkgs.python3
    pkgs.python311Packages.pip
    pkgs.screen
  ];

  shellHook = ''
    echo "Environment ready. Python, esptool, and arduino-cli are available."

    function esp-fc() {
      case "$1" in
        install)
          pip install --target=./lib -r dependencies.txt
          ;;
        deploy)
          mkdir -p ./src/lib
          cp -f ./lib/microdot/microdot.py ./src/lib/
          rshell -p /dev/ttyUSB0 rsync -m src /pyboard
          ;;
        rshell)
          rshell -p /dev/ttyUSB0
          ;;
        screen)
          screen /dev/ttyUSB0 115200
          ;;
        *)
          echo "Usage: esp-fc [install|deploy|rshell]"
          ;;
      esac
    }
  '';
}
