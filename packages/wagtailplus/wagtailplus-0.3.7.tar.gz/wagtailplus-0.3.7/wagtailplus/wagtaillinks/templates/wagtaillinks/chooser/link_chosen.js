function(modal) {
    modal.respond('linkChosen', {{ link_json|safe }});
    modal.close();
}