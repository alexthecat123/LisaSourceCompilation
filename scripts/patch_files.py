import sys
import os

# Changelog:
# 7/27/2025 - Initial Release
# 7/29/2025 - Added patches for LisaGuide (APIM), TKALERT, and the COMP and INSTALL scripts in the BUILD directory.

# A dictionary of all our find and replace patches. The key is the filename, and each patch is stored as a list with 3 elements.
# These are: the thing to find, the thing to replace it with, and the number of replacements that we expect to perform.
patches = {
    'APIM-IMEVTLOOP' : [['{$U apim/tfilercomm }tfilercomm', '{$U FilerComm }  FilerComm', 1]],
    'APIM-IMFOLDERS' : [['ObjectKind', 'ObjectAKind', 1]],
    'APIM-IMINTERP' : [['ObjectKind', 'ObjectAKind', 3], ['{$U fld.obj      }  FieldEdit,', '{$U fld.obj     }  FieldEdit,\n     {$U FilerComm } FilerComm,', 1]],
    'APIM-IMPATMAT' : [['{$U fld.obj      }  FieldEdit,', '{$U fld.obj     }  FieldEdit,\n     {$U FilerComm } FilerComm,', 1]],
    'APIM-IMSCRIPT' : [['{$U fld.obj      }  FieldEdit,', '{$U fld.obj     }  FieldEdit,\n     {$U FilerComm } FilerComm,', 1]],
    'APIM-IMSIM' : [['{$U fld.obj      }  FieldEdit,', '{$U fld.obj     }  FieldEdit,\n     {$U FilerComm } FilerComm,', 1]],
    'APIM-TCATALOG' : [['nilKind     = 0;', '{nilKind    = 0;', 1], ['fileKind    = 1;', 'fileKind   = 1;}', 1], ['folderkind  = 3;', '{folderkind = 3;', 1], ['computerKind= 10;', 'computerKind=10;}', 1], ['folderPad   = 16;', '{folderPad  = 16;}', 1], ['clockKind   = 19;', '{clockKind  = 19;}', 1], ['toolKind    = 24;', '{toolKind   = 24;', 1], ['disk2Kind   = 27;', 'disk2Kind  = 27;}', 1], ['drawerKind', 'actualDrawerKind', 1], ['deskKind', 'actualDeskKind', 2], ['profileKind', 'actualProfileKind', 2], ['lastKind', 'actualLastKind', 1], ['{$U AlertMgr  } AlertMgr,', '{$U AlertMgr   } AlertMgr,\n   {$U FilerComm } FilerComm,', 1]],
    'APIM-TFDOCCTRL' : [['{$U apim/tfilercomm } tfilercomm', '{$U FilerComm }  FilerComm', 1], ['profileKind', 'actualProfileKind', 2]],
    'APIM-TFILER' : [['{$U Apim/tfilercomm }  Tfilercomm', '{$U FilerComm }  FilerComm', 1], ['drawerKind', 'actualDrawerKind', 3], ['deskKind', 'actualDeskKind', 3], ['profileKind', 'actualProfileKind', 7], ['lastKind', 'actualLastKind', 4], ['iconWidth    = 48;', '{iconWidth   = 48;}', 1], ['iconHt       = 32;', '{iconHt      = 32;}', 1], ['ObjectKind', 'ObjectAKind', 20], ['objectKind', 'ObjectAKind', 2], ['iconData', 'aIconData', 32], ['iconMask', 'aIconMask', 34], ['iconBoxes', 'aIconBoxes', 3]],
    'APIM-TFILER2' : [['deskKind', 'actualDeskKind', 1], ['profileKind', 'actualProfileKind', 3], ['ObjectKind', 'ObjectAKind', 6], ['iconData', 'aIconData', 1], ['iconBoxes', 'aIconBoxes', 2]],
    'APIM-TFILERINT' : [['drawerKind', 'actualDrawerKind', 1], ['deskKind', 'actualDeskKind', 2], ['profileKind', 'actualProfileKind', 1], ['ObjectKind', 'ObjectAKind', 4]],
    'APHP-HP' : [['{t12}', '{t100}', 3]],
    'APCL-CLOCK' : [['{t13}', '{t101}', 1]],
    'APLL-INITFEX' : [['{t5}', '{t103}', 2]],
    'APLT-INIT' : [['{T10}', '{T104}', 2]],
    'APLW-UNITLOTUS' : [['{$U ApLW/UnitSpell.Obj }  UnitSpell,', '{ ApLW/UnitSpell.Obj   UnitSpell, }', 1], ['{$u aplw/sp/spelling.obj }    spelling,', '{ aplw/sp/spelling.obj     spelling, }', 1], ['{$u aplw/sp/verify.obj }      SpVerify,', '{ aplw/sp/verify.obj       SpVerify, }', 1], ['UndoPutDict(fUndoUndo);', '{UndoPutDict(fUndoUndo)}', 1], ['UndoRmvDict(fUndoUndo);', '{UndoRmvDict(fUndoUndo)}', 1], ['DoSpellImid(imid, orecConDwn);', '{DoSpellImid(imid,  orecConDwn);}', 1], ['imidGuess: EndGuessDbox(butnReplace);', '{imidGuess:  EndGuessDbox(butnReplace);}', 1], ['imidGNext: EndGuessDbox(butnRNext);', '{imidGNext:  EndGuessDbox(butnRNext);}', 1], ['NQMore;', '{NQMore}\n            fMoreToQ := FALSE;', 1], ['ParamAlert(ShowReturn (ord (HMReturn))^, \'\', \'\');', '{ParamAlert(ShowReturn (ord(HMReturn))^, \'\', \'\');}', 1], ['SetHzSpell(hzLotus);', '{SetHzSpell(hzLotus)}\ntheDBox.isOpen := FALSE;', 1], ['SpTerminate(closeFile)', 'ok', 1], ['fGenOrec: TF;', 'fGenOrec:  TF;\n    fTstSpell: TF;\n    fTstHeap: TF;\n    fMoreToQ: TF;', 1], ['{T1}', '{T105}', 2]],
    'APLW-TESTBOX' : [['{$U ApLW/UnitSpell.Obj }  UnitSpell,', '{ ApLW/UnitSpell.Obj   UnitSpell, }', 1], ['{$u aplw/sp/spelling.obj }    spelling,', '{ aplw/sp/spelling.obj     spelling, }', 1], ['{$u aplw/sp/verify.obj }      SpVerify,', '{ aplw/sp/verify.obj       SpVerify, }', 1], ['fTstSpell := f;', '{fTstSpell :=  f;}', 1], ['fTstHeap := f;', '{fTstHeap :=  f;}', 1], ['fTrash := FCheckFlag(\'Spell\', fTstSpell);', '{fTrash := FCheckFlag(\'Spell\',  fTstSpell);}', 1], ['fTrash := FCheckFlag(\'Heap\', fTstHeap);', '{fTrash := FCheckFlag(\'Heap\',  fTstHeap);}', 1], ['writeln(\'SpTerminate returned \', ShowReturn (ord (HMReturn))^);', '{writeln(\'SpTerminate returned \', ShowReturn (ord(HMReturn))^);}', 1], ['spStatus := uninitialized;', '{spStatus :=  uninitialized;}', 1], ['SpTerminate(cleanUp)', 'ok', 1], ['LABEL 999;', 'LABEL  999;\n\nTYPE\n    TSpReturn = (ok, notInitialized, illegalString, masterError, unableToLoad, userMemoryFull, wordExists, notFound, limitExceeded);', 1]],
    'APLW-SP-VERIFY' : [['{t1}', '{t105}', 1]],
    'APLW-UNITSCRAP' : [['{t1}', '{t105}', 1], ['{T1}', '{T105}', 2]],
    'APLW-UNITSPELL' : [['{t1}', '{t105}', 1], ['{T1}', '{T105}', 2]],
    'APLW-UNITSRCH' : [['{T1}', '{T105}', 1]],
    'APLC-LCFILER' : [['{T2}', '{T108}', 1], ['{T3}', '{T107}', 1]],
    'APLC-MM-LEX' : [['{T2}', '{T108}', 1], ['{T3}', '{T107}', 1]],
    'APLC-APPDIBOX' : [['{T3}', '{T107}', 5], ['inPutGrahics', 'inPutGraphics', 1]],
    'APBG-BG1' : [['BG1.0', 'BG1/0', 3]],
    'APPW-BTNREAD' : [['{T11}buttons', 'APPW/T11buttons', 1]],
    'APPW-CONFIG' : [['{T11}', '{T109}', 6]],
    'APPW-PREFMAIN' : [['{t11}', '{t109}', 1], ['{T11}', '{T109}', 1]],
    'BUILD-COMP' : [['-newdisk-intrinsic.lib', 'intrinsic.lib', 3]],
    'BUILD-INSTALL' : [['-newdisk-intrinsic.lib', 'intrinsic.lib', 5]],
    'LIBDB-LMSCAN' : [['{$SETC OSBUILT := TRUE }', '{$SETC OSBUILT := TRUE  }\n{$SETC fSymOk := FALSE  }\n{$SETC fTRACE := FALSE  }', 1], ['procedure diffWAdDelete', 'procedure diffWADelete', 1]],
    'LIBFE-FLD.MAIN' : [['{$I libfe/fld.fmt.text}', '{$I libfe/fld/fmt.text }', 1], ['{$I libfe/fld.disp.text}', '{$I libfe/fld/disp.text }', 1], ['{$I libfe/fld.sel.text}', '{$I libfe/fld/sel.text }', 1], ['{$I libfe/fld.word.text}', '{$I libfe/fld/word.text }', 1], ['{$I libfe/fld.edit.text}', '{$I libfe/fld/edit.text }', 1], ['{$I libfe/fld.cmds.text}', '{$I libfe/fld/cmds.text }', 1], ['{$I libfe/fld.font.text}', '{$I libfe/fld/font.text }', 1]],
    'LIBFP-NEWFPLIB' : [['{$I libFP/str2dec }', 'procedure Str2Dec; external;', 1]],
    'LIBHW-KEYBOARD' : [['uses {$U hwint.obj} LibHW/hwint;', 'uses {$U libhw/hwint.obj} hwint;', 1]],
    'LIBOS-PSYSCALL' : [['(*$U object/syscall.obj *)', '(*$U libos/syscall.obj *)', 1]],
    'LIBPL-TFLDERCALL' : [[' paslibequs.text', ' libpl/paslibequs.text', 1]],
    'LIBQD-QDSAMPLE' : [['$U obj:QuickDraw', '$U LIBQD/QuickDraw', 1], ['$U obj:QDSupport', '$U LIBQD/QDSupport', 1]],
    'LIBQP-UBAUDRATE' : [['{$U -newdisk-QP/Hardware} Hardware;', '{$U LIBQP/QP/Hardware} Hardware;', 1]],
    'LIBTK-UTEXT' : [['{$U UABC}', '{$U libtk/UABC}', 1]],
    'TKIN-SOURCE' : [['{$U Tkin/Globals', '{$U APDM/Globals', 1], ['{$U Tkin/Cat', '{$U APDM/Cat', 1]],
    'TKIN-ENTRY' : [['{$U TKIN/Globals}', '{$U APDM/Globals}', 1]],
    'SOURCE-PROFILE' : [['if (discsize <= 9728) or (discsize > 30000)', 'if (discsize <= 9728) or (discsize > 500000)', 1]],
    'SOURCE-DRIVERDEFS' : [['(*$SETC DEBUG1:=TRUE*)', '(*$SETC DEBUG1:=FALSE*)', 1], ['(*$SETC TWIGGYBUILD:=TRUE*)', '(*$SETC TWIGGYBUILD:=FALSE*)', 1]],
    'SOURCE-PASCALDEFS' : [['DEBUG1          .EQU    1', 'DEBUG1          .EQU    0', 1], ['TWIGGYBUILD     .EQU    1', 'TWIGGYBUILD     .EQU    0', 1]],
    'LIBPL-PASMATH' : [['        .END', '\n        .include libpl/pwrii.text\n\n       .END', 1]],
    'LIBPL-PASMISC' : [['.PROC   %%%MISC', '.PROC    %%%MISC\n\n        .include libpl/paslibdefs.text', 1], ['.ref    gotoxy', '.ref    %_FGOTOXY', 1], ['jsr     gotoxy', 'jsr     %_FGOTOXY', 1], ]
}

