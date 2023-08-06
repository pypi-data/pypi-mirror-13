.. image:: https://img.shields.io/github/release/dslackw/slpkg.svg
    :target: https://github.com/dslackw/slpkg/releases
.. image:: https://travis-ci.org/dslackw/slpkg.svg?branch=master
    :target: https://travis-ci.org/dslackw/slpkg
.. image:: https://landscape.io/github/dslackw/slpkg/master/landscape.png
    :target: https://landscape.io/github/dslackw/slpkg/master
.. image:: https://img.shields.io/codacy/6464ba0bd1e342e28388c71a34b3a5e8.svg
    :target: https://www.codacy.com/public/dzlatanidis/slpkg/dashboard
.. image:: https://img.shields.io/pypi/dm/slpkg.svg
    :target: https://pypi.python.org/pypi/slpkg
.. image:: https://img.shields.io/sourceforge/dt/slpkg.svg
    :target: https://sourceforge.net/projects/slpkg/
.. image:: https://img.shields.io/badge/license-GPLv3-blue.svg
    :target: https://github.com/dslackw/slpkg
.. image:: https://img.shields.io/github/stars/dslackw/slpkg.svg
    :target: https://github.com/dslackw/slpkg
.. image:: https://img.shields.io/github/forks/dslackw/slpkg.svg
    :target: https://github.com/dslackw/slpkg
.. image:: https://img.shields.io/github/issues/dslackw/slpkg.svg
    :target: https://github.com/dslackw/slpkg/issues
 

Slpkg v3.0.9
============

|

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/slpkg_package.png
    :target: https://github.com/dslackw/slpkg

|

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/poweredbyslack.gif
    :target: http://www.slackware.com/
|

.. contents:: Table of Contents:


About
-----

Slpkg is a powerful software package manager that installs, updates, and removes packages on 
Slackware based systems. It automatically computes dependencies and figures out what things 
should occur to install packages. Slpkg makes it easier to maintain groups of machines without 
having to manually update.

Slpkg works in accordance with the standards of the organization slackbuilds.org 
to builds packages. Also uses the Slackware Linux instructions for installation,
upgrading or removing packages. 

What makes slpkg to distinguish it from other tools; The user friendliness is its primary 
target as well as easy to understand and use, also use color to highlight packages and 
display warning messages, etc.


Features
--------

- Dependency resolution
- Dependencies visualizations
- Multiple options
- Multiple repositories
- Easy configuration
- Fully configurable
- Adaptability
- Powerful options
- Source builder
- Faster process
- Better Security


Installation
------------

Download latest release:

.. code-block:: bash
    
    Required root privileges
   
    $ tar xvf slpkg-3.0.9.tar.gz
    $ cd slpkg-3.0.9
    $ ./install.sh
    
    Installed as Slackware package

    Uninstall:

    $ slpkg -r slpkg

    or

    $ removepkg slpkg


Using pip:

.. code-block:: bash
    
    $ pip install slpkg --upgrade
    
    Uninstall:

    $ pip uninstall slpkg

    Data remove run from source code:

    $ python clean.py


Binary packages:

Slackware: `slpkg-3.0.9-i486-1_dsw.txz <https://github.com/dslackw/slpkg/releases/download/v3.0.9/slpkg-3.0.9-i486-1_dsw.txz>`_

Slackware64: `slpkg-3.0.9-x86_64-1_dsw.txz <https://github.com/dslackw/slpkg/releases/download/v3.0.9/slpkg-3.0.9-x86_64-1_dsw.txz>`_


Optional dependencies
---------------------

`python2-pythondialog <http://slackbuilds.org/repository/14.1/python/python2-pythondialog/>`_ for dialog box interface

`pygraphviz <http://slackbuilds.org/repository/14.1/graphics/pygraphviz/>`_ for drawing dependencies diagram

`graph-easy <http://slackbuilds.org/repository/14.1/graphics/graph-easy/>`_ for drawing ascii dependencies diagram


Recommended
-----------

Stay updated, see `SUN (Slackware Update Notifier) <https://github.com/dslackw/sun>`_


Upgrade
-------

From version '2.1.4' you can update slpkg itself with '# slpkg update slpkg'.
In each slpkg upgrade should track the configuration files in the folder '/etc/slpkg' 
for changes.


Demonstration
-------------

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/slpkg_youtube.png
    :target: https://www.youtube.com/watch?v=oTtD4XhHKlA


Youtube Asciicasts
------------------

`Playlist Tutorials <https://www.youtube.com/playlist?list=PLLzUUMSzaKvlS5--8AiFqWzxZPg3kxkqY>`_
 
 
Repositories
------------

Default available Repositories:

- `SBo <http://slackbuilds.org/>`_
  Arch: {x86, x86_64}
  Versions: {13.1, 13.37, 14.0, 14.1}
- `Slack <http://www.slackware.com/>`_
  Arch: {x86, x86_64}
  Versions: {3.3, 8.1, 9.0, 9.1, 10.0, 10.1, 10.2, 11.0, 12.0, 12.2, 13.0, 13.37, 14.0, 14.1, current}
- `Alien's <http://taper.alienbase.nl/mirrors/people/alien/sbrepos/>`_
  Arch: {x86, x86_64}
  Versions: {13.0, 13.1, 13.37, 14.0, 14.1, current}
- `Slacky <http://repository.slacky.eu/>`_
  Arch: {x86, x86_64}
  Versions: {11.0, 12.0, 12.1, 12.2, 13.0, 13.1, 13.37, 14.0, 14.1}
- `Robby's <http://rlworkman.net/pkgs/>`_
  Arch: {x86, x86_64}
  Versions: {11.0, 12.0, 12.1, 12.2, 13.0, 13.1, 13.37, 14.0, 14.1}
- `Studioware <http://studioware.org/packages>`_
  Arch: {x86, x86_64}
  Versions: {13.37, 14.0, 14.1}
- `Slackers <http://ponce.cc/slackers/repository/>`_
  Arch: {x86_64}
  Versions: {current}
- `Slackonly <https://slackonly.com/>`_
  Arch: {x86, x86_64}
  Versions: {14.1}
- `Alien's ktown <http://alien.slackbook.org/ktown/>`_
  Arch: {x86, x86_64}
  Versions: {13.37, 14.0, 14.1, current}
- `Alien's multi <http://www.slackware.com/~alien/multilib/>`_
  Arch: {x86_64}
  Versions: {13.0, 13.1, 13.37, 14.0, 14.1, current}
- `Slacke E17 and E18 <http://ngc891.blogdns.net/pub/>`_
  Arch: {x86, x86_64, arm}
  Versions: {14.1}
