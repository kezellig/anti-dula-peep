# i think i may have overcomplicated this LOL
import shutil, zipfile, re, logging
from pathlib import Path

srcDir = Path('src/')
tmpDir = Path('tmp/') # no i didnt spell it tmp to make it line up nicely, why do you ask?
# also didnt end up needing it

outDir = Path('out/')
outXPI = Path('temp.xpi')
outZIP = Path('temp.zip')

def clearFiles():
    shutil.rmtree(outDir, ignore_errors=True)
    shutil.rmtree(tmpDir, ignore_errors=True)

def build(mode, pack=False):
    clearFiles()
    shutil.copytree(srcDir, outDir)
    
    with open(outDir/'manifest.json', 'r+') as manifestFile:
        splitManifest = splitText(manifestFile.read())

        if not mode in splitManifest: 
            print(f'mode "{mode}" not found, using default')
            mode = 'default'

        parsedManifest = removeTrailingCommas(splitManifest[mode])

        manifestFile.seek(0)
        manifestFile.write(parsedManifest)
        manifestFile.truncate()

    # TODO: option to export packaged extentions


# variable names are hard
mustachePattern = re.compile('%%([\s]*.*?[\s]*)%%', re.DOTALL)
def splitText(text):
    mustaches = re.finditer(mustachePattern, text)

    blocksByMode = {}
    stack = []

    for mustache in mustaches:
        body = mustache.group(1).strip().split()

        match body:
            case ['only', mode]:
                if not mode in blocksByMode: blocksByMode[mode] = []

                blocksByMode[mode].append([mustache.start(), mustache.end()])
                stack.append(mode)

            case ['end']:
                if not stack:
                    print('yaknow you need to start a block to end it right?')

                blocksByMode[stack[-1]][-1].append(mustache.start())
                blocksByMode[stack[-1]][-1].append(mustache.end())

                stack.pop()

            case _:
                print('*sigh* you probably typod')

    # too much nesting augh
    outputsByMode = {}
    outputsByMode['default'] = text
    for mode in blocksByMode:
        outputsByMode[mode] = text

    for blockMode, blocks in blocksByMode.items():
        for currentMode, output in outputsByMode.items():
            if blockMode == currentMode:
                for block in blocks:
                    outputsByMode[currentMode] = outputsByMode[currentMode] \
                        .replace(text[block[0]:block[3]], text[block[1]:block[2]])
            else:
                for block in blocks:
                    outputsByMode[currentMode] = outputsByMode[currentMode] \
                        .replace(text[block[0]:block[3]], "")
        
    return outputsByMode


trailingCommaPattern =  re.compile('\,(?=\s*?[\}\]])')
def removeTrailingCommas(text):
    trailingCommas = re.finditer(trailingCommaPattern, text)
    for comma in trailingCommas:
        text = text[:comma.start()] + text[comma.end():]

    return text

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("mode")
    parser.add_argument("--watch", "-w", action="store_true")
    # TODO: watch mode

    args = parser.parse_args()
    build(args.mode)