if len(sys.argv) != 2: # Make sure the user specified the path to their Lisa_Source directory!
    print(f'Usage: python3 {sys.argv[0]} <path_to_source_code>')
    print(f'Example: python3 {sys.argv[0]} Lisa_Source/')
    sys.exit(1)

source_directory = sys.argv[1]
total_patches_applied = 0
total_possible_patches = 7 # The total number of patches for our first "file grafting" round of file mods.

if not os.path.isdir(source_directory): # Make sure the user-specified directory is actually a directory before we continue!
    print('ERROR: The source code path that you specified isn\'t a directory!')
    sys.exit(1)

print()
print('------------ File Grafting ------------')
print()

# I'm not even going to try commenting all this stuff. It's very poorly-written and I don't even want to look at it again.
# But basically it performs some file operations on some of the source files; things that are beyond find and replace.
# Like making new source files and filling them with portions of others.
# Commenting will resume when we get to the find and replace patches later on!
found_file = False
for root, dir, files in os.walk(source_directory):
    for directory in dir:
        if directory.upper() == 'LIBPL':
            found_file = True
            full_path = os.path.abspath(os.path.join(root, directory)) + '/'
            break
if found_file:
    libpl = True;
    found_file = False
    for file_name in os.listdir(full_path):
        if 'LIBPL-PASMATH' in file_name.upper():
            print('LIBPL/PASMATH.TEXT:\n    File already exists, skipping.')
            found_file = True
            break
    if not found_file:
        for root, dir, files in os.walk(source_directory):
            for file_name in files:
                if 'SOURCE-PASMATH' in file_name.upper():
                    full_path_2 = os.path.abspath(os.path.join(root, file_name))
                    if not 'Lisa_Toolkit' in full_path_2:
                        found_file = True
                        break
        if found_file:
            with open(full_path_2, 'r', encoding='iso-8859-1') as source_pasmath:
                contents = source_pasmath.readlines()
            with open(full_path + 'LIBPL-PASMATH.TEXT', 'w', encoding='iso-8859-1') as libpl_pasmath:
                libpl_pasmath.writelines(contents)
            print('LIBPL/PASMATH.TEXT:\n    Created file as a copy of SOURCE/PASMATH.TEXT.')
            total_patches_applied += 1
        else:
            print('WARNING: Can\'t find SOURCE/PASMATH.TEXT. So we can\'t create LIBPL/PASMATH.TEXT!')