- `SalixOS <http://download.salixos.org/>`_
  Arch: {x86, x86_64}
  Versions: {13.0, 13.1, 13.37, 14.0, 14.1}
- `Slackel <http://www.slackel.gr/repo/>`_
  Arch: {x86, x86_64}
  Versions: {current}
- `Restricted <http://taper.alienbase.nl/mirrors/people/alien/restricted_slackbuilds/>`_
  Arch: {x86, x86_64}
  Versions: {11.0, 12.0, 12.1, 12.2, 13.0, 13.1, 13.37, 14.0, 14,1, current}
- `MATE Desktop Environment <http://slackware.org.uk/msb/>`_
  Arch: {x86, x86_64}
  Versions: {14.0, 14,1}


* Choose default repositories you need to work from file '/etc/slpkg/repositories.conf' default 
  is 'slack' and 'sbo' repositories and read REPOSITORIES file for each of the particularities.
  If a repository is not in the above list, manage custom repositories with commands 'repo-add'
  and 'repo-remove'.


Usage
-----

Need to run '# slpkg update' for the first time to synchronize the list of packages,
also every time you add a new repository.
To add or remove repositories must edit the file '/etc/slpkg/repositories.conf'.

Add custom repositories with the command '# slpkg add-repo <repository name> <URL>' and after
run '# slpkg update' to update package list.

View list of repositories with command '# slpkg repo-list' or get repository information with
command '# slpkg repo-info <repository>.

Update slpkg itself simply run '# slpkg update slpkg', and slpkg check from GitHub repository if
new versions are available.

Checking packages health with command "# slpkg health" and slpkg check if files missing from 
package file list.

Print dependencies status used by packages with command '# slpkg deps-status' or drawing image 
map dependencies with additional option '--graph=[image]'.

Manage .new configuration files with command 'slpkg new-config' like remove, overwrite, merge etc.

If you have already downloaded the script and the source code you can build the package with 
the command '# slpkg <script.tar.gz> <sources>'.

Manage packages in the black list with the command '# slpkg -b <packages> --add or --remove'.

Add SBo packages to queue with command '# slpkg -q <packages> --add or --remove' and manage as 
build, install or build and install with command '# slpkg build or install or build-install'.
This is very useful if you want to install multiple packages together suffice to add in the right 
order if there are dependent packages.

View list of packages from specific repository with command '# slpkg -l <repository>'.
Combine with the command 'grep' to catch the results you want.

