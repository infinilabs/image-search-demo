{
  inputs = {
    nixpkgs.url = "nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        inherit (pkgs) mkShell;
        inherit (pkgs.lib) makeLibraryPath;
        pyLibs = with pkgs; [ stdenv.cc.cc zlib ];
      in
      {
        devShells.default = mkShell {
          buildInputs = with pkgs; [ python3 ];
          shellHook = ''
            export LD_LIBRARY_PATH=${makeLibraryPath pyLibs}:$LD_LIBRARY_PATH
            export FONTCONFIG_FILE=/etc/fonts/fonts.conf
          '';
        };
      }
    )
  ;
}