else:
    libpl = False;
    print('WARNING: Can\'t find a LIBPL directory. The operations on PASMATH, PASMOVE, PASMISC, and PASRANGE will be skipped.')

if libpl:
    found_file = False
    osint = False
    for root, dir, files in os.walk(source_directory):
            for file_name in files:
                if 'SOURCE-OSINTPASLIB' in file_name.upper():
                    full_path_2 = os.path.abspath(os.path.join(root, file_name))
                    if not 'Lisa_Toolkit' in full_path_2:
                        osint = True
                        break
    if osint:
        for file_name in os.listdir(full_path):
            if 'LIBPL-PASMOVE' in file_name.upper():
                print('LIBPL/PASMOVE.TEXT:\n    File already exists, skipping.')
                found_file = True
                break        
        if not found_file:
            with open(full_path_2, 'r', encoding='iso-8859-1') as source_osintpaslib:
                osintpaslib = source_osintpaslib.readlines()
            for index, line in enumerate(osintpaslib):
                if '; File: PASMOVE.TEXT' in line:
                    start_index = index
                if '; File: PASRANGE.TEXT' in line:
                    stop_index = index
            new_contents = []
            for index, a in enumerate(range(start_index, stop_index)):
                new_contents.append(osintpaslib[index + start_index])
            new_contents.append('       .END')
            with open(full_path + 'LIBPL-PASMOVE.TEXT', 'w', encoding='iso-8859-1') as libpl_pasmove:
                libpl_pasmove.writelines(new_contents)
            print('LIBPL/PASMOVE.TEXT:\n    Created file from data in SOURCE/OSINTPASLIB.TEXT.')
            total_patches_applied += 1

    else:
        osint = False
        print('WARNING: Can\'t find SOURCE/OSINTPASLIB.TEXT. Operations on PASMOVE, PASMISC, and PASRANGE will be skipped!')
    if osint:
        found_file = False
        for file_name in os.listdir(full_path):
            if 'LIBPL-PASMISC' in file_name.upper():
                print('LIBPL/PASMISC.TEXT:\n    File already exists, skipping.')
                found_file = True
                break
        if not found_file:
            with open(full_path_2, 'r', encoding='iso-8859-1') as source_osintpaslib:
                osintpaslib = source_osintpaslib.readlines()
            for index, line in enumerate(osintpaslib):
                if '; File: PASMISC.TEXT' in line:
                    start_index = index
                if '; File: PASMOVE.TEXT' in line:
                    stop_index = index
            new_contents = []
            for index, a in enumerate(range(start_index, stop_index)):
                new_contents.append(osintpaslib[index + start_index])
            new_contents.append('       .END')
            with open(full_path + 'LIBPL-PASMISC.TEXT', 'w', encoding='iso-8859-1') as libpl_pasmisc:
                libpl_pasmisc.writelines(new_contents)
            print('LIBPL/PASMISC.TEXT:\n    Created file from data in SOURCE/OSINTPASLIB.TEXT.')
            total_patches_applied += 1

        found_file = False
        for file_name in os.listdir(full_path):
            if 'LIBPL-PASRANGE' in file_name.upper():
                print('LIBPL/PASRANGE.TEXT:\n    File already exists, skipping.')
                found_file = True
                break
        if not found_file:
            with open(full_path_2, 'r', encoding='iso-8859-1') as source_osintpaslib:
                osintpaslib = source_osintpaslib.readlines()
            for index, line in enumerate(osintpaslib):
                if '; File: PASRANGE.TEXT' in line:
                    start_index = index
                if '; File: PASSCOMP.TEXT' in line:
                    stop_index = index
            new_contents = []
            for index, a in enumerate(range(start_index, stop_index)):
                new_contents.append(osintpaslib[index + start_index])
            new_contents.append('       .END')
            with open(full_path + 'LIBPL-PASRANGE.TEXT', 'w', encoding='iso-8859-1') as libpl_pasrange:
                libpl_pasrange.writelines(new_contents)
            print('LIBPL/PASRANGE.TEXT:\n    Created file from data in SOURCE/OSINTPASLIB.TEXT.')
            total_patches_applied += 1


