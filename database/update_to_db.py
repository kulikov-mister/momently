async def update_sent_item(sent_item, **kwargs):
    for key, value in kwargs.items():
        setattr(sent_item, key, value)
    sent_item.save()