Check and upgrade the distribution of your upgrade your packages with command '# slpkg -c <repository> 
--upgrade'. Don't forget to update packages list before (for 'slack' repository don't is necessary).
This command except upgrade packages will fix packages with broken dependencies. Switch  off automatic
resolve dependencies with additional option '--resolve-off'. Use '--checklist' option to help you
to choose easy packages. For advanced users, option '--skip' give them more power (see man page).

The most famous command is '# slpkg -s <repository> <packages>' , this command downloads and 
installs packages with resolve all the dependencies or switch off resolve with additional option
'--resolve-off'. Also additional option "--case-ins" help you find packages with case insensitive.

Tracking the dependencies of a package with command '# slpkg -t <repository> <package>'.
Displays a package dependency tree and also tells you which ones are installed on your system events.
Check if packages used from other packages with additional option '--check-deps' or drawing image 
map dependencies with additional option '--graph=[image]'.

Get information description of a package with command '# slpkg -p <repository> <package>' and change
color text with additional flag '--color=[]'.

View a page SBo package on your terminal with command '# slpkg -n <package>' and then manage multiple 
choices such read, download, build, install etc.

If you want to find packages from all repositories, this command will solve your hands '# slpkg -F 
<packages>'. It will search in all enabled repositories will find the configuration file 
'/etc/slpkg/repositories.conf' will print all the packages that match the description that you enter.

If you want to see if any packages are installed on your system enter the command '# slpkg -f <packages>'.
The surprise in the end is the reporting of packages sum and size found.

The next four commands '# slpkg --installpkg, --upgradepkg, --removepkg <packages>' install, upgrade, 
remove packages from your system events.
Notable mention must give the command '# slpkg --removepkg <packages>' which can remove a packages 
with all dependencies together after editing configuration file '/etc/slpkg/slpkg.conf' 
(default is disable) or add additional option "--deps". Also you can check if packages used as 
dependency with additional option 
"--check-deps". Option "--tag" allow to remove packages with by TAG.
Optional you can use dialog utility with additional option "--checklist" (require python2-pythondialog).

The last command is useful to print the entire contents of a package installed on the system with the
command '# slpkg -d <packages>'.

Some examples you will see below.


Issues
------

Please report any bugs in `ISSUES <https://github.com/dslackw/slpkg/issues>`_


Testing
-------

The majority of trials have been made in an environment Slackware x86_64 'stable' 
and x86 'current' version 14.1.


Slackware Current
-----------------

For Slackware 'current' users must change the variable VERSION in '/etc/slpkg/slpkg.conf' file.

.. code-block:: bash

    $ slpkg -g edit


Slackware ARM
-------------

Must use only two repositories currently there 'slack' and 'sbo'.


Slackware Mirrors
-----------------

Slpkg uses the central mirror "http://mirrors.slackware.com/slackware/" to find the 
nearest one. If however for some reason this troublesome please edit the file in 
'/etc/slpkg/slackware-mirrors'.


Slpkg configuration
-------------------

It is important to read the configuration file '/etc/slpkg/slpkg.conf'. You will find many 
useful options to configure the program so as you need it.

A simple example is to close the progress bar for speed, changing the variable PRG_BAR the 
value "off".


Configuration Files
-------------------

.. code-block:: bash

    /tmp/slpkg
         Slpkg temponary donwloaded files and build packages

    /etc/slpkg/slpkg.conf
         General configuration of slpkg
    
    /etc/slpkg/repositories.conf
         Configuration file for repositories

    /etc/slpkg/blacklist
         List of packages to skip

    /etc/slpkg/slackware-mirrors
         List of Slackware Mirrors

    /etc/slpkg/default-repositories
         List of default repositories

    /etc/slpkg/custom-repositories
         List of custom repositories

    /var/log/slpkg
         ChangeLog.txt repositories files
         SlackBuilds logs and dependencies files

    /var/lib/slpkg
         PACKAGES.TXT files 
         SLACKBUILDS.TXT files
         CHECKSUMS.md5 files
         FILELIST.TXT files

     
Command Line Tool Usage
-----------------------

.. code-block:: bash

    Slpkg is a user-friendly package manager for Slackware installations
    
    Usage: slpkg [COMMANDS|OPTIONS] {repository|package...}

                                                     _       _
                                                 ___| |_ __ | | ____ _
                                                / __| | '_ \| |/ / _` |
                                                \__ \ | |_) |   < (_| |
                                                |___/_| .__/|_|\_\__, |
                                                      |_|        |___/

    Commands:
       update, --only=[...]                      Run this command to update all
                                                 the packages list.
       upgrade, --only=[...]                     Delete and recreate all packages
                                                 lists.
       repo-add [repository name] [URL]          Add custom repository.
       repo-remove [repository]                  Remove custom repository.
       repo-enable                               Enable or disable default
                                                 repositories via dialog utility.
       repo-list                                 Print a list of all the
                                                 repositories.
       repo-info [repository]                    Get information about a
                                                 repository.
       update slpkg                              Upgrade the program directly from
                                                 repository.
       health, --silent                          Health check installed packages.
       deps-status, --tree, --graph=[type]       Print dependencies status used by
                                                 packages or drawing dependencies
                                                 diagram.
       new-config                                Manage .new configuration files.

    Optional arguments:
      -h | --help                                Print this help message and exit.
      -v | --version                             Print program version and exit.
      -a | --autobuild, [script] [source...]     Auto build SBo packages.
                                                 If you already have downloaded the
                                                 script and the source code you can
                                                 build a new package with this
                                                 command.
      -b | --blacklist, [package...] --add,      Manage packages in the blacklist.
           --remove, list                        Add or remove packages and print
                                                 the list. Each package is added
                                                 here will not be accessible by the
                                                 program.
      -q | --queue, [package...] --add,          Manage SBo packages in the queue.
           --remove, list, build, install,       Add or remove and print the list
           build-install                         of packages. Build and then
                                                 install the packages from the
                                                 queue.
      -g | --config, print, edit, reset          Configuration file management.
                                                 Print, edit the configuration file
                                                 or reset in the default values.
      -l | --list, [repository], --index,        Print a list of all available
           --installed, --name                   packages from repository, index or
                                                 print only packages installed on
                                                 the system.
      -c | --check, [repository], --upgrade,     Check for updated packages from
           --skip=[...], --resolve--off          the repositories and upgrade or
           --checklist                           install with all dependencies.
      -s | --sync, [repository] [package...],    Sync packages. Install packages
           --resolve-off, --download-only,       directly from remote repositories
           --directory-prefix=[dir], --case-ins  with all dependencies.
      -t | --tracking, [repository] [package],   Tracking package dependencies and
           --check-deps, --graph=[type],         print package dependencies tree
           --case-ins                            with highlight if packages is
                                                 installed. Also check if
                                                 dependencies used or drawing
                                                 dependencies diagram.
      -p | --desc, [repository] [package],       Print description of a package
           --color=[]                            directly from the repository and
                                                 change color text.
      -n | --network, [package], --checklist,    View a standard of SBo page in
           --case-ins                            terminal and manage multiple
                                                 options like reading, downloading,
                                                 building, installation, etc.
      -F | --FIND, [package...], --case-ins      Find packages from each enabled
                                                 repository and view results.
      -f | --find, [package...], --case-ins      Find and print installed packages
                                                 reporting the size and the sum.
      -i | --installpkg, [options] [package...]  Installs single or multiple *.tgz
           options=[--warn, --md5sum, --root,    (or .tbz, .tlz, .txz) Slackware
           --infobox, --menu, --terse, --ask,    binary packages designed for use
           --priority, --tagfile]                with the Slackware Linux
                                                 distribution onto your system.
      -u | --upgradepkg, [options] [package...]  Upgrade single or multiple
           options=[--dry-run, --install-new,    Slackware binary packages from
           --reinstall, --verbose]               an older version to a newer one.
      -r | --removepkg, [options] [package...],  Removes a previously installed
           --deps, --check-deps, --tag,          Slackware binary packages,
           --checklist                           while writing a progress report
           options=[-warn, -preserve, -copy,     to the standard output.
           -keep]                                Use only package name.
      -d | --display, [package...]               Display the contents of installed
                                                 packages and file list.


Slpkg Examples
--------------

Enable or disable default repositories, edit /etc/slpkg/repositories.conf file or with 
command.
(require pythondialog, install with '# slpkg -s sbo python2-pythondialog'):

.. code-block:: bash
    
    $ slpkg repo-enable

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/repo_enable.png
    :target: https://raw.githubusercontent.com/dslackw/images/master/slpkg/deps2.png


If you use slpkg for the first time will have to create and update the package 
list. This command must be executed to update the package lists:

.. code-block:: bash

    $ slpkg update

    Update repository [slack] ... Done
    Update repository [sbo] ... Done
    Update repository [alien] ... Done
    Update repository [slacky] ... Done
    Update repository [studio] ... Done
    Update repository [slackr] ... Done
    Update repository [slonly] ... Done
    Update repository [ktown] ... Done
    Update repository [salix] ... Done
    Update repository [slacke] ... Done
    Update repository [slackl] ... Done
    Update repository [multi] ... Done
    Update repository [msb] ... Done

    Update specifically repositories:

    $ slpkg update --only=sbo,msb,slacky

Also you can check ChangeLog.txt for changes like:

.. code-block::

    $ slpkg -c sbo
    
    +==============================================================================
    | Repository         Status
    +==============================================================================
      sbo                News in ChangeLog.txt

    Summary
    ===============================================================================
    From 1 repositories need 1 updating. Run the command 'slpkg update'.


    $ slpkg -c ALL

    +==============================================================================
    | Repository         Status
    +==============================================================================
      slack              No changes in ChangeLog.txt
      sbo                News in ChangeLog.txt
      slacky             News in ChangeLog.txt
      alien              No changes in ChangeLog.txt
      rlw                No changes in ChangeLog.txt

    Summary
    ===============================================================================
    From 5 repositories need 2 updating. Run the command 'slpkg update'.


Add and remove custom repositories:

.. code-block:: bash

    $ slpkg repo-add ponce http://ponce.cc/slackware/slackware64-14.1/packages/

    Repository 'ponce' successfully added


    $ slpkg repo-add repo1 file:///home/user1/repos/alien/
    
    Repository 'repo1' successfully added

    
    $ slpkg repo-remove ponce

    Repository 'ponce' successfully removed

    
View information about the repositories:
    
.. code-block:: bash

    $ slpkg repo-list
    
    +==============================================================================
    | Repo id  Repo URL                                            Default   Status
    +==============================================================================
      alien    http://www.slackware.com/~alien/slackbuilds/        yes     disabled
      ktown    http://alien.slackbook.org/ktown/                   yes     disabled
      msb      http://slackware.org.uk/msb/                        yes      enabled
      multi    http://www.slackware.com/~alien/multilib/           yes     disabled
      ponce    http://ponce.cc/slackware/slackware64-14.1/packa~   no       enabled
      rested   http://taper.alienbase.nl/mirrors/people/alien/r~   yes     disabled
      rlw      http://rlworkman.net/pkgs/                          yes     disabled
      salix    http://download.salixos.org/                        yes     disabled
      sbo      http://slackbuilds.org/slackbuilds/                 yes      enabled
      slack    http://ftp.cc.uoc.gr/mirrors/linux/slackware/       yes      enabled
      slacke   http://ngc891.blogdns.net/pub/                      yes     disabled
      slackl   http://www.slackel.gr/repo/                         yes     disabled
      slackr   http://www.slackers.it/repository/                  yes     disabled
      slacky   http://repository.slacky.eu/                        yes     disabled
      slonly   https://slackonly.com/pub/packages/                 yes     disabled
      studio   http://studioware.org/files/packages/               yes     disabled

    Repositories summary
    ===============================================================================
    3/15 enabled default repositories and 1 custom.
    For enable or disable default repositories edit '/etc/slpkg/repositories.conf' 
    file.

    $ slpkg repo-info alien

    Default: yes
    Last updated: Tue Dec 23 11:48:31 UTC 2014
    Number of packages: 3149
    Repo id: alien
    Repo url: http://www.slackware.com/~alien/slackbuilds/
    Status: enabled
    Total compressed packages: 9.3 Gb
    Total uncompressed packages: 36.31 Gb


Installing packages from the repositories (supporting multi packages):

.. code-block:: bash
    
    $ slpkg -s sbo brasero
    Reading package lists... Done
    Resolving dependencies... Done

    The following packages will be automatically installed or upgraded 
    with new version:

    +==============================================================================
    | Package                 New version        Arch    Build  Repos          Size
    +==============================================================================
    Installing:
      brasero                 3.12.1             x86_64         SBo
    Installing for dependencies:
      orc                     0.4.23             x86_64         SBo
      gstreamer1              1.4.5              x86_64         SBo
      gst1-plugins-base       1.4.5              x86_64         SBo
      gst1-plugins-bad        1.4.5              x86_64         SBo

    Installing summary
    ===============================================================================
    Total 5 packages.
    5 packages will be installed, 0 already installed and 0 package
    will be upgraded.

    Would you like to continue [y/N]?
    
    
    Example install multi packages:
    
    $ slpkg -s sbo brasero pylint atkmm
    Reading package lists... Done
    Resolving dependencies... Done

    The following packages will be automatically installed or upgraded 
    with new version:
    
    +==============================================================================
    | Package                 New version        Arch    Build  Repos          Size
    +==============================================================================
    Installing:
      brasero                 3.12.1             x86_64         SBo
      pylint-1.3.1            1.3.1              x86_64         SBo
      atkmm                   2.22.7             x86_64         SBo
    Installing for dependencies:
      libsigc++               2.2.11             x86_64         SBo
      glibmm                  2.36.2             x86_64         SBo
      cairomm                 1.10.0             x86_64         SBo
      pangomm                 2.34.0             x86_64         SBo
      six-1.8.0               1.8.0              x86_64         SBo
      pysetuptools-17.0       17.0               x86_64         SBo
      logilab-common-0.63.2   0.63.2             x86_64         SBo
      astroid-1.3.6           1.3.6              x86_64         SBo
      orc                     0.4.23             x86_64         SBo
      gstreamer1              1.4.5              x86_64         SBo
      gst1-plugins-base       1.4.5              x86_64         SBo
      gst1-plugins-bad        1.4.5              x86_64         SBo

    Installing summary
    ===============================================================================
    Total 15 packages.
    10 packages will be installed, 5 already installed and 0 package
    will be upgraded.

    Would you like to continue [y/N]?


    Example from 'alien' repository:

    $ slpkg -s alien atkmm
    Reading package lists... Done
    Resolving dependencies... Done

    +==============================================================================
    | Package                 New version        Arch    Build  Repos          Size
    +==============================================================================
    Installing:
      atkmm                   2.22.6             x86_64  1      alien         124 K
    Installing for dependencies:
      libsigc++               2.2.10             x86_64  2      alien         128 K
      glibmm                  2.32.1             x86_64  1      alien        1012 K
      cairomm                 1.10.0             x86_64  2      alien         124 K
      pangomm                 2.28.4             x86_64  1      alien         124 K

    Installing summary
    ===============================================================================
    Total 5 packages.
    5 packages will be installed, 0 will be upgraded and 0 will be reinstalled.
    Need to get 124 Kb of archives.
    After this process, 620 Kb of additional disk space will be used.

    Would you like to continue [y/N]?

    
Close auto resolve dependencies:

.. code-block:: bash

    $ slpkg -s alien atkm --resolve-off
    Reading package lists... Done

    The following packages will be automatically installed or upgraded 
    with new version:

    +==============================================================================
    | Package                 New version        Arch    Build  Repos          Size
    +==============================================================================
    Installing:
      atkmm                   2.22.6             x86_64  1      alien         124 K
    
     Installing summary
     ===============================================================================
     Total 1 package.
     1 package will be installed, 0 will be upgraded and 0 will be reinstalled.
     Need to get 124 Kb of archives.
     After this process, 620 Kb of additional disk space will be used.

     Would you like to continue [y/N]?



Build packages and passing variables to the script:

.. code-block:: bash

    First export variable(s) like:
    
    $ export FFMPEG_ASS=yes FFMPEG_X264=yes
    
    
    And then run as you know:

    $ slpkg -s sbo ffmpeg

    or

    $ slpkg -n ffmpeg

    or if already script and source donwloaded:

    $ slpkg -a ffmpeg.tar.gz ffmpeg-2.1.5.tar.bz2

    
Tracking all dependencies of packages,
and also displays installed packages:

.. code-block:: bash

    $ slpkg -t sbo brasero
    Resolving dependencies... Done

    +=========================
    | brasero dependencies   :
    +=========================
    \ 
     +---[ Tree of dependencies ]
     |
     +--1 orc
     |
     +--2 gstreamer1
     |
     +--3 gst1-plugins-base
     |
     +--4 gst1-plugins-bad
     |
     +--5 libunique

    
Check if dependencies used:

.. code-block:: bash

    $ slpkg -t sbo Flask --check-deps
    Resolving dependencies... Done

    +=============================
    | Package Flask dependencies :
    +=============================
    \
     +---[ Tree of dependencies ]
     |
     +--1: pysetuptools is dependency --> Flask, bpython, pip, pylint
     |
     +--2: MarkupSafe is dependency --> Flask
     |
     +--3: itsdangerous is dependency --> Flask
     |
     +--4: Jinja2 is dependency --> Flask
     |
     +--5: werkzeug is dependency --> Flask

    
Drawing dependencies diagram:

.. code-block:: bash

    $ slpkg -t sbo flexget --graph=image.x11

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/deps2.png
    :target: https://raw.githubusercontent.com/dslackw/images/master/slpkg/deps2.png


.. code-block:: bash

    $ slpkg -t sbo Flask --check-deps --graph=image.x11
    Resolving dependencies... Done

    +=============================
    | Package Flask dependencies :
    +=============================
    \
     +---[ Tree of dependencies ]
     |
     +--1: pysetuptools is dependency --> APScheduler, Flask, Jinja2, MarkupSafe, astroid, autopep8, blessings, bpython, cffi, cryptography, curtsies, itsdangerous, monty, ndg_httpsclient, pip, pyOpenSSL, pylint, wcwidth
     |
     +--2: MarkupSafe is dependency --> Flask, Jinja2
     |
     +--3: itsdangerous is dependency --> Flask
     |
     +--4: Jinja2 is dependency --> Flask
     |
     +--5: werkzeug is dependency --> Flask

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/deps3.png
    :target: https://raw.githubusercontent.com/dslackw/images/master/slpkg/deps3.png


Drawing dependencies ascii diagram:

.. code-block:: bash
   
    $ slpkg -t sbo botocore --graph=ascii
    
                                       +---------------------------------+
                                       |                                 |
                                       |                                 |
                                       |    +---------+                  |
                                       |    |         |                  |
                                       |    |         |                  |
                      +----------------+----+----+    |                  |
                      |                |    |    |    |                  |
    +--------------+  |  +--------------------+  |  +-----------------+  |
    |   jmespath   | -+- |      botocore      |  +- | python-dateutil |  |
    +--------------+  |  +--------------------+     +-----------------+  |
      |               |    |           |    |         |                  |
      |               |    |           |    |         |                  |
      |               |    |           |    |         |                  |
    +--------------+  |  +----------+  |    |       +-----------------+  |
    | pysetuptools | -+  |  bcdoc   | -+----+------ |       six       | -+
    +--------------+     +----------+  |    |       +-----------------+
      |                    |           |    |
      |                    |           |    |
      |                    |           |    |
      |                  +----------+  |    |
      |                  | docutils | -+    |
      |                  +----------+       |
      |                                     |
      +-------------------------------------+


Print dependencies status used by packages:

.. code-block:: bash
   
    $ slpkg deps-status

    +==============================================================================
    | Dependencies                    Packages
    +==============================================================================
      astroid                         pylint
      logilab-common                  pylint
      werkzeug                        Flask
      cryptography                    bpython
      ndg_httpsclient                 bpython
      enum34                          bpython
      pyOpenSSL                       bpython
      curtsies                        bpython
      six                             bpython, pylint
      cffi                            bpython
      python-requests                 bpython
      pysetuptools                    Flask, bpython, pip, pylint
      MarkupSafe                      Flask
      Pygments                        bpython
      Jinja2                          Flask
      pycparser                       bpython
      blessings                       bpython
      greenlet                        bpython
      pyasn1                          bpython

    Summary
    ===============================================================================
    Found 19 dependencies in 4 packages.


Use additional option "--graph=[image]" to drawing dependencies diagram:

.. code-block:: bash

    $ slpkg deps-status --graph=image.x11

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/deps.png
    :target: https://raw.githubusercontent.com/dslackw/images/master/slpkg/deps.png

Check if your packages is up to date or changes in ChangeLog.txt:

.. code-block:: bash

    You can check ChangeLog.txt for changes before with command:

    $ slpkg -c sbo

    +==============================================================================
    | Repository         Status
    +==============================================================================
      sbo                News in ChangeLog.txt

    Summary
    ===============================================================================
    From 1 repositories need 1 updating. Run the command 'slpkg update'.


And check if packages need upgrade with:

.. code-block:: bash

    $ slpkg -c sbo --upgrade
    Checking... Done
    Reading package lists... Done
    Resolving dependencies... Done

    The following packages will be automatically installed or upgraded 
    with new version:

    +==============================================================================
    | Package                 New version        Arch    Build  Repos          Size
    +==============================================================================
    Upgrading:
      astroid-1.3.2           1.3.4              x86_64         SBo           
      jdk-7u51                8u31               x86_64         SBo           
    Installing for dependencies:
      six-1.7.3               1.8.0              x86_64         SBo           
      logilab-common-0.60.1   0.63.2             x86_64         SBo           
      pysetuptools-6.1        7.0                x86_64         SBo           

    Installing summary
    ===============================================================================
    Total 5 packages.
    0 package will be installed, 2 already installed and 3 packages
    will be upgraded.

    Would you like to continue [y/N]?


    $ slpkg -c slacky --upgrade
    Checking... Done
    Reading package lists... Done
    Resolving dependencies... Done

    +==============================================================================
    | Package                 New version        Arch    Build  Repos          Size
    +==============================================================================
    Upgrading:
      gstreamer1-1.4.1        1.4.4              x86_64  1      slacky       1563 K

    Installing summary
    ===============================================================================
    Total 1 package.
    0 package will be installed, 1 will be upgraded and 0 will be reinstalled.
    Need to get 1.53 Mb of archives.
    After this process, 14.55 Mb of additional disk space will be used.

    Would you like to continue [y/N]? 


Check if your Slackware distribution is up to date.
This option works independently of the others i.e not need before updating the list of
packages by choosing "# slpkg update", works directly with the official repository and
why always you can have updated your system:

.. code-block:: bash

    $ slpkg -c slack --upgrade
    Reading package lists... Done

    These packages need upgrading:
    
    +==============================================================================
    | Package                   New version      Arch     Build  Repos         Size
    +==============================================================================
    Upgrading:
      dhcpcd-6.0.5              6.0.5            x86_64   3      Slack         92 K
      samba-4.1.0               4.1.11           x86_64   1      Slack       9928 K
      xscreensaver-5.22         5.29             x86_64   1      Slack       3896 K

    Installing summary
    ===============================================================================
    Total 3 package will be upgrading and 0 will be installed.
    Need to get 13.58 Mb of archives.
    After this process, 76.10 Mb of additional disk space will be used.
    
    Would you like to continue [y/N]?

    
    
Upgrade only distribution:

.. code-block:: bash

    $ slpkg -c slack --upgrade --skip="multi:*multilib*,ktown:*"  // This upgrade 
    Checking... Done                                              // distribution
                                                                  // and skip all 
    Slackware64 'stable' v14.1 distribution is up to date         // packages from
                                                                  // ktown repository
                                                                  // and multilib
                                                                  // from multi.
Skip packages when upgrading:

.. code-block:: bash

    $ slpkg -c sbo --upgrade --skip=pip,jdk     // Available options:
    Checking... Done                            // repository:*string*
    Reading package lists... Done               // repository:string*
    Resolving dependencies... Done              // repository:*string

    The following packages will be automatically installed or upgraded 
    with new version:

    +==============================================================================
    | Package                 New version        Arch    Build  Repos          Size
    +==============================================================================
    Upgrading:
      cffi-1.0.1              1.1.0              x86_64         SBo
    Installing for dependencies:
      pysetuptools-17.0       17.0               x86_64         SBo
      pycparser-2.12          2.13               x86_64         SBo

    Installing summary
    ===============================================================================
    Total 3 packages.
    0 package will be installed, 1 already installed and 2 packages
    will be upgraded.

    Would you like to continue [y/N]?


View complete slackbuilds.org site in your terminal.
Read files, download, build or install:

.. code-block:: bash

    $ slpkg -n bitfighter
    Reading package lists... Done

    +==============================================================================
    |                             SlackBuilds Repository
    +==============================================================================
    | 14.1 > Games > bitfighter
    +===============================================================================
    | Package url: http://slackbuilds.org/repository/14.1/games/bitfighter/
    +===============================================================================
    | Description: multi-player combat game
    | SlackBuild: bitfighter.tar.gz
    | Sources: bitfighter-019c.tar.gz, classic_level_pack.zip 
    | Requirements: OpenAL, SDL2, speex, libmodplug
    +===============================================================================
    | README               View the README file
    | SlackBuild           View the .SlackBuild file
    | Info                 View the .info file
    | Doinst.sh            View the doinst.sh file
    | Download             Download this package
    | Build                Download and build this package
    | Install              Download/Build/Install
    | Clear                Clear screen
      Quit                 Quit
    +================================================================================ 
      Choose an option > _


Use dialog utility to help you find a packages:

.. code-block:: bash
    
    Load all repository:

    $ slpkg -n ALL --checklist
    Reading package lists...

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/pythondialog5.png
    :target: https://github.com/dslackw/slpkg

.. code-block:: bash
    
    Search from pattern such as all 'perl' packages:

    $ slpkg -n perl --checklist
    Reading package lists...

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/pythondialog6.png
    :target: https://github.com/dslackw/slpkg

     
Auto tool to build package:

.. code-block:: bash

    Two files termcolor.tar.gz and termcolor-1.1.0.tar.gz
    must be in the same directory.
    (slackbuild script & source code or extra sources if needed)

    $ slpkg -a termcolor.tar.gz termcolor-1.1.0.tar.gz

    termcolor/
    termcolor/slack-desc
    termcolor/termcolor.info
    termcolor/README
    termcolor/termcolor.SlackBuild
    termcolor-1.1.0/
    termcolor-1.1.0/CHANGES.rst
    termcolor-1.1.0/COPYING.txt
    termcolor-1.1.0/README.rst
    termcolor-1.1.0/setup.py
    termcolor-1.1.0/termcolor.py
    termcolor-1.1.0/PKG-INFO
    running install
    running build
    running build_py
    creating build
    creating build/lib
    copying termcolor.py -> build/lib
    running install_lib
    creating /tmp/SBo/package-termcolor/usr
    creating /tmp/SBo/package-termcolor/usr/lib64
    creating /tmp/SBo/package-termcolor/usr/lib64/python2.7
    creating /tmp/SBo/package-termcolor/usr/lib64/python2.7/site-packages
    copying build/lib/termcolor.py -> 
    /tmp/SBo/package-termcolor/usr/lib64/python2.7/site-packages
    byte-compiling /tmp/SBo/package-termcolor/usr/lib64/python2.7/site-packages/termcolor.py 
    to termcolor.pyc
    running install_egg_info
    Writing 
    /tmp/SBo/package-termcolor/usr/lib64/python2.7/site-packages/termcolor-1.1.0-py2.7.egg-info

    Slackware package maker, version 3.14159.

    Searching for symbolic links:

    No symbolic links were found, so we wont make an installation script.
    You can make your own later in ./install/doinst.sh and rebuild the
    package if you like.

    This next step is optional - you can set the directories in your package
    to some sane permissions. If any of the directories in your package have
    special permissions, then DO NOT reset them here!

    Would you like to reset all directory permissions to 755 (drwxr-xr-x) and
    directory ownerships to root.root ([y]es, [n]o)? n

    Creating Slackware package:  /tmp/termcolor-1.1.0-x86_64-1_SBo.tgz

    ./
    usr/
    usr/lib64/
    usr/lib64/python2.7/
    usr/lib64/python2.7/site-packages/
    usr/lib64/python2.7/site-packages/termcolor.py
    usr/lib64/python2.7/site-packages/termcolor.pyc
    usr/lib64/python2.7/site-packages/termcolor-1.1.0-py2.7.egg-info
    usr/doc/
    usr/doc/termcolor-1.1.0/
    usr/doc/termcolor-1.1.0/termcolor.SlackBuild
    usr/doc/termcolor-1.1.0/README.rst
    usr/doc/termcolor-1.1.0/CHANGES.rst
    usr/doc/termcolor-1.1.0/PKG-INFO
    usr/doc/termcolor-1.1.0/COPYING.txt
    install/
    install/slack-desc

    Slackware package /tmp/termcolor-1.1.0-x86_64-1_SBo.tgz created.

    Total build time for package termcolor : 1 Sec


Upgrade, install packages like Slackware command '# upgradepkg --install-new':

.. code-block:: bash

    $ slpkg -u --install-new /tmp/termcolor-1.1.0-x86_64-1_SBo.tgz

    +==============================================================================
    | Installing new package ./termcolor-1.1.0-x86_64-1_SBo.tgz
    +==============================================================================

    Verifying package termcolor-1.1.0-x86_64-1_SBo.tgz.
    Installing package termcolor-1.1.0-x86_64-1_SBo.tgz:
    PACKAGE DESCRIPTION:
    # termcolor (ANSII Color formatting for output in terminal)
    #
    # termcolor allows you to format your output in terminal.
    #
    # Project URL: https://pypi.python.org/pypi/termcolor
    #
    Package termcolor-1.1.0-x86_64-1_SBo.tgz installed.

Install mass-packages:

.. code-block:: bash

    $ slpkg -u --install-new *.t?z
    
    or 

    $ slpkg -i *.t?z


Slpkg auto detect Slackware binary packages (.tgz, .txz, .tlz and .tbz) for installation:

.. code-block:: bash

    $ slpkg pysed-0.7.8-x86_64-1_SBo.tgz

    Detected Slackware binary package for installation:

      pysed-0.7.8-x86_64-1_SBo.tgz

    +==============================================================================
    | Choose a Slackware command:
    +==============================================================================
    | i)  installpkg
    | r)  upgradepkg --reinstall
    | u)  upgradepkg --install-new
    +==============================================================================
     > _

    