found_file = False
for root, dir, files in os.walk(source_directory):
    for file_name in files:
        if 'LIBOS-SYSCALL' in file_name.upper():
            full_path = os.path.abspath(os.path.join(root, file_name))
            if not 'Lisa_Toolkit' in full_path:
                found_file = True
                break
if found_file:
    with open(full_path, 'r', encoding='iso-8859-1') as libos_syscall:
        contents = libos_syscall.readlines()
        for line in contents:
            if 'Copyright 1983, 1984, Apple Computer Inc.' in line:
                print('LIBOS/SYSCALL.TEXT:\n    Already replaced with SOURCE/SYSCALL, skipping.')
                found_file = False
                break
        if found_file:
            found_file = False
            for root, dir, files in os.walk(source_directory):
                for file_name in files:
                    if 'SOURCE-SYSCALL' in file_name.upper():
                        full_path_2 = os.path.abspath(os.path.join(root, file_name))
                        if not 'Lisa_Toolkit' in full_path_2:
                            found_file = True
                            break
            if found_file:
                print('LIBOS/SYSCALL.TEXT:')
                with open(full_path_2, 'r', encoding='iso-8859-1') as source_syscall:
                    contents = source_syscall.readlines()
                with open(full_path, 'w', encoding='iso-8859-1') as libos_syscall:
                    libos_syscall.writelines(contents)
                print('    Replaced contents with that of SOURCE/SYSCALL.TEXT.')
                total_patches_applied += 1

            else:
                print(f'WARNING: Failed to find file SOURCE/SYSCALL.TEXT. So we can\'t update LIBOS/SYSCALL.TEXT!')
