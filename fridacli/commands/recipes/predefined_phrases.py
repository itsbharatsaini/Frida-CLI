from fridacli.interface.styles import add_styletags_to_string

ANGULAR_PROJECT_DETECTED = f"{add_styletags_to_string('- Angular project detected', style='success')} voyager started..."
ANGULAR_PROJECT_NOT_DETECTED = f"{add_styletags_to_string('- Angular project not detected', style='warning')}"
ANGULAR_PROJECT_NOT_DETECTED = (
    lambda path: f"{add_styletags_to_string('- Angular project not detected in',style='warning')} {add_styletags_to_string(path,style='path')}"
)
ANGULAR_PROJECT_GRAPH_CONSTRUCTED = f"{add_styletags_to_string('- Angular project graph constructed', style='success')} voyager keep going..."