Search for packages from the enabled repositories:

.. code-block:: bash
   
    $ slpkg -F aria2

    Packages with name matching [ aria2 ]

    +==============================================================================
    | Repository  Package                                                      Size
    +==============================================================================
      sbo         aria2-1.18.10                                                 0 K
      slonly      aria2-1.18.10-x86_64-1_slack.txz                           1124 K
      salix       aria2-1.18.1-x86_64-1rl.txz                                1052 K
      slackr      aria2-1.18.10-x86_64-1cf.txz                               1140 K
    
    Found summary
    ===============================================================================
    Total found 4 packages in 4 repositories.

   
    Search in repositories with case insensitives:

    $ slpkg -F pyqt5 AAA --case-ins

    Packages with name matching [ pyqt5, AAA ]

    +==============================================================================
    | Repository  Package                                                      Size
    +==============================================================================
      slack       aaa_base-14.1-x86_64-1.txz                                   12 K
      slack       aaa_elflibs-14.1-x86_64-3.txz                              4316 K
      slack       aaa_terminfo-5.8-x86_64-1.txz                                44 K
      sbo         jaaa-0.8.4                                                    0 K
      sbo         python3-PyQt5-5.5                                             0 K
      slonly      jaaa-0.8.4-x86_64-1_slack.txz                                40 K
      slonly      python3-PyQt5-5.5-x86_64-1_slack.txz                       3088 K

    Found summary
    ===============================================================================
    Total found 7 packages in 3 repositories.