else:
    print(f'WARNING: Failed to find file LIBOS/SYSCALL.TEXT. It will not be modified!')


found_file = False
print('TKALERT.TEXT:')
for root, dir, files in os.walk(source_directory):
    for file_name in files:
        if 'TKALERT' in file_name.upper() and 'LINKMAPS AND MISC. 3.0' in root.upper():
            full_path = os.path.abspath(os.path.join(root, file_name))
            if not 'Lisa_Toolkit' in full_path:
                found_file = True
                break
if found_file:
    with open(full_path, 'r', encoding='iso-8859-1') as tkalert:
        contents = tkalert.readlines()
    found_file = False
    for root, dir, files in os.walk(source_directory):
        for file_name in files:
            if 'TKALERT' in file_name.upper() and not 'LINKMAPS AND MISC. 3.0' in root.upper():
                full_path_2 = os.path.abspath(os.path.join(root, file_name))
                if not 'Lisa_Toolkit' in full_path_2:
                    found_file = True
                    break
    if not found_file:
        with open(full_path, 'r', encoding='iso-8859-1') as tkalert:
            contents = tkalert.readlines()
        with open(source_directory + '/LISA_OS/TKALERT.TEXT', 'w', encoding='iso-8859-1') as tkalert_new:
            tkalert_new.writelines(contents)
        print('    Created file with contents of Linkmaps and Misc. 3.0/TKALERT.TEXT.')
        total_patches_applied += 1

    else:
        print(f'    LISA_OS/TKALERT.TEXT already exists, skipping.')
