# Vendored Q# samples

Copied verbatim from [microsoft/qdk](https://github.com/microsoft/qdk) at tag **v1.31.0**,
which is the version of the `qsharp` compiler this repository runs. Each file retains its
original MIT copyright header.

These are fed to the code generator as style references, one per algorithm, because
`generate.py` previously had exemplars for only five algorithm names and passed an empty
string for everything else.

## Do not edit these files

They are a snapshot, and `tooling/test_qdk_samples_provenance.py` records a SHA-256 of each
one. Hand-editing a file fails that check, along with the compile and legacy-syntax checks.

To refresh after a compiler upgrade:

```
python tooling/vendor_qdk_samples.py
```

That fetches raw sources at the tag matching the installed `qsharp` version, compiles each
one, and keeps only those that build and define a `Main` operation. It refuses to run if the
pinned tag and the installed compiler disagree.

`provenance.json` records the tag, the compiler version, and the source URL and hash of every
file.
