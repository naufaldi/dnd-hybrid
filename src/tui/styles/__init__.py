/* Main CSS styles for D&D Roguelike */

Screen {
    background: $surface;
}

#menu_container {
    width: 100%;
    height: 100%;
    content-align: center middle;
}

#menu_items {
    width: 40;
    height: auto;
}

#title {
    text-align: center;
    text-style: bold;
    color: $accent;
    width: 100%;
}

#subtitle {
    text-align: center;
    color: $text-muted;
    width: 100%;
}

/* Game Screen Layout */
#game_layout {
    width: 100%;
    height: 100%;
}

#map_container {
    width: 80%;
    height: 100%;
    border: solid $border;
}

#sidebar {
    width: 20%;
    height: 100%;
    border: solid $border;
    padding: 1;
}

/* Status Widget */
#status {
    height: auto;
    padding: 1;
    border-bottom: solid $border;
}

/* Combat Widget */
#combat {
    height: 100%;
    padding: 1;
}

/* Character Screen */
#char_container {
    width: 100%;
    height: 100%;
}

#char_content {
    width: 60;
    height: auto;
    padding: 2;
}

#char_title {
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
}

#char_details {
    width: 100%;
}

/* Inventory Screen */
#inv_container {
    width: 100%;
    height: 100%;
}

#inv_list {
    height: 60%;
}

#inv_details {
    height: 40%;
    padding: 1;
}

/* Log Screen */
#log_container {
    width: 100%;
    height: 100%;
}

#log_content {
    width: 100%;
    height: 100%;
    padding: 1;
}

/* Character Creation */
#cc_container {
    width: 100%;
    height: 100%;
    content-align: center middle;
}

#cc_content {
    width: 50;
    height: auto;
    padding: 2;
}

#cc_title {
    text-style: bold;
    color: $accent;
    text-align: center;
    margin-bottom: 2;
}

#cc_prompt {
    margin-bottom: 1;
}

#cc_value {
    text-style: bold;
    margin-bottom: 1;
}

#cc_options {
    margin-bottom: 1;
}

#cc_help {
    color: $text-muted;
    text-align: center;
}