else:
    print(f'    WARNING: Failed to find file Linkmaps and Misc. 3.0/TKALERT.TEXT!')

found_file = False
for root, dir, files in os.walk(source_directory):
    for file_name in files:
        if 'APLW-UNITLOTUS' in file_name.upper():
            full_path = os.path.abspath(os.path.join(root, file_name))
            if not 'Lisa_Toolkit' in full_path:
                found_file = True
                break
if found_file:
    found_file = False
    with open(full_path, 'r', encoding='iso-8859-1') as unitlotus:
        contents = unitlotus.readlines()
    for line in contents:
        if 'TSpReturn = (ok, notInitialized, illegalString, masterError, unableToLoad, userMemoryFull, wordExists, notFound, limitExceeded);' in line:
            print('APLW/UNITLOTUS.TEXT:\n   Already patched, skipping.')
            found_file = True
            break
    if not found_file:
        for index, line in enumerate(contents):
            if 'CONST dxScroll = 16;' in line:
                found_file = True
                contents[index - 1] = '\nTYPE\n    TSpReturn = (ok, notInitialized, illegalString, masterError, unableToLoad, userMemoryFull, wordExists, notFound, limitExceeded);\n\n'
                break
        if found_file:
            with open(full_path, 'w', encoding='iso-8859-1') as unitlotus:
                unitlotus.writelines(contents)
            print('APLW/UNITLOTUS.TEXT:\n   Added type definitions near the top of the file.')
            total_patches_applied += 1

