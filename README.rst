===============
ROCrate 2 rohub
===============

Library and script to convert any RO-crate to a valid rohub RO-crate.

Checks for the existence of "title", "description" and "Research area" and can
add these to an existing crate.

Internally, a research area is stored as a link to a eurovoc term, in the field
"studySubject".
