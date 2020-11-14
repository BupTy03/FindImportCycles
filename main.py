# -*- coding: utf-8 -*-
import sys
import re
from os import listdir
from os import path


class SourceFileInfo(object):
    def __init__(self, moduleName, importsList):
        self.ModuleName = moduleName
        self.ImportsList = importsList


def is_cpp_source_file(file):
    (name, ext) = path.splitext(file)
    return ext in (".cpp", ".ixx")


def get_source_file_imports_info(file):
    moduleName = ""
    importsList = []

    moduleNameRegex = re.compile("^\s*export\s+module\s+(.*)\s*;$")
    moduleImport = re.compile("^\s*import\s+(.*)\s*;$")
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            groups = re.findall(moduleNameRegex, line)
            if groups and len(groups) > 0:
                moduleName = groups[0]
            else:
                groups = re.findall(moduleImport, line)
                if groups and len(groups) > 0:
                    importsList.append(groups[0])

    return SourceFileInfo(moduleName, importsList)


def main():
    if len(sys.argv) != 2:
        print("Wrong arguments count, expected 1")
        return

    dirPath = sys.argv[1]
    if not path.isdir(dirPath):
        print("'{}' is not a path of existing directory".format(dirPath))
        return

    print("Path to directory: '{}'".format(dirPath))

    print("Files:")
    sourceFiles = [path.join(dirPath, f) for f in listdir(dirPath) if path.isfile(path.join(dirPath, f)) and is_cpp_source_file(f)]
    for f in sourceFiles:
        print(f)

    sourceFilesInfo = [get_source_file_imports_info(sourceFile) for sourceFile in sourceFiles]
    for sfinf in sourceFilesInfo:
        print("Module name: '{}', Imports: {}".format(sfinf.ModuleName, sfinf.ImportsList))

    pairs = set()
    for outerInfo in sourceFilesInfo:
        for interInfo in sourceFilesInfo:
            if interInfo == outerInfo or (interInfo.ModuleName, outerInfo.ModuleName) in pairs:
                continue

            if outerInfo.ModuleName in outerInfo.ImportsList:
                print("Error: module '{}' imports self".format(outerInfo.ModuleName))

            if outerInfo.ModuleName in interInfo.ImportsList and interInfo.ModuleName in outerInfo.ImportsList:
                pairs.add((outerInfo.ModuleName, interInfo.ModuleName))
                print("Error: modules '{}' and '{}' import each other".format(outerInfo.ModuleName, interInfo.ModuleName))


if __name__ == "__main__":
    main()