else:
    print('WARNING: Failed to find file APLW/UNITLOTUS.TEXT. It will not be modified!')

print()
if total_patches_applied == total_possible_patches:
    print(f'Successfully performed {total_patches_applied}/{total_possible_patches} file grafts.')
elif total_patches_applied == 0:
    print(f'No file grafts applied. Your code has probably already been patched!')
else:
    print(f'WARNING: Performed {total_patches_applied}/{total_possible_patches} file grafts. Check the output above to see where the problems occurred!')


# Yay, time for the more elegant find and replace code!
print()
print('------------ Patches ------------')
print()

total_patches_applied = 0
total_possible_patches = 0

for entry in patches: # Iterate through each file in our patch dictionary.
    for patch in patches[entry]: # And then iterate through each patch for that file.
        total_possible_patches += patch[2] # Sum up all the individual patches to report to the user later.

for entry in patches: # Iterate through all the files we need to patch again.
    proper_name = entry.replace('-', '/') + '.TEXT' # And convert the filename into a nice and pretty Lisa-formatted name.
    found_file = False
    for root, dir, files in os.walk(source_directory): # Iterate through all the files in the Lisa_Source directory.
        if found_file == True:
            break
        for file_name in files: # And check each file's name to see if it matches the file that we want to patch.
            if entry + '.TEXT' in file_name.upper():
                full_path = os.path.abspath(os.path.join(root, file_name))
                # If we find one, and it's not in the Lisa_Toolkit or LISA_OS/LIBHW directories (which contain duplicate files we don't care about), then let's patch it!
                if (not 'Lisa_Toolkit' in full_path) and (not 'LISA_OS/LIBHW' in full_path) and (not 'OS exec files' in full_path):
                    found_file = True
                    break
    if found_file: # If we actually found a file, then start by printing out its Lisa-formatted name.
        print(f'{proper_name}:')
        with open(full_path, 'r', encoding='iso-8859-1') as source_file: # Then open it up and read it in as a list of lines.
            contents = source_file.readlines()
        for patch in patches[entry]: # Iterate through each patch that we want to perform.
            success_count = 0
            for index, line in enumerate(contents): # And search through each line in the file until we find the "find string" that we need to replace.
                if patch[0] in line:
                    contents[index] = line.replace(patch[0], patch[1]) # Once we do, replace it with the "replace string"
                    success_count += 1 # Increment the success counter for this file
                    total_patches_applied += 1 # And the total success counter too
            if success_count != patch[2]: # If we didn't patch all the instances we were expecting to, warn the user.
                print(f'    WARNING: Patched {success_count} instances of \"{patch[0]}\", expected {patch[2]} instances.')
            else: # Otherwise tell them that we succeeded.
                print(f'    Patched {success_count}/{patch[2]} instances of \"{patch[0]}\".')
        # Now open the file up again in write mode and write our changes back out to it.
        with open(full_path, 'w', encoding='iso-8859-1') as dest_file:
            dest_file.writelines(contents)
    else: # If we failed to find the file earlier, then tell the user as much!
        print(f'WARNING: Failed to find file {proper_name}. It will not be patched!')

print()
if total_patches_applied == total_possible_patches: # If we applied all the patches, tell the user we succeeded.
    print(f'Successfully applied {total_patches_applied}/{total_possible_patches} patches.')
elif total_patches_applied == 0: # If we applied no patches, tell them that the code has probably already been patched.
    print(f'No patches applied. Your code has probably already been patched!')
else: # If we're somewhere in between those two extremes, then the user probably has something to worry about!
    print(f'WARNING: Applied {total_patches_applied}/{total_possible_patches} patches. Check the output above to see where the problems occurred!')