Find installed packages:

.. code-block:: bash

    $ slpkg -f apr

    Packages with matching name [ apr ] 
    
    [ installed ] - apr-1.5.0-x86_64-1_slack14.1
    [ installed ] - apr-util-1.5.3-x86_64-1_slack14.1
    [ installed ] - xf86dgaproto-2.1-noarch-1
    [ installed ] - xineramaproto-1.2.1-noarch-1

    Found summary
    ===============================================================================
    Total found 4 matcing packages
    Size of installed packages 1.61 Mb

    
Display the contents of the packages:

.. code-block:: bash

    $ slpkg -d termcolor lua

    PACKAGE NAME:     termcolor-1.1.0-x86_64-1_SBo
    COMPRESSED PACKAGE SIZE:     8.0K
    UNCOMPRESSED PACKAGE SIZE:     60K
    PACKAGE LOCATION: ./termcolor-1.1.0-x86_64-1_SBo.tgz
    PACKAGE DESCRIPTION:
    termcolor: termcolor (ANSII Color formatting for output in terminal)
    termcolor:
    termcolor: termcolor allows you to format your output in terminal.
    termcolor:
    termcolor:
    termcolor: Project URL: https://pypi.python.org/pypi/termcolor
    termcolor:
    termcolor:
    termcolor:
    termcolor:
    FILE LIST:
    ./
    usr/
    usr/lib64/
    usr/lib64/python2.7/
    usr/lib64/python2.7/site-packages/
    usr/lib64/python2.7/site-packages/termcolor.py
    usr/lib64/python2.7/site-packages/termcolor.pyc
    usr/lib64/python2.7/site-packages/termcolor-1.1.0-py2.7.egg-info
    usr/lib64/python3.3/
    usr/lib64/python3.3/site-packages/
    usr/lib64/python3.3/site-packages/termcolor-1.1.0-py3.3.egg-info
    usr/lib64/python3.3/site-packages/__pycache__/
    usr/lib64/python3.3/site-packages/__pycache__/termcolor.cpython-33.pyc
    usr/lib64/python3.3/site-packages/termcolor.py
    usr/doc/
    usr/doc/termcolor-1.1.0/
    usr/doc/termcolor-1.1.0/termcolor.SlackBuild
    usr/doc/termcolor-1.1.0/README.rst
    usr/doc/termcolor-1.1.0/CHANGES.rst
    usr/doc/termcolor-1.1.0/PKG-INFO
    usr/doc/termcolor-1.1.0/COPYING.txt
    install/
    install/slack-desc
    
    No such package lua: Cant find


