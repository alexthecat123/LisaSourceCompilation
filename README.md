# Lisa OS Source Code Compilation
All the info needed to compile the Apple Lisa's operating system (LOS) from source!
<img width="1081" alt="SCR-20250628-snpg" src="https://github.com/user-attachments/assets/1ca63c0d-61a0-4f4d-a1a9-7089b22332e7" />

# Background
In January of 2023, Apple released the source code to the Lisa Office System to celebrate the Lisa's 40th birthday. It's a whole lot of code though (20+ MB over 1000+ files), so nobody had undertaken the task of trying to compile it all. Until January of 2025, when I started what ended up being a 5-month endeavor that culminated in a fully-working copy of the Lisa OS and its apps, all freshly compiled in 2025! And this repo contains (almost) everything that you'll need to replicate it yourself!

# What's in this repo?
Four things!
- In the ```src``` directory, you can find all the files that I created as part of the build process. This includes build scripts and new source files that I had to make. The directory structure in ```src``` is identical to the structure in which these files should be organized on the actual Lisa hard disk. These are all included in the disk image I'm about to talk about; I just put them here too for easy viewing in a modern text editor.
- In the ```scripts``` directory, you'll find some scripts that patch the source files and help you get them onto your Lisa. We'll talk more about them later.
- ```LOS Compilation Base.image.zip``` is a disk image compatible with ESProFile, Cameo/Aphid, and ArduinoFile that contains everything that I can possibly provide to get you started with compiling LOS without violating Apple's license agreement. Of course, unzip it before you do anything with it! This disk image has stock LOS 3.0 and the Workshop installed, as well as all my build scripts, new source files I had to create, my "incredibly beautiful" application icons, and a couple programs like ICONEDIT that I had to grab from other Lisa disks, as well as plenty of disk space for all the source files you'll have to copy over and the object code that gets generated. You can use the raw-to-dc42 tool that comes with LisaEm to convert this to a DC42 image that you can actually mount and use in LisaEm.
- ```glue.c``` is a replacement for LisaEm's standard glue.c that will allow your custom copy of LOS to function in LisaEm, even after you've replaced the stock copy of SYSTEM.OS with your own. We'll talk about why this is necessary later.

# What's not in this repo?
The actual LOS source code itself. Thanks to Apple's really weird license on the code, I can't share it here. So you'll have to patch some of the source files, copy everything into my disk image, and then use my build scripts to build everything. But don't worry, all the info needed to do all of this (and scripts that you can use to automate pretty much the entire process) is right here!

# Source Code Structure and the Lisa OS Architecture
The LOS source code can be divided into 3 main parts. Going from highest level of abstraction to lowest level of abstraction, these are:
- Applications
- Libraries
- The OS Itself

## Applications
The apps include not only the 7/7 apps (LisaWrite, LisaCalc, etc) but also some other stuff:
| App Name | Description |
| -------- | ----------- |
| APBG     | Business Graphics AKA LisaGraph. |
| APCL     | The Clock tool. |
| APDM     | The Desktop Manager; the graphical shell of LOS. |
| APEW     | The Environments Window (the thing that lets you pick whether you want to boot into LOS or the Workshop). |
| APHP     | The Calculator tool. Not sure what HP means, maybe because HP makes calculators or something? |
| APIN     | The Installer application that runs when you boot from the LOS install diskettes. |
| APLC     | LisaCalc. |
| APLD     | LisaDraw, called the Graphics Editor during development. |
| APLL     | LisaList. |
| APLP     | LisaProject. |
| APLT     | LisaTerminal. |
| APLW     | LisaWrite. Its codename during development was Lotus. |
| APPW     | The Preferences Window. |

Note that Apple didn't release LisaWrite's dictionary as part of the source code release because it's still copyrighted by HM. And they also omitted some of the source files that talk to the dictionary file for some reason, so we actually have to make some changes to the LisaWrite source code to patch out all the dictionary code and get it to compile.

By default, files visible in the Workshop are NOT visible in the graphical Office System itself. So once you've built an application, you have to do a couple extra things in order to actually get it to appear in the Office System. First, you have to copy the application binary into the root of your hard disk and rename it to {TXXX}Obj where XXX is the application's "tool number". This can be any number you want, but be careful to search through the source code in case there are any instances where it's hard-coded into the application which you would need to modify! Now that you've given it the proper name, you run INSTALLTOOL from the Workshop, which will ask you a few questions about your app, including its tool number. Once you answer its questions and give your app a name, it'll install the app into the Office System with whatever name you provided! And by the way, this is all just for reference; my build scripts do it for you!

There's one more thing that you have to do though: make an application phrase file. You'll notice that all the Office System apps 
come with an "alert" file somewhere in their source directory, which contains all the strings that show up in the app's dialog boxes and menu bar menus. This file has to be run through a Workshop program called ALERT, which will generate a phrase file from this data that the Alert Manager can understand. The resulting phrase file must be saved as {TXXX}PHRASE in order for the Office System to find it. And once again, my build scripts will do this for you!

Since the Environments Window (APEW) and Desktop Manager (APDM) don't get installed into the Office System (the Environments Window loads before the Office System and the Desktop Manager is the Office System), you don't have to use INSTALLTOOL for either of them.

The Environments Window is the first shell that gets loaded by the system, so it gets saved as SYSTEM.SHELL on your disk. It then loads the Desktop Manager, and in order to have APEW see your Desktop Manager instance, it must be saved as shell.Something, where Something is the name that you want the shell to show up with in the Environments Window. To allow the use of both the original LOS shell and our newly-compiled replacement, my build scripts install the new Desktop Manager as shell.AlexTheCat123 and leave the old shell.Office System untouched. This will cause your newly-compiled shell to show up in the Environments Window as AlexTheCat123. APEW doesn't require a phrase file, but APDM does, and it's normally saved as SYSTEM.DMALERTSPHRASE. But to avoid overwriting the original Office System's phrase file, my build scripts save it as SYSTEM.DMALEXALERTSPHRASE instead.

Both APLC and APBG require a file called {Txxx}tables, which is made from aplc/mm/tables.text, but it's not just a direct copy of that file. To generate it, you have to build LCORBGLIB (which we'll talk about in a second) in debug mode, and it'll automatically read the file and generate {Txxx}tables. Then rebuild in regular mode and it'll use the newly-made table file. But that's really annoying, so I've just included a copy from the original LisaCalc diskette that the build scripts will use instead. APLC also requires some LisaDraw picture files for things like the "function hints" page, so I've included copies of those from the original disk as well. The build scripts will put them in the proper place for you!

APLW requires a file called {TXXX}search.lotus that contains some strings related to LisaWrite's Find tool, which has to be grabbed from the original LisaWrite diskette. I've already done this for you and included it in the base disk image for the build scripts to use!

To put APIN (the OS installer) onto an install diskette, the build scripts simply copy the APIN binary over to the install disk as SYSTEM.SHELL. And it also requires a phrase file, which gets copied over as officephrase. There's an extra library required to get the installer to run, but we'll talk about that later.

## Libraries
The system libraries are used by all of the applications, but not by the OS itself. The Lisa has 21 libraries in total; I've capitalized the letters that give the library its name in each description:

| Library | Description |
| ------- | ----------- |
| LIBAM   | The Alert Manager. Handles displaying alerts in dialog boxes. |
| LIBDB   | The DataBase library. |
| LIBFC   | The FilerComm library. Handles communications between apps and the Lisa Filer. |
| LIBFE   | The Field Editor. Handles the entry of text into text fields. |
| LIBFM   | The Font Manager. |
| LIBFP   | The Floating Point library. |
| LIBHW   | The low-level HardWare interface library. |
| LIBIN   | The InterNational library. Handles conversion between charsets. |
| LIBOS   | The OS library. Basically just syscall stuff. |
| LIBPL   | The PascaL runtime library. |
| LIBPM   | The Parameter RAM library. |
| LIBPR   | The PRinter library. |
| LIBQD   | QuickDraw. |
| LIBQP   | QuickPort, a framework that can be used to quickly port apps from the Workshop to LOS. |
| LIBSB   | The ScrollBar library. |
| LIBSM   | The Storage Manager. Handles the allocation and management of heap zones. |
| LIBSU   | The Scrap Unit (essentially clipboard) library. |
| LIBTE   | The Table Editor. Handles data entry and storage in tables (like spreadsheets). |
| LIBTK   | The ToolKit, an API for developing graphical LOS apps. |
| LIBUT   | The Universal Text library. Not really sure what it does... |
| LIBWM   | The Window Manager. |

These libraries don't get linked to form 21 separate library files; they instead get compacted into 8 files, some of which contain components of multiple libraries. These 8 files are:

| Library File  | Description |
| ------------- | ----------- |
| IOSPASLIB.OBJ | The Pascal runtime library. Nothing but LIBPL. |
| IOSFPLIB.OBJ  | The floating point library. Nothing but LIBFP. |
| PRLIB.OBJ     | The printer library. Nothing but LIBPR.        |
| QPLIB.OBJ     | The QuickPort library. Nothing but LIBQP.      |
| TKLIB.OBJ     | The ToolKit. Nothing but LIBTK.                |
| TK2LIB.OBJ    | More ToolKit stuff. Nothing but LIBTK.         |
| SYS1LIB.OBJ   | A bunch of stuff. Contains LIBFC, a little bit of LIBHW, LIBPM, LIBSM, LIBFM, LIBQD, LIBWM, a little bit of LIBPR, LIBSB, LIBAM, LIBSU, a little bit of LIBDB, LIBFE, LIBIN, and LIBUT. |
| SYS2LIB.OBJ   | Everything that didn't get put into SYS1LIB. So LIBTE and the rest of LIBDB. |

