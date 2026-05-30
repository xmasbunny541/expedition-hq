# Visual System

## Visual classes

| Visual class | Render as |
|---|---|
| specialist | little AI character |
| candidate_specialist | little AI character with experimental/dormant status |
| automation | construct, tower, rover, or clockwork helper |
| route_bridge | bridge, gate, portal, checkpoint |
| interface | console, handset, map room |
| station | workstation, server rack, base camp |
| archive | vault, shelf, records room |
| data_source | crate, library cabinet, external supply cache |

## Core rule

Movement and animation must come from real state:
- current assignment
- last event
- incident/blocker
- review-needed status
- maturity state

## Homepage hubworld direction

The homepage should feel like a friendly living hubworld, not a technical dashboard.

Preferred visual direction:
- Use cute helper characters instead of abstract tokens when possible: elf-like, bean-like, costumed, expressive, and easy to recognize.
- Give the ecosystem most of the screen. Panels should be compact, collapsible, or nested behind hover/tap details.
- Name the central shared area plainly, such as `Work Board`, `Town Square`, `Dispatch Board`, or `Mission Board`. It should clearly mean "work arrives here, gets sorted, and moves to helpers."
- Make rooms feel occupiable by multiple helpers at once. The user should be able to tell who is in each room and what they are doing.
- Prefer plain activity labels like `Doing now`, `waiting for you`, `resting`, `building`, `saving`, `checking`, and `carrying note`. Avoid `awake` as a primary label.
- Use `Work archives`, not `Saved stuff`, for the history/records area.
- Keep `Work archives` accessible but compact on the homepage; deeper records can live inside the archive area.
- Keep `Needs a look` visually prominent. It means an agent needs user input, review, or a decision. Its portrait/icon should match the same helper visible in the hubworld.
- Preserve a compact `Recent handoffs` chain. It is a good way to show real-time agent-to-agent work passing.
- Use graphical bridges, tubes, rails, shuttles, or delivery lanes to show work moving. Do not label this system generically as `paths`; show what is moving: notes, questions, reports, ideas, or finished work.

Guide and learning behavior:
- The hubworld should teach the basics through hover/tap tooltips, small nested explanations, and repeated symbols.
- A guide or manual tab is useful only if every symbol it explains also appears in the hubworld.
- Explanations should use short everyday wording. The user should learn by looking around, not by reading a manual first.

Avoid:
- Technical jargon on the homepage: API, MCP, endpoint, schema, token, route-edge, risk level, privacy class.
- Grim-dark, black-heavy, or corporate analytics styling.
- Large legends, giant sidebars, or bottom strips that shrink the ecosystem without explaining useful activity.
- Showing `All local` as a normal badge. If locality/exposure changes, treat it as an important warning with consequences and suggested next steps.
- Fake control actions such as start/stop/deploy/rotate. Expedition HQ remains an observatory unless a future control surface is explicitly designed and gated.
