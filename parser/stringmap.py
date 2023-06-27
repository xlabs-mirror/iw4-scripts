from pathlib import Path
from re import compile
from subprocess import run, PIPE

# class StringMap():
#     file: Path

#     def search(self, query: str) -> list[str]:
#         pass

class StringMaps():
    pattern = compile(r"REFERENCE\s+(.*?)\s+LANG_ENGLISH\s+\"(.*?)\"")
    es_cmd = ['es','-regex','localizedstrings\\\\.*.str']
    strings: dict[str, dict[str, str]] = {}

    def get_files(self):
        files = run(self.es_cmd, stdout=PIPE).stdout.strip().splitlines()
        print("Got", len(files), "files from es")
        return files
    
    def parse_files(self, files: list[str]):
        for file in files:
            print("Parsing", file)
            self.parse_file(Path(file.decode('utf-8')))

    def parse_file(self, file: Path):
        with file.open('r', encoding='latin-1') as f:
            file_contents = f.read()
        matches = self.pattern.findall(file_contents)
        lang = str(file).replace('\\localizedstrings','').split('\\')[-2] or 'english'
        if lang == 'iw4x_unpacked': lang = 'english'
        # lang = file.parent.parent.name
        if lang not in self.strings: self.strings[lang] = {}
        print(f"Found {len(matches)} strings in {file.name} ({lang})")
        for match in matches:
            key = match[0]
            value = match[1]
            self.strings[lang][key] = value
