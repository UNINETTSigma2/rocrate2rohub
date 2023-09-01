from pathlib import Path
from tempfile import TemporaryDirectory

from rdflib import Graph
from rocrate.rocrate import ROCrate


__all__ = [
    'convert_jsonld_to_crate',
    'convert_crate_to_jsonld',
]


FILE_FORMAT = 'json-ld'



def convert_jsonld_to_crate(jsonld_file) -> ROCrate:
    rdf = Graph().parse(jsonld_file, format=FILE_FORMAT)
    with TemporaryDirectory() as tempdirpath:
        with open(Path(tempdirpath) / 'ro-crate-metadata.json', 'w') as F:
            text = rdf.serialize(format=FILE_FORMAT)
            F.write(text)
        crate = ROCrate(tempdirpath)
        return crate


def convert_crate_to_jsonld(crate: ROCrate) -> str:
    with TemporaryDirectory() as tempdirpath:
        path = Path(tempdirpath) / "RO-crate"
        crate.write(str(path))
        with open(path / 'ro-crate-metadata.json') as F:
            text = F.read()
            return text