Removes a previously installed Slackware binary packages:

.. code-block:: bash

    $ slpkg -r termcolor
    
    Packages with name matching [ termcolor ]
    
    [ delete ] --> termcolor-1.1.0-x86_64-1_SBo

    Removed summary
    ===============================================================================
    Size of removed packages 50.0 Kb.

    Are you sure to remove 1 package(s) [y/N]? y

    Package: termcolor-1.1.0-x86_64-1_SBo
        Removing... 

    Removing package /var/log/packages/termcolor-1.1.0-x86_64-1_SBo...
        Removing files:
    --> Deleting /usr/doc/termcolor-1.1.0/CHANGES.rst
    --> Deleting /usr/doc/termcolor-1.1.0/COPYING.txt
    --> Deleting /usr/doc/termcolor-1.1.0/PKG-INFO
    --> Deleting /usr/doc/termcolor-1.1.0/README.rst
    --> Deleting /usr/doc/termcolor-1.1.0/termcolor.SlackBuild
    --> Deleting /usr/lib64/python2.7/site-packages/termcolor-1.1.0-py2.7.egg-info
    --> Deleting /usr/lib64/python2.7/site-packages/termcolor.py
    --> Deleting /usr/lib64/python2.7/site-packages/termcolor.pyc
    --> Deleting /usr/lib64/python3.3/site-packages/__pycache__/termcolor.cpython-33.pyc
    --> Deleting /usr/lib64/python3.3/site-packages/termcolor-1.1.0-py3.3.egg-info
    --> Deleting /usr/lib64/python3.3/site-packages/termcolor.py
    --> Deleting empty directory /usr/lib64/python3.3/site-packages/__pycache__/
    WARNING: Unique directory /usr/lib64/python3.3/site-packages/ contains new files
    WARNING: Unique directory /usr/lib64/python3.3/ contains new files
    --> Deleting empty directory /usr/doc/termcolor-1.1.0/

    +==============================================================================
    | Package: termcolor-1.1.0 removed
    +==============================================================================


