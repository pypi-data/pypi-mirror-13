def display_quote(context):
    doc = context.app.get_record('doc1')
    if doc:
        return doc.get('quote', '')
    else:
        return "No quote"


def create(context):
    doc = context.app.create_record('doc1')
    doc["quote"] = "Knowledge is power, France is bacon."
    doc.save()


def boom(context):
    context.wrong()
