Introduction
============

Products.Maps provides facilities for attaching geolocation information to content types. Content objects using its location field can then be automatically represented in map views of collections and folders that aggregate the geolocated content objects.

This package adds a Dexterity behavior to add geolocation fields to content types and to add the adapters and views necessary to used them with Products.Maps views.

Install this package as you would any Plone package. Dependencies include plone.app.dexterity, plone.formwidget.geolocation and Products.Maps.

Most of the implementation is straightforward. The only part that's hacky is removing the jsregistry conditions for shipping the Products.Maps editing facility. This was because I couldn't figure out how to provide a BrowserView for an add form by virtue of the content type having a behavior. Drop me a note if you know how to do it.