Remove packages with all dependencies and check if used as dependency:
(Presupposes install with the option '# slpkg -s <repository> <packages>')

.. code-block:: bash

    $ slpkg -r Flask --deps --check-deps 

    Packages with name matching [ Flask ]

    [ delete ] --> Flask-0.10.1-x86_64-1_SBo

    Removed summary
    ===============================================================================
    Size of removed packages 1.2 Mb.

    Are you sure to remove 1 package [y/N]? y

    +==============================================================================
    | Found dependencies for package Flask:
    +==============================================================================
    | pysetuptools-18.0.1
    | MarkupSafe-0.23
    | werkzeug-0.9.4
    | Jinja2-2.7.3
    | itsdangerous-0.24
    +==============================================================================
    | Size of removed dependencies 5.52 Mb
    +==============================================================================

    Remove dependencies (maybe used by other packages) [y/N]? y
    
    
    +==============================================================================
    |                              !!! WARNING !!!  
    +==============================================================================
    | pysetuptools is dependency of the package --> Flask
    | MarkupSafe is dependency of the package --> Flask
    | werkzeug is dependency of the package --> Flask
    | Jinja2 is dependency of the package --> Flask
    | itsdangerous is dependency of the package --> Flask
    | pysetuptools is dependency of the package --> flake8
    | pysetuptools is dependency of the package --> pip
    | pysetuptools is dependency of the package --> pipstat
    | pysetuptools is dependency of the package --> pylint
    | pysetuptools is dependency of the package --> wcwidth
    +==============================================================================
    +==============================================================================
    | Insert packages to exception remove:
    +==============================================================================
     > pysetuptools

    .
    .
    .
    +==============================================================================
    | Total 5 packages removed
    +==============================================================================
    | Package Flask-0.10.1 removed
    | Package MarkupSafe-0.23 removed
    | Package itsdangerous-0.24 removed
    | Package Jinja2-2.7.3 removed
    | Package werkzeug-0.9.4 removed
    +==============================================================================