And note that most of LIBHW gets linked to form SYSTEM.LLD instead of one of these library files. LLD stands for Low-Level Drivers, and this file is loaded by the OS very early in the boot process to allow it to interface with the Lisa's hardware. Since this file is loaded before the MMU is up (in fact, the code in this file is what the loader uses to bring the MMU up), we link it with the +P (physical link) option so that it's linked for physical address space instead of logical address space.

Another library that produces more than just an intrinsic library is LIBPR. On top of producing PRLIB.OBJ, the files in that directory also produce all of the following files:

| File                           | Purpose |
| ------------------------------ | ------- |
| System.Print                   | The background printing process than handles scheduling and executing print jobs. |
| System.PR_Imagewriter / II DMP | Printer driver for the ImageWriter Printer. |
| System.PR_Daisy Wheel Printer  | Printer driver for the Daisy Wheel Printer. |
| System.PR_Ink Jet Printer      | Printer driver for the Canon Inkjet Printer. |
| PARBTNDATA                     | Parent Button Data file; contains the locations/attributes of buttons in the main print dialog. |
| SYSTEM.PARENT.PHRASE           | Parent phrase file; contains the alerts shown by System.Print. |
| SYSTEM.PR.PHRASE               | Printer phrase file; more general alerts related to printing. |
| CIBTNDATA                      | C-Itoh Button Data file; locations/attributes of buttons in the ImageWriter printer dialog. |
| SYSTEM.CIALERTS.PHRASE         | C-Itoh phrase file; contains alerts related to the ImageWriter printer. |
| CNBTNDATA                      | Canon Button Data file; locations/attributes of buttons in the Canon inkjet printer dialog. |
| SYSTEM.CNALERTS.PHRASE         | Canon phrase file; contains alerts related to the Canon inkjet printer. |
| DWBTNDATA                      | Daisy Wheel Button Data file; locations/attributes of buttons in the daisy wheel printer dialog. |
| SYSTEM.DWALERTS.PHRASE         | Daisy Wheel phrase file; contains alerts related to the Daisy Wheel printer. |


Yeah, it's a whole lot. Figuring out which files got linked to form each one was quite a task!

There were also some missing source files in LIBPL and LIBFP that I had to recreate. I did this by disassembling the original IOSPASLIB and IOSFPLIB, finding the necessary missing code in the disassembly, and creating new source files to house it. Then we just run these through the assembler and link them with everything else when we build IOSPASLIB and IOSFPLIB. And since they're based on the original IOSPASLIB and IOSFPLIB instead of source code, I can include the files in the disk image that I 
provide! The recreated files are LIBPL/PASMEM.TEXT, LIBPL/PWRII.TEXT, and LIBFP/STR2DEC.TEXT. And also LIBPL/PASLIB.TEXT, which is just a dummy unit file with nothing in it.

There's an extra library file called LCORBGLIB.OBJ that is actually linked from code in the APLC (LisaCalc) directory, but this isn't really a system library. It's just used to hold code that's shared between APLC and APBG (LisaGraph), hence LC OR BG LIB.

All of these library files are intrinsic libraries, meaning that they're dynamically linked instead of statically linked. This way, only a single copy of the library has to be kept on disk and any application that needs to use library code can pull it from that single copy instead of requiring that a copy of the library be inserted in each program executable at link time.

There's a file on the disk called INTRINSIC.LIB that tells the Lisa OS what intrinsic library files are installed, where to find them, and what units are contained within each one. Whenever you make a new intrinsic library or recompile an existing one, INTRINSIC.LIB must be updated using the Workshop's IUMANAGER tool to account for these changes. Luckily, my build scripts will do this for you after they link each intrinsic library!

## The OS
The entirety of the Lisa's OS (most of the files in the SOURCE directory on the Lisa, or the OS directory on your modern machine) gets linked into one single file: SYSTEM.OS. This is just a standard binary, except that we link it with the -O (omit OS data record; it's the OS itself so it doesn't need a data record) and +F (link for MMU domain 0; the OS runs in context 0 all the time) options. But there are more files that are OS-adjacent, namely all of the SYSTEM.CD_* files and the SYSTEM.BT_* files. 

There are 10 SYSTEM.CD files, which are Configurable Drivers for all of the hardware devices in the Lisa. They are the following:
| Configurable Driver      | Purpose |
| ------------------------ | ------- |
| SYSTEM.CD_2 Port Card    | 2-port parallel card driver. |
| SYSTEM.CD_Archive Tape   | Priam DataTower tape drive driver. |
| SYSTEM.CD_Console        | Text console driver. |
| SYSTEM.CD_Modem A        | Modem driver. |
| SYSTEM.CD_Parallel Cable | Parallel cable (parallel port printer) driver. |
| SYSTEM.CD_Priam Card     | Priam DataTower interface card driver. |
| SYSTEM.CD_Priam Disk     | Priam DataTower hard disk driver. |
| SYSTEM.CD_Profile        | ProFile hard disk driver. |
| SYSTEM.CD_Serial Cable   | Serial port driver. |
| SYSTEM.CD_Sony           | Sony floppy drive driver. |

By default, SYSTEM.CD_Profile only supports drives up to 16MB thanks to the following lines in SOURCE/PROFILE.TEXT (the main source file that forms the ProFile driver):
```
if (discsize <= 9728) or (discsize > 30000)
    then drivetype:= T_Profile (* set drivetype to profile *)
```
This says that the drive gets considered a 5MB ProFile (T_Profile) if it's 5MB or smaller (9728 blocks or smaller) or if it's larger than about 16MB (30000 blocks). Otherwise, if it's between this range, then the actual capacity of the drive gets utilized. So this means that we can't make a volume any larger than 16MB because it'll get formatted to 5MB, but we certainly need more than this in order to fit all the code on the disk. So we can patch the driver by changing the 30000 to some massive number so that drives get utilized to their full potential up to a much larger size. And this allows us to have a 50-ish MB drive like the image that's in this GitHub repo. You can go much bigger than this even (theoretically 8GB), but there's no reason to.

Interestingly enough, we have some of the code necessary to build a SYSTEM.CD_Twiggy (SOURCE/TWIGGY.TEXT), but we seem to be missing SOURCE/TWIGGYASM.TEXT. If we recreated that file though, I think we could add Twiggy support back to LOS 3.0!

We've also got 4 SYSTEM.BT files, which are BooTloaders for the different devices that the Lisa can boot from. They are:
| Bootloader        | Device |
| ----------------- | ------ |
| SYSTEM.BT_PRIAM   | Bootloader for the Priam DataTower hard disk. |
| SYSTEM.BT_PROFILE | Bootloader for the ProFile hard drive. |
| SYSTEM.BT_SONY    | Bootloader for the Sony floppy drive. |
| SYSTEM.BT_TWIG    | Bootloader for the Twiggy floppy drive. Useless since we don't have a CD for the Twiggy. |

Note that simply having the bootloader files sit on your hard disk doesn't really do anything. In order to actually use one as the bootloader of your disk, you must write it into the disk's boot blocks. Whenever the OS initializes a disk, it automatically copies the bootloader from the appropriate BT file into the boot blocks of that disk, but there's also an FS_Utilities() syscall (see LIBOS/PSYSCALL.TEXT and SOURCE/FSINIT2.TEXT for more info) that will copy the appropriate BT file into the boot blocks without destroying all the data on the disk.

## The Lisa Boot Process
Let's go over what happens from the moment you choose a disk in the Startup From... menu to the moment that the desktop appears.

First, after you choose to boot from a disk, the Lisa boot ROM loads the first block of that disk into RAM and checks if it's bootable by looking for the signature "AAAA" in the disk's tag bytes. Then, if this is found, it jumps to the start of that block, which contains the beginning of the bootloader code from SYSTEM.BT.

This code is written in assembly and is called the "loader loader" because it's what loads the loader itself. You can find the ProFile version of the loader loader in SOURCE/LDPROF.TEXT. It basically just loads the loader itself into RAM, gets things set up to run Pascal code, loads the code necessary to parse the filesystem, and then hands control over to the actual loader.

The "real" loader (which also came from SYSTEM.BT) is mostly written in Pascal (SOURCE/LOADER.TEXT) and is responsible for several things. First, it loads the debugger (SYSTEM.DEBUG) if it's available. Then it loads all the hardware interface routines from SYSTEM.LLD into RAM so that it can do things like control the MMU, talk to the COP, and so on. Then it finds the file SYSTEM.OS and begins parsing it to find the OS's code segments. As an aside, a single program on the Lisa can have a max of 32 segments, each of which can be up to 32K in size. It then goes through and loads each segment that's supposed to be resident in memory (there are a few that aren't; their names start with "nr") into its proper location, before mapping it with the MMU. Once all segments are properly loaded, the loader jumps to the OS's entry point and control is handed over to the OS code itself!

