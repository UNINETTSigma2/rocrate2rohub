import importlib.resources as import_resources

from rocrate.rocrate import ROCrate
import rohub


ROHUB_NAME_MINLENGTH = 5
RESEARCH_AREA_FILE = 'research_areas.tsv'


class ConversionError(ValueError):
    pass


class CrateConverter:
    CHECKLIST = ("name", "description", "research_area")

    def __init__(self, filename=None):
        self.filename = filename
        self.crate = self.load(filename)
        self.research_areas = self.get_research_area_mapping()

    def load(self, filename):
        return ROCrate(filename)

    def reload_research_areas(self):
        self.research_areas = self.get_research_area_mapping()

    def validate(self):
        errors = []
        for checkname in self.CHECKLIST:
            check_method = getattr(self, f"check_{checkname}")
            if not check_method:
                errors.append((check_name, "validator missing"))
            error_message = check_method()
            if error_message:
                errors.append((checkname, error_message))
        return tuple(sorted(errors))

    def write_directory(self, filename):
        if filename.endswith('.zip'):
            raise ConversionError("Will not write to a directory ending with \".zip\"")
        self.crate.write(filename)

    def write_zipfile(self, filename):
        if not filename.endswith('.zip'):
            raise ConversionError("Will not write a zip to a filename not ending with \".zip\"")
        self.crate.write_zip(filename)

    def check_name(self):
        name = self.crate.root_dataset._jsonld.get('name')
        if not name:
            return f"must be set and be at least {ROHUB_NAME_MINLENGTH} characters long"
        if len(name) < ROHUB_NAME_MINLENGTH:
            return f"must be at least {ROHUB_NAME_MINLENGTH} characters long"
        return None

    def set_name(self, name):
        name = str(name)
        if len(name) < ROHUB_NAME_MINLENGTH:
            raise ConversionError(f"\"name\" must be at least {ROHUB_NAME_MINLENGTH} characters long")
        self.crate.root_dataset._jsonld["name"] = name

    def check_description(self):
        description = self.crate.root_dataset._jsonld.get('description')
        if not description:
            return f"must be set"
        return None

    def set_description(self, description):
        description = str(description)
        self.crate.root_dataset._jsonld["description"] = description

    def check_research_area(self):
        research_area = self.crate.root_dataset._jsonld.get('studySubject')
        if not research_area:
            return f"must be set"
        return None

    def set_research_area(self, research_area):
        link = self.research_areas.get(research_area, None)
        if link:
            self.crate.root_dataset._jsonld["studySubject"] = link
        raise ConversionError("Research area not supported by rohub: {research_area}")

    @staticmethod
    def get_research_area_mapping():
        file = import_resources.files('rocrate2rohub').joinpath(RESEARCH_AREA_FILE)
        with open(file) as F:
            lines = F.readlines()
        mapping = dict((line.split('\t') for line in lines))
        return mapping
