# Programming ACK of art delivery

This is a receiver-produced ACK by the real programming context
`/root/studio_programming`, addressed to `/root/studio_art`, replying to DELIVER
`e3b6a17b-45cb-45a2-a499-37e1bc5111df`. The project is
`key-door-studio-demo`, shared world revision 1. The shared contract and world
are unchanged.

I read the art delivery note and packet, manifest, production evidence and actual
SVG assets, along with the current contract and world. The handoff helper
returned `CURRENT` for the delivery's exact pinned bytes. I did not alter the
art source, parameters, assets, preview, or evidence.

`programming/build.py` consumes `art/generated/manifest.json`, reads each
referenced SVG, checks the contracted IDs and 32px dimensions/viewBox, and embeds
its exact bytes as an image data URI in `index.html`. All five IDs are used in
the emitted board. Floors precede walls and entities; key and exit overlays
precede player. Input/output hashes are recorded in
`programming/generated/build-evidence.json`.

The witness executing the HTML's shipped JS confirmed exact SVG-byte presence
in the emitted image sources and actual markup use of all IDs. It observed the
key image's hidden property become true on collection and false after restart;
it observed the player position update to the exit while the player element
remains layered last. Visible text assignments communicate key possession,
locked-door feedback, door readiness and victory. These claims come from
`programming/generated/runtime-evidence.json`, whose seven grouped checks passed.

Technical integration acceptance covers the embedded bytes, image markup order
and runtime DOM assignments. It does not establish successful image decoding,
actual CSS layout or perceptual clarity in a browser. Art's separate rendered
preview observation remains art's evidence. No actual game-browser inspection or
human playtest was possible on this host, and no browser was downloaded.

There is no missing art asset or integration-format decision. The next useful
visual check is to open the delivered HTML in an available desktop browser and
inspect initial, key-collected and won states. This ACK makes no broader product
or independent visual-acceptance claim.