Remove packages with by TAG:

.. code-block:: bash
    
    $ slpkg -r _SBo --tag
    
    Packages with name matching [ _SBo ]

    [ delete ] --> Jinja2-2.7.3-x86_64-1_SBo
    [ delete ] --> MarkupSafe-0.23-x86_64-1_SBo
    [ delete ] --> Pafy-0.3.72-x86_64-1_SBo
    [ delete ] --> Pulse-Glass-1.02-x86_64-1_SBo
    [ delete ] --> Pygments-1.6-x86_64-2_SBo
    [ delete ] --> asciinema-1.1.1-x86_64-1_SBo
    [ delete ] --> astroid-1.3.8-x86_64-1_SBo
    [ delete ] --> autopep8-1.2-x86_64-1_SBo
    [ delete ] --> blessings-1.6-x86_64-1_SBo
    [ delete ] --> bpython-0.14.2-x86_64-1_SBo
    [ delete ] --> cffi-1.1.2-x86_64-1_SBo
    [ delete ] --> cryptography-0.8.2-x86_64-1_SBo
    [ delete ] --> curtsies-0.1.19-x86_64-1_SBo
    [ delete ] --> enum34-1.0.4-x86_64-1_SBo

    Removed summary
    ===============================================================================
    Size of removed packages 24.61 Mb.

    Are you sure to remove 14 packages [y/N]? 

Remove packages using dialog utility:

.. code-block:: bash

    $ slpkg -r _SBo --tag --checklist

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/pythondialog.png
    :target: https://github.com/dslackw/slpkg

.. code-block:: bash

    $ slpkg -r Flask --check-deps --checklist

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/pythondialog2.png
    :target: https://github.com/dslackw/slpkg

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/pythondialog3.png
    :target: https://github.com/dslackw/slpkg

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/pythondialog4.png
    :target: https://github.com/dslackw/slpkg


Build and install packages that have added to the queue:

.. code-block:: bash

    $ slpkg -q roxterm SDL2 CEGUI --add
    
    Add packages in queue:

    roxterm
    SDL2
    CEGUI

    
    $ slpkg -q roxterm --remove (or 'slpkg -q ALL --remove' remove all packages)
    
    Remove packages from queue:

    roxterm

    
    $ slpkg -q list

    Packages in queue:

    SDL2
    CEGUI
    
    
    $ slpkg -q build (build only packages from queue)

    $ slpkg -q install (install packages from queue)

    $ slpkg -q build-install (build and install)


Add or remove packages in blacklist file manually from 
/etc/slpkg/blacklist or with the following options:

.. code-block:: bash
    
    $ slpkg -b live555 speex faac --add

    Add packages in blacklist: 

    live555
    speex
    faac


    $ slpkg -b speex --remove (or 'slpkg -b ALL --remove' remove all packages)

    Remove packages from blacklist:

    speex


    $ slpkg -b list

    Packages in blacklist:

    live555
    faac

    Note: you can use asterisk "*" to match more packages like:

    *lib*   \\ Add all packages inlcude string "lib"
    *lib    \\ Add all packages ends with string "lib"
    lib*    \\ Add all packages starts with string "lib"

    multi:*multilib*   \\ Add all packages include string "multilib" from "multi"
                       \\ repository.
    
Print package description:

.. code-block:: bash

    $ slpkg -p alien vlc --color=green

    vlc (multimedia player for various audio and video formats)

    VLC media player is a highly portable multimedia player for various
    audio and video formats (MPEG-1, MPEG-2, MPEG-4, DivX, mp3, ogg, ...)
    as well as DVDs, VCDs, and various streaming protocols.
    It can also be used as a server to stream in unicast or multicast in
    IPv4 or IPv6 on a high-bandwidth network.


    vlc home: http://www.videolan.org/vlc/


Man page it is available for full support:

.. code-block:: bash

    $ man slpkg


Donate
------
If you feel satisfied with this project and want to thank me go
to `Slackware <https://store.slackware.com/cgi-bin/store/slackdonation>`_ and make a donation or 
visit the `store <https://store.slackware.com/cgi-bin/store>`_.


Copyright 
---------

- Copyright 2014-2016 © Dimitris Zlatanidis
- Slackware® is a Registered Trademark of Patrick Volkerding.
- Linux is a Registered Trademark of Linus Torvalds.
