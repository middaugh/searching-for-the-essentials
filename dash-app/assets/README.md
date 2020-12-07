# CSS Naming Guide

The CSS for this project follows two CSS naming conventions, 
that of ITCSS and BEM. Utilizing these two guides, the

There are two main "levels": 

 - dashboard-block
 - viz-card
 
 A _dashboard-block_ is a top level block and is applied
 by index.py solely. 
 
 Imagine index.py as the board game of operation. 
 Each of the different dashboard blocks are like one of the orgons
 and have a specific place within the dashboard. They can take up an entire tab, 
 or be combined to form a single page within the dashboard.
 
 Similarly, each dashboard-block is made up of viz-cards. A viz-card
 is made up of discrete elements which do not have children (or at least, children which we style)
 
 
 .viz-card
 .viz
 
The name of the dashboard-block will match the modifier applied to a .viz-card

Every single viz-card has the .viz-card class applied to it, as well as
the module-specific modifier.


## Example
Within apps/ you have a python module named indicators.py. 
Within index.py, 
indicators.layout would be brought in. It's top level div would be styled as

.dashboard-block
.dashboard-block--indicators

All of its components would be 

.viz-card
.viz-card--indicators

With portions within it being

.viz-card

.viz-card__graph

.viz-card__graph--indicators
.viz-card__header 
.viz-card__header--indicators 


## FIX ME FIX ME 
If the indicator.py module is made up of multiple cards,
this is extended to 

.viz-card__card__graph
.viz-card__card_header--record_types


 
 
 
 ## How BEM is Applied
 
 ## ITCSS: How the code is structured 
 
 

 
 ??? What if we moved this all down one level. 
 
 
 At the very top top level, all the legos that we slot in are olny being positioned.d No skin is applied at the very very top level. 
 The application of skin tcan happen only at the top level within the module.py
 
 
  ## Resources
 https://csswizardry.com/2013/01/mindbemding-getting-your-head-round-bem-syntax/
 https://www.xfive.co/blog/itcss-scalable-maintainable-css-architecture/
 https://css-tricks.com/bem-101/
 http://www.stubbornella.org/content/2010/06/25/the-media-object-saves-hundreds-of-lines-of-code
 http://nicolasgallagher.com/about-html-semantics-front-end-architecture/
 https://www.youtube.com/watch?v=1OKZOV-iLj4
 https://www.creativebloq.com/web-design/manage-large-css-projects-itcss-101517528
 https://css-tricks.com/developing-extensible-html-css-components/