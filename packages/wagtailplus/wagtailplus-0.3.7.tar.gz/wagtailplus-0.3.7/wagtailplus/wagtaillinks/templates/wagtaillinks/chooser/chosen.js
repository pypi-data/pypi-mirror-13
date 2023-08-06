function(modal) {
    modal.respond('linkChosen', {{ obj|safe }});
    modal.close();
}