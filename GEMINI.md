 - no introductions, no sugar couting, get straight to the point, don't waste tokens on politeness

Documentation lives under markdown/:
 - markdown/PROJECT.md - project structure, coding conventions, dependencies
 - markdown/BACKEND.md - architecture, layers, classes, data flow
 - markdown/TODO.md - todos. If something is done remove it from it

This project can also have (if necessary):
 - markdown/BUGS.md - list of bugs
 - markdown/FIXPLAN.md - if there is a plan to implement something from TODO.md

Order of work:
 - Do not run tests until changes were performed
 - Start with updating .md files if they should be updated (PROJECT, URLS, etc)
 - write unit tests if a case is missing
 - proceed with updating code
 - after implementation double check if there are similar places in code that should be refactored into a function, or if values were hardcoded in two or more places, but should be in one only

If you find additional errors not connected to prompt, context - you don't have to fix them immediately, but can put these into BUGS.md
