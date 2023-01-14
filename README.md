# Role Association Crossover - Readme

## Overview

Per [TvTropes](https://tvtropes.org/pmwiki/pmwiki.php/JustForFun/RoleAssociation), a Role Association is an entry in a game where you "Insert an actor's other roles into the plot of another work". Role Association Crossover takes that game a step further by treating an actor as if they truly were the sum of all their roles.

A graph model of actors and the characters they've played, displayed as wiki-style pages, as a mashup of all the connected nodes.

The graph is designed with nodes `[actor1] - [character1] - [actor2] - [character2]`. Users can choose a starting node and a distance from that node, and RAC will render the selected nodes into a single page with sections such as "powers" or "relationships". These sections display all properties of a node with the same name, as if the group of nodes represented a single character.

## Development Environment

RAC was developed in Visual Studo Code, and was written in python using the 'flask' module to render HTML, and the 'cinemagoer'(formerly imdbpy) module to import the data from IMDB. I intend to use neomodel in the future for the graph visualizer page. The database is built in neo4j.

## Future Work

- Cleaner code
-- TODO: the base needs to be more modular. public methods should be calling db-specific private methods
-- (a note) Law of Demeter: each class should only 'know' it's own methods or variables, and the top-level methods of any other classes it has been given
-- Have "getters" vs public variables
-- TODO variable types with (name: type)
-- TODO more intuitive variable names, a sweep to make it pythonic
-- TODO: update per: [cinemagoer's docs](https://cinemagoer.readthedocs.io/en/latest/)
-- TODO: does adultSearch=0 still work?

- Website and forms
-- Merging and separating roles would be easier with a drag-and-drop interface
-- TODO: navigation back to the previous page should be easier after using a form
--- I shouldn't need "go_back_url"
--- some pages need to stay put when something is submitted
--- Links/buttons can go onclick="history.back()"
-- The tooltips for "character_connector" need to be renamed
-- The textboxes of forms should be resizable.
-- The 'ability template' editor should have the ability to add sub-templates
-- A way to add user-made roles to replace the ... or 'additional voices' for actors w/ multiple roles, such as in 'Skyrim'

- The front page
-- featured articles based off of hits or connections (after the webview/ hub sigils works)

- The wiki page
-- A little box for a gallary and captions, in the actor bio, in role sections.

- Page generation
-- If we can get 'all nodes of distance "n" from a given node', the page generator can be directly integrated into the Flask template.

- Web View
-- TODO (may be working now) neomodel needs Shapely, which doesn't work for python 3.10

- "Hub Sigils"
-- Representations of the largest nodes that a node is connected to, with their distance.
-- These will be a way to identify a node by which cluster it belongs to.

- Database
-- Is it possible to use neo4j to return all nodes at distance 'n' from a parent node?
-- Test that the objects returned by the database are not nested in an extra tuple
-- Abilities need to be nodes
-- The 'ability templates' should have the ability to connect to sub-templates
-- Error handling when attempting to get an actor who is not already in the database
-- A way to revert a merged mr, rather than resetting the mr of each role
-- A way to add user-made roles to replace the ... or 'additional voices' for actors w/ multiple roles, such as in 'Skyrim'
-- A strategy for merging duplicate actors/actresses who have changed their name [such as "Comona Lewin"]
-- The property 'fictional_in_universe' needs to get moved from mr's to roles, to resolve eg: Buzz Lightyear the toy having same MR as fictional Buzz the movie character
-- Allow the search function to look in descriptions or bios?

- Changelog (of actors/ roles)
-- TODO we need a better way to store the changelog for actors/mrs/abilities

- Importing IMDB
-- The get_movie, get_person and get_company methods take an optional info parameter, which can be used to specify the kinds of data to fetch. Use this to only fetch what we need.
-- (already done, design note) generating MR id equal to the role id
-- cinemagoer can fetch from a static download of the IMDB datasets, rather than from the site itself. This would use the same calls aside from uri, and save bandwith. See if this fetches the info we need.