The OS entry point is in SOURCE/STARTUP.TEXT, and it does several things in order to get the OS running. First, it maps some things like the jump table with the MMU, initializes some error handlers and exception vectors, and initializes the heap. Then it inits the memory manager, process scheduler, event/exception manager, and syscall table. After this, it's time to load all the SYSTEM.CD's into memory, after which PRAM is also initialized. Then we init the file system and mount the hard disk, followed by creating system processes for many of the items that we've initialized so far. Then we kill the "pseudo-outer process" that the loader was running in, officially handing process control over to the scheduler and the OS itself.

Now that the OS is in control, if you want to debug the OS to learn a lot more about what happens as it starts up, look for the DEBUG, DEBUG1, DEBUG2, and DEBUG3 flags near the top of SOURCE/DRIVERDEFS.TEXT and SOURCE/PASCALDEFS.TEXT. The regular old DEBUG one should always be TRUE (in DRIVERDEFS) or 1 (in PASCALDEFS) to allow LisaBug to work, but you can enable the others as well to get detailed debugging output as it boots. Make sure you always enable/disable each flag in both DRIVERDEFS and PASCALDEFS, or else things will break!

But even with these enabled, you still won't get a ton of info printing to the console by default. This is because there's also a debug "fence" that gets set by the line "SET_TRACE_FENCE(i,100);" in SOURCE/STARTUP.TEXT. This basically lets you control how much debug info different bits of the OS print out, but to see more info from everything, lower the 100 to something a bit smaller. You'll really start seeing a lot once you go below 50!

Now the processes that we've spawned can continue to configure the OS for operation, which includes things like loading INTRINSIC.LIB, reading intrinsic library segments into memory, and so on. Once all the initialization is done, the OS will automatically load the "application shell" executable file SYSTEM.SHELL to prepare for actually loading the Office System environment.

Remember, SYSTEM.SHELL is the Environments Window (APEW/SHELL.TEXT), so once this process gets control it'll search for shell.* operating environment files on the disk and will then display them, assuming you haven't set it to automatically boot from a default environment. Then you pick your environment (let's assume you pick the Office System (APDM) here), and SYSTEM.SHELL will tell the OS to spawn the shell.whatever_your_environment_was_called process.

Once control is handed over to this process, the load of the graphical shell (the Desktop Manager, APDM) can begin. This is all done in APDM/DESK.TEXT. First, it sets up some exception handlers, and then inits the PRAM Manager, QuickDraw, the Font Manager, the Window Manager, the Alert Manager, some objects, and the Storage Manager, which includes making heap zones for the Desktop Manager's use. This takes a while because it requires loading LIBPM, LIBQD, LIBFM, LIBWM, LIBAM, and LIBSM into memory, and you know this process is over when the "Welcome to LOS" dialog shows up on the screen. After this dialog pops up, the Desktop Manager loads the printer library (LIBPR) into RAM. Then it inits the field editor (LIBFE), scrollbar library (LIBSB), international library (LIBIN), and FilerComm (LIBFC). Now it spawns System.Print, the background printing process, and marks the completion of this task by removing the "Welcome to LOS" box from the screen. Now it's just a matter of drawing the icons on the desktop, mounting any additional drives besides the boot volume, and changing the cursor from the hourglass "busy cursor" to the "standard cursor". And that's it; you're now on the desktop and the Lisa is ready to use!

## Packing and PACKSEG
In order to conserve disk space, the Lisa actually uses a form of compression on some of the binaries on the disk. The compression algorithm is fairly simple and can be found in SOURCE/UNPACK.TEXT; it basically either loads code from the object file itself or from a common "packtable" containing bits of code commonly shared by lots of files and routines depending on the state of a series of flag bytes. But the compiler/linker doesn't generate packed code by default; Apple used a separate program called PACKSEG to pack each source file according to the common system packtable called SYSTEM.UNPACK.

The problem is that we don't have either the PACKSEG binary or the source code to it, so we can't pack any of our binaries. Fortunately, the OS loader is smart enough to auto-detect and load either a packed or an unpacked binary, so we don't strictly need to pack any of the code on the hard disk, but the issue is that many of our files won't fit on the LOS installer diskettes without being packed. So it's impossible to make new installer disks (or a LisaGuide diskette; it's also too big) until we find the original PACKSEG source code, find a binary that's compatible with the Workshop, or write our own.

# The Workshop Development Environment
All development work for the Lisa is done in an operating environment called the Workshop. This is an almost entirely text-based environment that gets installed alongside the regular Office System, with the only graphical components being the text editor, the serial transfer tool, and the Preferences tool.

The Workshop interface is very heavily inspired by the UCSD P-System. Menu options are displayed across the top of the screen, and you just type the first letter of a menu option in order to activate it. The FILE-MGR and SYSTEM-MGR are actually submenus, which you can return from by hitting Q for Quit. FILE-MGR's function should be pretty obvious, but SYSTEM-MGR is how you access the Preferences tool, set the clock, and view/kill running processes.

There are often more menu options than can fit on the screen, so just hit "?" to show any options that couldn't fit. For instance, the Linker and Assembler aren't visible on the main menu without hitting "?". Note that you can still execute hidden options by pressing the appropriate letter even if they're hidden.

The Lisa's filesystem is a bit weird, especially in its naming of disks and use of wildcards. In a Lisa 2/5, your hard disk is called -#11 and in a 2/10 it's called -#12. The micro diskette drive is called -lower and hard disks attached to expansion slots are in the format -#slotnum#portnum, like -#2#1 for a drive attached to the lower port on a parallel card installed in slot 2. You probably won't need these upcoming 3, but the serial ports are -rs232a and -rs232b and the printer is -printer.

By default, the Lisa will perform operations on the boot volume, so if you choose List from the FILE-MGR and just hit enter, it'll just list the contents of your boot hard disk without you having to specify -#11 or -#12. But if you wanted to list all the files on the micro diskette, you'd have to specify -lower-= using the Lisa's weird "=" wildcard. On the Lisa, "=" is the same as the "*" wildcard that you might be more familiar with. As another example, if you wanted to list all the files in the ALEX directory on your boot disk, you could specify ALEX/= in response to the list prompt (remember, we don't have to put -#11- at the beginning since the default drive is the boot drive).

To copy all the files in one directory to another, things are also a bit weird. You use the drive number (if necessary) and "=" wildcard for the source, but you use the "$" wildcard for the destination. So if I wanted to copy all files in the CATS directory on
the micro diskette to the MEOW directory on the hard disk, I'd choose C for Copy from the FILE-MGR, specify -lower-CATS/= for the source path, and MEOW/$ for the destination path. The Workshop is pretty weird!

To run a program/tool, just choose R for Run from the main menu and type the path to the desired object file.

