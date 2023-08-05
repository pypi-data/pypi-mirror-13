Buildout Garbage Collector
==========================

Introduction
------------
The buildout.gc extensions can be used to ensure your egg directory only contains 'used' eggs.
The extension can report, move unused eggs to a specified directory or just remove egss.

This package is fork of https://github.com/thepjot/buildout.eggscleaner


Installation
------------
Garbase Collector is a buildout extensions, can add it like so ::

    [buildout]
    extensions =
            buildout.gc


Options
-------

old-eggs-directory
        The directory you want buildout.gc to move your unused eggs to.
        Should an excact egg already exist, we remove the one in the ''used'' eggs directory

remove-eggs
        Remove eggs


Example ::

        [buildout]
        extensions =
                buildout.gc
        old-eggs-directory = ${buildout:directory}/old-eggs/

Tested with
-----------

zc.buildout: 2.xx
python: 2.4.6, 2.6.8, 3.3

Working with other extensions
-----------------------------

I looked at how buildout.dumppickedversions works and made this extension work in a similar manner.
This extension will run alongside that one perfectly well.


Example outputs
---------------

Moving eggs ::

    *************** BUILDOUT GC ****************
    Moved unused egg: webcouturier.dropdownmenu-2.3-py2.6.egg
    Moved unused egg: collective.uploadify-1.0-py2.6.egg
    Moved unused egg: collective.simplesocial-1.6-py2.6.egg
    Moved unused egg: collective.autopermission-1.0b2-py2.6.egg
    *************** /BUILDOUT GC ****************

Reporting ::

    *************** BUILDOUT GC ****************
    Don't have a 'old-eggs-directory' set, only reporting
    Can add it by adding 'old-eggs-directory = ${buildout:directory}/old-eggs' to your [buildout]
    Found unused egg: webcouturier.dropdownmenu-2.3-py2.6.egg
    Found unused egg: plone.recipe.command-1.1-py2.6.egg
    Found unused egg: collective.uploadify-1.0-py2.6.egg
    Found unused egg: Products.DocFinderTab-1.0.5-py2.6.egg
    Found unused egg: collective.simplesocial-1.6-py2.6.egg
    Found unused egg: collective.autopermission-1.0b2-py2.6.egg
    Found unused egg: Products.Clouseau-1.0-py2.6.egg
    *************** /BUILDOUT GC ****************