If you instead want to run an EXEC script (like to build the OS, we'll talk about them later), you have to add a "<" character at the start of the path, like "<ALEX/MAKE/LIBOS.TEXT" to build LIBOS.

From the main menu, P runs the Pascal compiler, A runs the Assembler, and L runs the Linker.

## Workshop EXEC Scripts
EXEC is the Workshop's rather impressive scripting language that can be used to automate building applications (and pretty much any other operation in the Workshop). Any command you can type from the keyboard can be automated in an EXEC script.

In its simplest form, an exec script is nothing but a series of keystrokes saved in a text file that gets passed to the Workshop shell as if you typed it yourself. For instance, the following EXEC script copies one file to another:
```
$EXEC
FCALEX/SAMPLE.TEXT
CATS/SAMPLE.TEXT
YQ
$EXEC
```

But this is really confusing on its own, so we can insert comments using curly braces to make it easier to understand:
```
$EXEC
F{ile-mgr}C{opy}ALEX/SAMPLE.TEXT {Source file}
CATS/SAMPLE.TEXT {Destination file}
Y{es, overwrite if it already exists}Q{uit the file-mgr}
$ENDEXEC
```

Now it makes a lot more sense, right?

You can also pass parameters into EXEC scripts, which are referenced within the script using %0 for the first one, %1 for the second, and so on. This, combined with the $SUBMIT command that calls another EXEC script from within our current one, essentially allows us to create EXEC functions that we can call. For example, instead of doing the following each time we want to compile a file:
```
$EXEC
P{ascal compiler}CATS.TEXT  {Input source file}
                            {No listing file}
CATS.OBJ                    {Output object code}
$ENDEXEC
```

We can instead use the BUILD/COMP.TEXT script from the source release and simply do:
```
$EXEC
$SUBMIT BUILD/COMP(CATS.TEXT)
$ENDEXEC
```

You can also do IF statements, I/O operations, and much more, but that's beyond the scope of this simple explanation. All you need to know is that I automated the entire LOS build process for you using EXEC scripts, so you can just run a single script and build everything, or run an individual script to build a particular bit of LOS.

# The LOS Compilation Base Disk Image
The disk image I've provided in this repo is a good starting point for your LOS compilation journey, containing as many files as I can possibly include without violating Apple's license agreement. It's also of an appropriate size to hold all the code thanks to the SYSTEM.CD_Profile patch.

Here's a list of everything that I've provided in the base disk image, just to give you a general idea (and show that there's no source code on there):
| Item                                   | Explanation |
| -------------------------------------- | ----------- |
| Stock Copy of LOS 3.0 and Workshop 3.0 | Completely stock, although it is patched to allow large disk support. Note that the patch was done on the binary level, so it doesn't contain compiled source code. |
| Icons For Apps                         | My lovely icons for all the LOS applications! |
| ALEX/TRANSFER.TEXT                     | A script that you'll use in conjunction with a Python program to easily copy the source files into your disk image! |
| My Build Scripts                       | This is the big one; all the build scripts I wrote to actually get the source code to build. |
| APLC/CIRCLEBOX                         | A LisaDraw picture file required by LisaCalc that I grabbed off the LisaCalc install diskette. |
| APLC/FINDBOX                           | Another picture needed by LisaCalc from the install diskette. |
| APLC/FUNCHINTS                         | Yet another LisaCalc picture. |
| APLC/PRINTBOX                          | And another. |
| APLC/STATUSBOX                         | And one last one! |
| APLC/TABLES                            | A table file needed by LisaCalc and LisaGraph that I also grabbed off the LisaCalc install diskette. |
| LIBPL/PASMEM.TEXT                      | One of the LIBPL files I recreated from a disassembly of the original IOSPASLIB binary. |
| LIBPL/PWRII.TEXT                       | Another recreated LIBPL file. |
| LIBPL/PASLIB.TEXT                      | One last recreated LIBPL file. |
| LIBFP/STR2DEC.TEXT                     | And a recreated file from LIBFP. |
| ICONEDIT.OBJ                           | The icon editor, in case you want to make new icons. I found this on Bitsavers somewhere. |
| ALLCHARS.TEXT                          | A text file containing all the characters in the Lisa's charset, for easy copy-pasting while modifying all the source files! |
| APLW/SEARCH.LOTUS                      | A LisaWrite data file containing strings needed by the Find tool that I copied from the LisaWrite install diskette. |

# Getting the Code Onto Your Lisa
First, download the code from [here](https://info.computerhistory.org/apple-lisa-code)! After you've got it, we need to get it over to the Lisa. Thanks to some great ideas from Tom Stepleton and James MacPhail on LisaList2, I've written a cool little Python program that will handle all this for you. It's not quick, but at least it doesn't require any user intervention!

## Fixing Up The Source Files
There are three main problems with the source files as they're given to us by Apple.
- First, the .unix.txt extensions on all the files are pretty annoying. They just make all the filenames longer and get in the way.
- Second, the Lisa has no idea what a LF character is. It only recognizes CRs. So we have to strip all the LFs from the source files and replace them with CRs.
- And third, each source file has a weird garbage character on its very last line. Obviously we need to get rid of all of these too!

The serial transfer program handles all these automatically while sending the files to the Lisa, so there's no need to make any changes to the actual files on your machine, but I've included another Python script that will fix all these problems on the files in place, in case that makes you feel better. I like doing this just to get rid of all the stupid .unix.txt extensions and get nice .text extensions on the ends! Simply place the script (from the ```scripts``` directory) into your Lisa_Source directory, and run:
```
python3 process_source.py
```

A note: If you ever change one of the source files on a modern machine, your text editor might replace all the CRs with LFs again. 
If, for some reason, you want to make them all CRs again, run the following command (also in the ```scripts``` directory) after saving any changes to that file:

```
python3 singlefile_cr.py <path_to_file_you_changed>
```

Not that it really matters though since the serial transfer program already converts them on the fly!

## Applying Some Patches
Some of the source files need to be patched before they'll compile properly. You used to have to do this manually, but I've now written a Python script (once again in the ```scripts``` directory) that will do all 80-something patches for you! Just run:

```
python3 patch_files.py <path_to_lisa_source_code_directory>
```

If it doesn't say that it successfully applied all of the patches, then look back through all the output for any warnings that might've appeared. If you can't figure out why a particular patch wasn't applied, email me and we can figure it out! Note that your copy of the code will NOT compile and work properly unless all of these patches are completed successfully.

## File-Copying Rules
As a general rule, we ignore the directory structure of the source release when structuring the files on the Lisa. The source release often has extra directory levels or directories with different names from what they should be on the Lisa. So we just use the filenames themselves for guidance on what to name the files, interpreting the "-" characters (and occasional "." characters) as slashes in the pathname. So for instance, we'd save the file APPS/APBG/apbg-BG.TEXT as APBG/BG.TEXT on the Lisa, and we'd save LISA_OS/OS/SOURCE-2PORTCARD.TEXT as SOURCE/2PORTCARD.TEXT on the Lisa. You can probably see that I also like saving all the files in all caps, but the Lisa FS isn't case-sensitive so it really doesn't matter.

Once again, my serial transfer script will handle all the file-renaming for you, so don't worry about any of these renaming conventions unless you're creating files manually or something.

There's also a chance that I might've renamed a file or two during the copying process beyond what I mentioned above (I have a vague memory of correcting a typo in a filename or something), but I can't remember for sure. If you've used the script to copy everything over, but the Workshop still complains about a missing file, let me know and I'll fix this ASAP!

## What You Need To Copy Over
- Everything in the APPS folder.
- LISA_OS/BUILD/BUILD-ASSEMB.TEXT, LISA_OS/BUILD/BUILD-COMP.TEXT, and LISA_OS/BUILD/BUILD-INSTALL.TEXT.
- LISA_OS/GUIDE_APIM if you care about LisaGuide.
- Everything in LISA_OS/LIBS.
- Everything in LISA_OS/OS.
- The two files in LISA_OS/TKIN.
- LISA_OS/TKALERT.TEXT.

## What You Don't
- The DICT directory. We don't have the LisaWrite American Dictionary to begin with, so why bother?
- LISA_OS/APIN. We already have APIN from inside the APPS directory.
- Any scripts in LISA_OS/BUILD aside from the three I mentioned above.
- LISA_OS/FONTS. We don't care about rebuilding the font library, so no need to copy over the raw font files.
- LISA_OS/LIBHW. This is basically just a duplicate of LISA_OS/LIBS/LIBHW that we already copied over.
- LISA_OS/Linkmaps 3.0 and LISA_OS/Linkmaps and Misc. 3.0. These are literally just linkmaps, so no reason to put them on the Lisa.
- Anything in LISA_OS/OS exec files. We've remade all these from scratch.
- Anything in Lisa_Toolkit. This is a combination of duplicate files from LIBTK and the ToolKit University disks, which contain no source code.

Don't worry, the serial transfer script will automatically copy over the things you need and exclude the things you don't, so this info is also just for reference!

So now let's actually talk about the transfer script! The program is called ```lisa_serial_transfer.py``` and you can find it in the ```scripts``` directory. It works by taking control of the Workshop's console over serial, and then uses a special Workshop utility I wrote to transfer characters straight into a text file, repeating this for each file you want to send. 

The COPY program that comes with the Workshop is almost perfect for this as-is, except that it uses the file-reading code from LIBPL, which annoyingly strips the high bit from all characters if it detects that they're being received over serial. So I had to write my own utility that uses the OS file-management routines instead and keeps that high bit intact. If you're curious about it, you can find the source code in ALEX/RECEIVE.TEXT, and the binary is ALEX/RECEIVE.OBJ. But I'd advise against running the binary manually unless you fully understand how it works; you'll probably lock up your Lisa and have to hit the reset button!

Before you try to run the transfer tool, you'll need to install the Pyserial library. So, assuming you've got Python installed, you can do that by typing:

```pip3 install pyserial```

Now connect a serial cable between Serial B on your Lisa and your modern computer (you'll probably need a USB to serial adapter here). You can run the serial transfer tool by doing:

```python3 lisa_serial_transfer.py <serial_port> <directory_or_file_to_send>```

Notice that you can specify either a single file or an entire directory to send to the Lisa. For getting all the code over to the Lisa for the first time, you'll want to specify a directory, probably ```Lisa_Source/``` unless you've renamed things in your copy of the code. But later on once you're making changes to the code, you can also just specify a single file.

Before the transfer starts, it'll ask you to run the EXEC file ```ALEX/TRANSFER.TEXT``` on your Lisa to configure the serial port and put the Lisa into remote console mode. So go ahead and hit R for Run from the main Workshop screen, and then type:
```<ALEX/TRANSFER.TEXT```.

Now hit return on your modern computer once the Lisa's screen goes blank, and the transfer should start!

As the file(s) are transferred, you'll see the text that's being transferred printed live to the console on your modern computer, as well as a status bar at the top of the screen showing you the progress of the current file, the entire transfer if you're doing multiple files, and ETAs for everything:

<img width="1613" height="1050" alt="SCR-20250724-nhyr" src="https://github.com/user-attachments/assets/4ea002ac-073b-4b32-b473-dc5b912d260b" />

The program will also create a log file called log.txt where it will print some info about each file as it gets transferred, including any errors that occur (the Lisa not responding properly to a command).

You'll also get occasional progress messages on the Lisa, but they're not super frequent to avoid slowing things down. You'll see a message whenever the Lisa begins receiving a new file, messages every 100 lines that the Lisa processes, and a message at the end of the file letting you know how many lines it was.

Note that the Lisa is pretty slow to process data coming to it over serial, so there's a lot of starting and stopping during the transfer process. We transfer about 8K of data, the Lisa deasserts DSR, and then we have to wait for it to process all the data before we can send more. So don't worry if the output freezes for a minute or two at a time while the "WAITING FOR LISA" message blinks at the top of the screen; that's totally normal and expected! If the freeze is concerningly long, the program will report an error.

Make sure that your USB to serial adapter supports DSR/DTR hardware handshaking, or else the program won't work! On macOS, some USB to serial adapters will show up as two different device entries, and only one of them supports hardware handshaking (normally the one with the longer name), so try both if you encounter this.

# Fixes to Source Files
Now that I've written software to automate all of these fixes, the information below probably won't be interesting to very many people, but I figured I'd leave it here for the sake of documenting everything that I had to change to get LOS to compile. So if you're curious, then read on, but otherwise, feel free to skip this!

The Character-Related Fixes section describes all of the fixes I had to do thanks to the Lisa's special characters getting corrupted during serial transfers. The characters in the Lisa's extended character set have their high bit set, and I originally couldn't figure out how to prevent the Lisa from stripping the high bit during serial transfers, leading to corrupted special characters. But I've now written a custom serial receiver program (```ALEX-RECEIVE.TEXT```) that ```lisa_serial_transfer.py``` uses to copy everything over to your Lisa while preserving the high bit. So it's not a problem anymore!

The Actual Code Changes section describes all the patches that I had to make to the source code itself in order to get it to build. So things like correcting typos, making new files, patching out the LisaWrite spellchecker, and so on. These are now all automated by the ```patch_files.py``` script that you run before copying things over to your Lisa.

## Character-Related Fixes
- In APHP/HP.TEXT, find "divide sign" and replace the character in the quotes with the division sign (÷). Now make sure the character on the next line is a forward slash and replace the character on the line below that with the Lisa "diamond" character. Also find "A-A" and delete everything following it on that line. Then retype the rest of the line as " A.A A–A A'A".
- In APHP/T12ALERT.TEXT, there are several things to change under the MenuBuzz heading, so just make it look like the picture below. <img width="152" alt="T12ALERT" src="https://github.com/user-attachments/assets/ac7363c0-710e-4185-9098-667fc4b5119c" />

- In APLP/T8ALERT.TEXT, find "A-A" and then delete the rest of the line after that text. Now retype the rest of the line as " A'A A-A".
- In APLL/DBCONVERT.TEXT, search for "sterling=" and replace the bad character in the quotes with the British pound symbol (option-3). Do the same with the Yen symbol on the next line, and a non-breaking space on the next line after that. Type a non-breaking space by hitting option-spacebar.
- In APLL/T5LM.TEXT, search for "A-A" and delete everything that follows it on that line. Then retype the rest of the line as " A-A A'A A.A".
- In APLT/CONVERT.TEXT, make the arrays look like this picture: <img width="749" alt="APLT-CONVERT" src="https://github.com/user-attachments/assets/fe8b5661-34ea-4ffd-95e4-ec08fe7dc620" />
- In APLT/INIT.TEXT, search for "AlphaNum:=" and make the array look like this: <img width="485" alt="APLT-INIT" src="https://github.com/user-attachments/assets/5b0af66f-f14a-4b0a-ba7c-a2bc502afd78" />
- In APLW/T1MENUS.TEXT, search for "6". Then replace the last character on the "Format" line below it with the "paragraph" symbol (option-7). Do the same with the last character on the "Single Space", "1-1/2 Space", "Double Space", and "Triple Space" lines a little further down.
- In APLW/T1ALERT.TEXT, search for "2 stop alert". Then go 4 lines down and replace the character between "on" and "off" with a "-". Now search for "8 stop alert", go to the next line, and delete everything after the word "of". Replace it with ""^1."" (include the inner set of quotes in what you type). Now search for "10 caution cancel alert", go to the next line, and surround the "^2" with quotes just like we did with the "^1.". Now search for "A-A" and then delete the rest of the line after that text. Now retype the rest of the line as " A-A A.A A'A". Now scroll down a couple lines to "14 stop alert" and do the same thing where we surround the "^1." on the next line with quotes. Next, search for "58 note alert", "60 note alert", and "63 ask alert" and do the same thing for the "^1" entries on the following lines. Now search for "71 wait alert" and replace the first character in the "copyright" line 2 lines below it with the copyright symbol. Scroll down a few more lines to "74 wait alert" and replace the character 2 lines down between "Apple" and "period" with a "-". Do the same with "76 wait alert" and "78 wait alert". Now scroll down to "81 note alert" and do the thing where we surround "^1" with quotes. Then go to "83 note alert" and surround "Put In Dictionary" with quotes. Then scroll to "85 wait alert" and add the "-" between "Apple" and "period". Now find "96 stop medium+alert" and replace the character in between "Chapter" and "2" a couple lines down with a space. Then search for "first part", go up 2 lines to "Set Aside", and replace the last character on this line with a double quote ("). Scroll down a little to "913", go to the next line, and replace its entire contents, with another double quote. Now scroll down a bit more to "Set Aside Clipboard" and replace the 2 characters around "Clipboard" with quotes. Scroll down some more to the Format menu and add paragraph (option-7) characters in the same places that we did in APLW/T1MENUS.TEXT. Also change the character between both instances of "1" and "1/2 Space" to a "-". Now scroll down a bit more to the line "Preview Pages" and change the next line to read "Don't Preview Pages". And then search for "Set Decimal" and surround the "." on the first line and the "," on the second line with quotes. And we're FINALLY done with this horrible file!!!
- In APLD/T4ALERT_MENUS.TEXT, find "A'A" and delete everything following that text on the line. Then retype the rest of the line as " A-A A-A A'A A.A".
- In APLC/T3ALERT.TEXT, find "A.A" and delete everything following that on that line. Retype the rest of the line as " A-A A'A"
- In APLC/LCFILER.TEXT, search for "if (str4" and replace the bad character in the array with the Lisa "bullet point" character (option-8).
- In APLC/APPDIBOX.TEXT, find the 3 instances of "number = ". Replace the value in quotes in the first instance with a "¬", the second with the degree symbol, and the third with a "ƒ". Then search for "textIndex]) <>" and replace the character in quotes with another "ƒ".
- In APBG/T2ALERT.TEXT, search for "A.A" and delete everything following it on that line. Then retype the rest of the line as " A-A A'A".
- In LIBPR/DWBTN.TEXT, search for "10/12+Add'l" and then replace the messed-up word "Characters" right after it with "Chåräçtérs".
- In LIBPR/PRALERT.TEXT, search for "Change Printer" and replace the bad character after it with the "..." character (option-;).
- In LIBQP/UVT100.TEXT, replace the bad character on the line "IF outstr[a] = '#' THEN BEGIN ch :=" with the UK pound sign (option-3). Do the same with the bad character on the line "IF (ch = '#') AND SELF.ukPound THEN ch :=" and the bad character on the line right below the one that says "ELSE IF (ach = '#') AND SELF.ukPound THEN".
- In LIBTK/UOBJECT4.TEXT, replace the bad character on the line "Byte2Char := '" with the "bullet point" character (option-8). Do the same for the 4 bad characters in the "write" statement on line 2152 and the 1 bad character on each of the 2 lines following the write statement.

## Actual Code Changes
- In APHP/HP.TEXT, find the 3 occurrences of "{t12}" and replace with "{t100}".
- In APCL/CLOCK.TEXT, find "{t13}" and replace with "{t101}".
- In APLL/INITFEX.TEXT, find the two occurrences of "{t5}" and replace with "{t103}".
- In APLT/INIT.TEXT, search for the two instances of "{t10}" and replace with "{t104}".
- In APLW/UNITLOTUS.TEXT, we need to disable the spellchecker. So first comment out the USES statement lines containing "$U ApLW/UnitSpell.obj", "$U aplw/sp/spelling.obj", and "$U aplw/sp/verify.obj". And then search for and comment out the lines containing "UndoPutDict", "UndoRmvDict", "DoSpellImid", "EndGuessDbox", "NQMore", "ord (HMReturn)", and "SetHzSpell". Right after the "NQMore" line, make a new line with the contents "fMoreToQ := FALSE;". And right after the "SetHzSpell" line, make a new line with the contents "theDBox.isOpen := FALSE;". Now find the line "HMReturn := SpTerminate(closeFile);" and replace it with "HMReturn := ok;". Next, go to the top of the file, and make a new heading called "TYPE" right above the VAR heading. Then, on the next line, type "TSpReturn = (ok, notInitialized, illegalString, masterError, unableToLoad, userMemoryFull, wordExists, notFound, limitExceeded);". Then, under the VAR heading, add the lines "fTstSpell: TF;", "fTstHeap: TF;", and "fMoreToQ: TF;". And completely unrelated to the spellchecker, find the 2 instances of "{t1}" and replace with "{t105}".
- In APLW/TESTBOX.TEXT, we also need to do stuff to disable the spellchecker. First comment out the USES statement lines containing "$U ApLW/UnitSpell.obj", "$U aplw/sp/spelling.obj", and "$U aplw/sp/verify.obj". Then find and comment out the lines containing "fTstSpell", "fTstHeap", "ord (HMReturn)", and "spstatus". And similar to UNITLOTUS, find the line "HMReturn := SpTerminate(cleanUp);" and replace it with "HMReturn := ok;". And then do the same thing that we did for UNITLOTUS where we made a new TYPE heading and declared that TSpReturn type underneath it.
- In APLW/SP/VERIFY.TEXT, find the instance of "{t1}" and replace with "{t105}".
- In APLW/UNITSCRAP.TEXT, find the 3 instances of "{t1}" and replace with "{t105}".
- In APLW/UNITSPELL.TEXT, find the 3 instances of "{t1}" and replace with "{t105}".
- In APLW/UNITSRCH.TEXT, find the instance of "{t1}" and replace with "{t105}".
- In APLC/LCFILER.TEXT, replace the occurrence of "{t2}" with "{t108}" and the occurrence of "{t3}" with "{t107}".
- In APLC/MM/LEX.TEXT, replace the occurrence of "{t2}" with "{t108}" and the occurrence of "{t3}" with "{t107}".
- In APLC/APPDIBOX.TEXT, replace the 5 instances of "{t3}" with "{t107}". Then find "inPutGrahics" and replace it with "inPutGraphics".
- In APPW/BTNREAD.TEXT, replace the instance of "{t11}" with "{t109}". Also replace "appw/btnfile.text" with "appw/T11buttons.text".
- In APPW/CONFIG.TEXT, replace the 6 instances of "{t11}" with "{t109}".
- In APPW/PREFMAIN.TEXT, replace the 2 instances of "{t11}" with "{t109}".
- In LIBDB/LMSCAN.TEXT, add the lines "{$SETC fSymOk := FALSE }" and "{$SETC fTRACE := FALSE }" right below the "{$SETC OSBUILT := TRUE }" line. Also search for "PROCEDURE diffWAdDelete" and replace it with "PROCEDURE diffWADelete".
- In LIBFP/NEWFPLIB.TEXT, delete the line that says "{$I libFP/str2dec }" and replace it with "procedure Str2Dec; external;".
- In LIBHW/KEYBOARD.TEXT, replace "uses {$U hwint.obj} LibHW/hwint;" with "uses {$U libhw/hwint.obj} libhw;".
- In LIBOS/SYSCALL.TEXT, replace the entire contents of the file with the contents of SOURCE/SYSCALL.TEXT.
- In LIBOS/PSYSCALL.TEXT, change the USES statement from "(*$U object/syscall.obj *)" to "(*$U libos/syscall.obj *)".
- In LIBPL/TFLDERCALL.TEXT, change the line ".include        paslibequs.text" to ".include        libpl/paslibequs.text".
- In LIBQP/UBAUDRATE.TEXT, change the USES statement from "{$U -newdisk-QP/Hardware} Hardware;" to "{$U LIBQP/QP/Hardware} Hardware;".
- In LIBTK/UTEXT.TEXT, change the USES statement reading "{$U UABC}" to "{$U libtk/UABC}".
- In TKIN/SOURCE.TEXT, change the USES statements reading "{$U Tkin/Globals         }" and "{$U Tkin/Cat         }" to "{$U APDM/Globals         }" and "{$U APDM/Cat         }". 
- In TKIN/ENTRY.TEXT, change the USES statement reading "{$U TKIN/Globals}" to "{$U APDM/Globals}".
- In SOURCE/PROFILE.TEXT, find the line "if (discsize <= 9728) or (discsize > 30000)" and replace the 30000 with some really big number (I used 500000).
- In SOURCE/DRIVERDEFS.TEXT, find the "$SETC DEBUG1" and "$SETC TWIGGYBUILD" statements. Change them both from TRUE to FALSE.
- In SOURCE/PASCALDEFS.TEXT, find the "DEBUG1          .EQU    1" and "TWIGGYBUILD     .EQU    1" statements. Change the 1's after the .EQU's to 0's.
- Copy (don't move) SOURCE/PASMATH.TEXT to LIBPL/PASMATH.TEXT.
- In LIBPL/PASMATH.TEXT (the new file you just created), add the line ".include libpl/pwrii.text" right below the ".DEF    %I_MUL4,%I_DIV4,%I_MOD4" line.
- Open SOURCE/OSINTPASLIB.TEXT, and copy the PASMOVE section (everything starting at the comment "; File: PASMOVE.TEXT" and ending right above the comment "; File: PASRANGE.TEXT"). Make a new file in the Editor (File->Tear off Stationery, then hit enter) and paste this text into it. Then save the file as LIBPL/PASMOVE.TEXT. Repeat this process for the PASMISC and PASRANGE sections of OSINTPASLIB, saving them as LIBPL/PASMISC.TEXT and LIBPL/PASRANGE.TEXT.
- In LIBPL/PASMISC.TEXT (the new file you just created), add the line ".include libpl/paslibdefs.text" right below the line ".PROC   %%%MISC" that appears near the top of the file. Also change the line ".ref    gotoxy" to ".ref    %_FGOTOXY". And change the line "jsr     gotoxy" to "jsr     %_FGOTOXY".
- In APIM/IMEVTLOOP.TEXT, change the uses statement that reads "{$U apim/tfilercomm }tfilercomm" to "{$U FilerComm }  FilerComm".
- In APIM/IMFOLDERS.TEXT, find the instance of ObjectKind and replace it with ObjectAKind.
- In APIM/IMINTERP.TEXT, find the 3 instances of ObjectKind and replace them with ObjectAKind. Then find the uses statement that reads "{$U fld.obj      }  FieldEdit" and make a new line below it that reads "{$U FilerComm } FilerComm,".
- In APIM/IMPATMAT.TEXT, find the uses statement that reads "{$U fld.obj      }  FieldEdit" and make a new line below it that reads "{$U FilerComm } FilerComm,".
- In APIM/IMSCRIPT.TEXT, find the uses statement that reads "{$U fld.obj      }  FieldEdit" and make a new line below it that reads "{$U FilerComm } FilerComm,".
- In APIM/IMSIM.TEXT, find the uses statement that reads "{$U fld.obj      }  FieldEdit" and make a new line below it that reads "{$U FilerComm } FilerComm,".
- In APIM/TCATALOG.TEXT, comment out the lines nilKind = 0, fileKind = 1, everything from folderKind = 3 to computerKind = 10, folderPad = 16, clockKind = 19, and everything from toolKind = 24 to disk2Kind = 27. Then change drawerKind to actualDrawerKind, the 2 occurrances of deskKind to actualDeskKind, the 2 occurrances of profileKind to actualProfileKind, and the occurrance of lastKind with actualLastKind. Right after the "{$U AlertMgr  } AlertMgr" line, make a new line that says "{$U FilerComm } FilerComm,".
- In APIM/TFDOCCTRL.TEXT, change the uses statement that reads "{$U apim/tfilercomm }tfilercomm" to "{$U FilerComm }  FilerComm". Also change the 2 occurrances of profileKind to actualProfileKind.
- In APIM/TFILER.TEXT, change the uses statement that reads "{$U Apim/tfilercomm }  Tfilercomm" to "{$U FilerComm }  FilerComm". Then change the 4 occurrances of drawerKind to actualDrawerKind, the 4 occurrances of deskKind to actualDeskKind, the 8 occurrances of profileKind to actualProfileKind, and the 4 occurrances of lastKind to actualLastKind. Comment out the lines "iconWidth    = 48;" and "iconHt       = 32;" too. Now go through and change all 23 instances of ObjectKind to ObjectAKind, all 32 instances of iconData to aIconData, all 34 instances of iconMask to aIconMask, and the 3 instances of iconBoxes to aIconBoxes.
- In APIM/TFILER2.TEXT, change the occurrance of deskKind to actualDeskKind, the 3 occurrances of profileKind to actualProfileKind, the 7 occurrances of ObjectKind to ObjectAKind, the 1 occurrance of iconData to aIconData, and the 2 occurrances of iconBoxes to aIconBoxes.
- In APIM/TFILERINT.TEXT, change the occurrance of drawerKind to actualDrawerKind, the 2 occurrances of deskKind to actualDeskKind, the occurrance of profileKind to actualProfileKind, and the 4 occurrances of ObjectKind to ObjectAKind.

# Why did we change all the tool numbers?
You might've noticed that we went through all the source files for the Lisa apps and changed their tool numbers from the defaults to things in the 100+ range. This was simply done so that you can have copies of the original LOS tools and your newly-built tools installed on your Lisa simultaneously. You could leave the tool numbers untouched if you wanted to, but you'd have to change the build scripts to account for this, and of course this would prevent you from installing the original LOS tools alongside your new ones.

# Tool Icons
If you've seen my VCF presentation, you'll know that I've drawn absolutely "lovely" icons for all the newly-built LOS apps. I've included these in the disk image so that they'll show up automatically when you build each tool, but you can make your own if you'd like. Just use the icon editor (ICONEDIT) in the Workshop to draw a new icon and that's all there is to it! If you want to delete my tool icons, they're saved in the root of the disk as {Txxx}icon where xxx is the tool number.

# How to Build the OS
Before we build things, there's one final thing to do if you're doing all this in LisaEm instead of on actual hardware.

## Patching LisaEm for Our Custom OS
If you're using LisaEm, the mouse will stop working the moment you compile the core OS itself and replace the original SYSTEM.OS with your new one. This is because LisaEm sets its mouse scaling depending on which OS is loaded, and it detects the OS based on a couple random longwords picked out of the SYSTEM.OS file. Our SYSTEM.OS file isn't quite the same as the original, so the longwords that it grabs are different, and it detects our OS as an unknown OS and thus doesn't set the mouse scaling properly. And we can't hard-code a new entry for our version of the OS because making any changes to the source is likely to change these longwords. So the solution is just to force LisaEm to always use the LOS 3.0 mouse scaling regardless of what OS it detects. To accomplish this, download and compile the LisaEm source code from [here](https://github.com/arcanebyte/lisaem/) but replace the file lisaem-master/src/lisa/motherboard/glue.c with the glue.c provided in this repo.

## Building Things
To build everything, run the ALEX/MAKE/ALL_NOFLOP EXEC script. Remember, to run an EXEC script, you hit R for Run and then type the name of the script prefixed with a "<". So here it's:
```
<ALEX/MAKE/ALL_NOFLOP
```

Make sure to build everything with this command before going back and building certain components on their own; this ensures that all dependencies for every piece of the OS are built and you won't have to worry about anything being missing.

The NOFLOP suffix runs the EXEC script that builds everything but doesn't try to make installer or LisaGuide diskettes at the end. Remember, we can't do those yet because we don't have PACKSEG!

If you want to build individual bits of the codebase, that's entirely possible too! Just list the contents of ALEX/MAKE/ to see all the scripts you can run, but here's a quick summary. If it's not listed here, then you probably shouldn't run it:
| Script Name | Purpose |
| ----------- | ------- |
| ALL         | Builds everything and makes a new set of installer and LisaGuide diskettes. Don't use this right now since we don't have PACKSEG! |
| ALL_NOFLOP  | Builds everything but doesn't make installer or LisaGuide diskettes. Run this one if you want to make everything! | 
| AP**        | Builds the app specified by ** (like APLP for instance), and performs the appropriate installation procedure for it. |
| APIM        | Technically one of the AP** scripts, but I want to mention it separately because this is LisaGuide. It'll ask you if you want to make a LisaGuide diskette after building LisaGuide itself; answer no for now since we don't have PACKSEG! |
| APIMDISK    | Makes a new LisaGuide diskette. Make sure you've built APIM first, and don't run this at all right now since we don't have PACKSEG! |
| APPS        | Builds and installs all the apps, other than APIN (the installer) and APIM (LisaGuide). |
| BTDRIVERS   | Builds all the SYSTEM.BT_* bootloaders and places them in the proper location on the hard disk. Does NOT overwrite the boot blocks! |
| BT*****    | Builds the individual SYSTEM.BT_ file specified by ***** and places it in the proper location. Does NOT overwrite the boot blocks! |
| CDDRIVERS   | Builds and installs all the SYSTEM.CD_* configurable driver files. Make sure to reboot after this! |
| CD*****     | Builds and installs the individual SYSTEM.CD_* file specified by *****. Make sure to reboot after this! |
| PREDRIVER   | If you're about to run a CD***** and you've never run PREDRIVER, CDDRIVERS, FULLOS, ALL, or ALL_NOFLOP before, then run this. |
| DISKS       | Makes new copies of all the LOS install disks from our newly-built files. Make sure you've built everything else first, and don't use this at all right now since we don't have PACKSEG! |
| DISKn       | Makes a new copy of LOS install disk n from our newly-built files. Make sure you've built everything else first, and don't use this at all right now since we don't have PACKSEG! |
| FULLOS      | Builds and installs the entirety of the OS itself, including SYSTEM.OS and the SYSTEM.CD_* and SYSTEM.BT_* files. Does NOT overwrite the boot blocks with the new BT files. Make sure to reboot after this! |
| INSTALLER   | Builds the LOS installer application and then optionally makes a set of new LOS install disks. Say no to this option for now since we don't have PACKSEG! |
| LIB**       | Builds the library specified by **, like LIBAM for instance. If the library you're building is part of SYS1LIB or SYS2LIB, you must re-link that library file and reboot after this in order to actually install it! |
| LIBS        | Builds and installs all of the system libraries. Make sure to reboot after this! |
| SYSTEMOS    | Builds and installs a new copy of SYSTEM.OS. Make sure to reboot after this! |
| TKIN        | Builds INSTALLTOOL and puts it in the PROGS directory. |
| TKALERT     | Builds the phrase file generator (ALERT) and places it in the PROGS directory as ALERTGEN_NEW1984.OBJ. |

To relink SYS1LIB or SYS2LIB, run ```ALEX/LINK/SYS1LIB``` or ```ALEX/LINK/SYS2LIB```.

There are tons of scripts in the ALEX/ASM, ALEX/COMP, and ALEX/LINK directories that handle the individual steps of assembling, compiling, and linking each portion of the source code. So if you only need to perform one of these operations instead of doing a full MAKE that runs all three, you can just run one of these scripts individually.

# Cool Programs
Alongside all the expected source code, the source release also included several little text-based Workshop utility and demo applications. As you build all the source code, each of these apps will build and install into the PROGS directory.

## Things That Work (And are in the PROGS directory)
| Program              | Purpose |
| -------------------- | ------- |
| ALERTGEN_OLD1982.OBJ | An old copy of the ALERT program from 1982. Source is in LIBAM. |
| ALERTGEN_NEW1984.OBJ | The most up-to-date copy of the ALERT program from 1984. Source is in TKALERT. |
| BLESS.OBJ            | A program that will bless a disk. Source is in LIBOS. |
| CDCHAR.OBJ           | Generates a "configurable driver characteristics file" for a set of LOS drivers. Not sure what this is for exactly. Source is in SOURCE. |
| CDCONFIG.OBJ         | Allows you to add and remove configurable driver entries from the SYSTEM.cdd configurable driver directory. Source is in SOURCE. |
| COPYMASTER.OBJ       | Does a block-for-block copy of one disk to another and makes the destination bootable. Source is in LIBOS. |
| DEVCONTROL.OBJ       | Allows you to directly control a device by sending commands to its driver. Source is in SOURCE. |
| GDATALIST.OBJ        | Provides info about the system global data area. Source is in SOURCE. |
| KEYBOARD.OBJ         | Tells you the layout of your keyboard and lets you change it. Source is in LIBHW. |
| LIBMASTER.OBJ        | Creates a new FONT.LIB system font file from a set of individual font files. Source is in LIBFM. |
| MAKEHEUR.OBJ         | Seems to make a new FONT.HEUR file from a FONT.LIB file, but I can't get it to work. Source is in LIBFM. |
| NWSHELL.OBJ          | An alternate Monitor-like shell for the Lisa. To run, rename to shell.UltraDOS, reboot, and choose it from the Environments Window. Source is in SOURCE. |
| PEPSITESTS.OBJ       | A set of hardware demos for the Pepsi (Lisa 2/10) system. Includes a theremin! Source is in LIBHW. |
| STUNTS.OBJ           | Similar to PEPSITESTS, but for the 2/5. Source is in LIBHW. |
## Things That Don't Work
| Program            | Purpose |
| ------------------ | ------- |
| LIBPR/SUPER.TEXT   | A printer demo that seems to be written for older versions of the system libraries. Could probably be updated to work with the latest Lisa system (which would be really cool)! |
| APPW/PMCONFIG.TEXT | A text-based version of the Preferences tool. Not only uses older versions of libraries, but also relies on an older Lisa driver model, so would be difficult to port to the latest Lisa system. |

# Fun Stuff I Learned
- Shift-option-numpad 0 will immediately dim the screen to black. So if you're up to no good on your Lisa, you can immediately hide your suspicious activities!
- Shift-option-numpad 4 prints the screen to whatever printer you have connected. This is really, really cool!
- Shift-option-numpad 7 will save a screenshot as a raw bitmap to the micro diskette. So make sure you have a diskette inserted, or else it won't work!
- Apple-option-m activates the Lisa Monkey, which is basically the same thing as the [Mac Monkey](https://folklore.org/Monkey_Lives.html?sort=date). You can single-step the Monkey with Apple-option-s and can kill the Monkey at any time with Apple-option-q. Note that you'll need to set the wmMonkey flag in LIBWM/EVENTS.TEXT to TRUE, rebuild LIBWM, and then relink SYS1LIB in order to include the Monkey in the compiled Window Manager.
- Believe it or not, none of the original Lisa apps actually use the ToolKit! They all interface with the system libraries directly without using the ToolKit API, likely because the ToolKit wasn't finished until well into application development.
- The Desktop Manager (APDM) has two flags in APDM/GLOBALS.TEXT that are pretty cool.
  - One is network, which offers a (very limited) peek into the network-enabled future of LOS if set to TRUE. It just shows a "file cabinet" icon on the desktop that I guess was supposed to be an inbox/outbox thing, but you can't copy files into this folder. And setting this flag to true also corrupts the filesystem and makes a new copy of the Clock on the desktop each time you reboot for some reason, so I'd advise against using it other than just as a curiosity!
  - The other is flrJrnl, which enables a cool journaling mode in the shell. If this is enabled, the OS will appear to hang on boot right around the "Welcome to LOS" screen, but just press Apple-Enter to go to the alt console where you can provide user input. It'll ask you for a recording or playback journal filename. So what you can do here is record a set of keyboard and mouse inputs to a journal file, reboot the system, and then load that file back in and play back your actions. It's pretty cool!
- Pretty much every app, library, and the OS itself has a debug flag that can be enabled to print tons of debugging info to the alt console (which you can access by pressing Apple-Enter). The debugging features are actually interactive for some of the graphical apps, where enabling the debugging flag might add a Debug menu to the menu bar.
- Contrary to what some people have said, the Lisa does NOT print tons of WRITELNs to the alt console by default. Pretty much all of the WRITELNs are compiled out by default, so this is not the reason for LOS being so slow. In fact, just enabling the WRITELNs for the OS alone takes the boot time from about 1 minute to about 45 minutes!
- There's a procedure called Muzak in SOURCE/SFILEIO2.TEXT that runs whenever the OS mounts an LOS 3.0 filesystem. But it'll only be compiled in if the DEBUG1 level of OS debugging is enabled, and even then it'll just play a single beep when the FS gets mounted. If you look at the Muzak procedure though, you'll see some other music notes that are commented out, so you can uncomment them all to have it play an entire "song" (although it really doesn't sound like music) whenever it mounts a disk. Pretty cool!

# Potential Additions/Improvements
Although I'd love to mess with some of these myself, I think I'll probably leave them to other people for the time being. I've spent enough time with LOS lately, and I need to work on some other things right now!
- Large Disk Support - Done!
- New Implementation of PACKSEG - VERY HIGH PRIORITY!!!!
- Y1.995K Patch - Allow dates later than 1995.
- MacWorks Screen Mod Compatibility - Allow LOS to work with the "square pixels" screen modification.
- XLerator Support - Start by getting LOS to boot with the 16MHz XLerator installed, then get LOS to actually turn the XLerator on!
- Twiggy Support - We've got the bootloader, we're just missing one source file from the configurable driver.
- Additional Device Drivers - Add support for things like SCSI, the Apple Color Plotter, the LisaDAC, and so on.

# All The Files That Form an LOS/Workshop Installation
We've talked about a bunch of files throughout this document, so let's conclude things by bringing them all together and making a list of all the files that you'll find on a standard LOS/Workshop hard disk. We've already talked about most of these, but a few are new.
| File                           | Purpose |
| ------------------------------ | ------- |
| CIBTNDATA                      | Button location and attributes data for the C-Itoh (ImageWriter) printer dialog box. Created by LIBPR/PRBTN.OBJ. |
| CNBTNDATA                      | Button location and attributes data for the Canon (Inkjet) printer dialog box. Created by LIBPR/PRBTN.OBJ. |
| DWBTNDATA                      | Button location and attributes data for the daisy wheel printer dialog box. Created by LIBPR/PRBTN.OBJ. |
| FONT.HEUR                      | Font heuristics file. Tells the system what fonts are installed and info about them. Created by PROGS/MAKEHEUR.OBJ, but I can't get this program to work right. |
| FONT.LIB                       | Font library file. Contains all of the system fonts. Created by PROGS/LIBMASTER.OBJ. |
| INTRINSIC.LIB                  | Intrinsic library directory file. Contains information about all intrinsic libraries on the Lisa. Created and updated by IUMANAGER.OBJ. |
| IOSFPLIB.OBJ                   | Floating point intrinsic library. |
| IOSPASLIB.OBJ                  | Pascal runtime intrinsic library. |
| LCORBGLIB.OBJ                  | LisaCalc and BusinessGraphics (LisaGraph) shared intrinsic library. |
| OBJIOLIB.OBJ                   | Object file I/O library; we don't have source code for this, I think it's part of the Workshop. |
| OEMSYSCALL.OBJ                 | We don't have source code for this either; seems to just be stuff used by the Workshop Filer. |
| PARBTNDATA                     | Button location and attributes data for the main printer dialog box. Created by LIBPR/PRBTN.OBJ. |
| PASLIBCALL.OBJ                 | Some random Pascal runtime library calls; just the compiled version of LIBPL/PASLIBCALL. |
| PRLIB.OBJ                      | Printer intrinsic library. |
| QPLIB.OBJ                      | QuickPort intrinsic library. |
| SCRAP1.FIGURES                 | Scrap (clipboard) file for graphics. Auto-created by LIBSU. |
| SCRAP1.LOTUS                   | Scrap (clipboard) file for text. Auto-created by LIBSU. |
| SCRAP2.FIGURES                 | Secondary Scrap file for graphics. Auto-created by LIBSU. |
| SCRAP2.LOTUS                   | Secondary Scrap file for text. Auto-created by LIBSU. |
| ScrapOne                       | Data segment used by the Scrap. Auto-created by LIBSU. |
| ScrapTwo                       | Secondary data segment used by the Scrap. Auto-created by LIBSU. |
| shell.Office System            | The Office System shell (APDM). Once you build it, the new one is called shell.AlexTheCat123. |
| SUlib.OBJ                      | The Standard Unit intrinsic library. We don't have source code for this. |
| SYS1LIB.OBJ                    | The main system intrinsic library that contains most of the LIB** libraries. |
| SYS2LIB.OBJ                    | Everything that isn't in SYS1LIB or another intrinsic library. |
| SYSCALL.OBJ                    | Just the compiled version of LIBOS/SYSCALL.OBJ. |
| SYSTEM.BADPAGEMSG.LOTUS        | Message that LisaWrite shows if a page in your document gets corrupted. We can't generate this; it must be copied from an actual LOS install. |
| system.bt_Priam Disk           | Priam DataTower hard disk bootloader. |
| system.bt_Profile              | ProFile hard disk bootloader. |
| system.bt_Sony                 | Sony micro diskette bootloader. |
| system.cdd                     | The system's configurable driver directory. Contains a list of all the CD's installed; generated by either PROGS/CDCONFIG.OBJ or the Preferences tool. |
| system.cd_2 Port Card          | 2-port parallel card driver. |
| system.cd_Archive Tape         | Priam DataTower tape drive driver. |
| system.cd_Console              | Text console driver. |
| system.cd_Modem A              | Modem (attached to Serial A) driver. |
| system.cd_Parallel Cable       | Parallel cable (for a parallel port printer) driver. |
| system.cd_Priam Card           | Priam DataTower interface card driver. |
| system.cd_Priam Disk           | Priam DataTower hard disk driver. |
| system.cd_Profile              | ProFile hard disk driver. |
| system.cd_Serial Cable         | Serial port driver. |
| system.cd_Sony                 | Sony micro diskette driver. |
| SYSTEM.CIALERTS.PHRASE         | The phrase file for the C-Itoh (ImageWriter) printer. |
| SYSTEM.CNALERTS.PHRASE         | The phrase file for the Canon (Inkjet) printer. |
| system.debug                   | LisaBug. We don't have the source code to this; it comes with the Workshop. |
| system.debug2                  | More of LisaBug. Once again, we don't have the source code. |
| SYSTEM.DMALERTSPHRASE          | Phrase file for the Desktop Manager (shell.Office System). The one for shell.AlexTheCat123 will be called SYSTEM.DMALEXALERTSPHRASE. |
| SYSTEM.DW.PHRASE               | The phrase file for the daisy wheel printer. |
| system.IUDirectory             | Intrinsic unit directory data segment created and used by the OS. I think this keeps track of what intrinsic segments are loaded into RAM at any given point in time. |
| system.lld                     | Low-level driver file containing hardware interface routines. Loaded early in the boot process. |
| system.os                      | The OS code itself. |
| SYSTEM.PARENT.PHRASE           | Phrase file for the system background print process. |
| SYSTEM.PR.PHRASE               | Phrase file containing general alerts related to printing. |
| SYSTEM.PRD                     | Printer directory file. Contains a list of all the printer drivers installed; generated by the Preferences tool. |
| System.PrData                  | Data segment created and used by the printer library. |
| System.Print                   | The system's background printing process. Started by the Desktop Manager and runs all the time. |
| System.PR_Daisy Wheel Printer  | Driver for the daisy wheel printer. |
| System.PR_Imagewriter / II DMP | Driver for the ImageWriter printer. |
| System.PR_Ink Jet Printer      | Driver for the Canon inkjet printer. |
| system.shell                   | The Environments Window boot picker. |
| SYSTEM.UNPACK                  | A packtable containing code often shared between other files. Allows for file compression. We have to steal this from an existing LOS installation. |
| TKLIB.OBJ                      | Part 1 of the Lisa ToolKit API intrinsic library. |
| TK2LIB.OBJ                     | Part 2 of the Lisa ToolKit API intrinsic library. |

# Changelog
- 7/9/2025 - Initial Release
- 7/24/2025 - Added ```lisa_serial_transfer.py```, a script for easily transferring the source files over to the Lisa. Also updated the disk image and ```src``` directory with a new ```ALEX/TRANSFER.TEXT``` script, an ```ALEX/ASM/LIBSM.TEXT``` script that was previously missing, and a fixed version of ```ALEX/COMP/LIBOS```.
- 7/25/2025 - Updated ```lisa_serial_transfer.py``` to use a larger buffer size, the -KEYBOARD instead of -CONSOLE, and a bunch of other tweaks. This has increased performance by a factor of two! Updated the disk image and ```ALEX/TRANSFER.TEXT``` accordingly too.
- 7/26/2025 - Updated ```lisa_serial_transfer.py``` to use my custom ```ALEX-RECEIVE.TEXT``` program to transfer files while preserving the high bit (and thus special characters). Also added ```patch_files.py```, a script that automatically patches all the source files that need modifications. These changes eliminate all the manual work needed to prepare the code for compilation. Updated the disk image accordingly.
- 7/27/2025 - Fixed a bug in ```ALEX-RECEIVE.TEXT``` where transfers would occasionally end prematurely during large multi-file operations. Also added status output on the Lisa's display during the transfer. Updated the disk image accordingly.
- 7/29/2025 - Updated the build scripts (and disk image) to correct a few mistakes that were in the initial set. Also updated ```patch_files.py``` to correct a mistake or two and to patch LisaGuide.